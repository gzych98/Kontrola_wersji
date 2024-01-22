import os
import shutil
from PyQt5.QtWidgets import QTextEdit ,QListWidgetItem  ,QApplication, QMainWindow, QPushButton, QLabel, QListWidget, QVBoxLayout, QHBoxLayout, QWidget, QDesktopWidget, QLineEdit, QDialog, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QDragEnterEvent, QDropEvent
from qfunctions import app_process, process_active, aktywuj_simpack_pre_i_otworz_plik, simpack_pre_active
from PyQt5.QtCore import Qt, QTimer
import pygetwindow as gw
import datetime
from ftplib import FTP

class DragDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDrop)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = [url.toLocalFile() for url in event.mimeData().urls()]
            for link in links:
                self.addItem(link)
        else:
            event.ignore()

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("O aplikacji")
        self.setGeometry(300, 300, 600, 200)  # Rozmiar i pozycja okna

        layout = QVBoxLayout(self)

        about_text = QLabel("Kontrola Wersji v0.9.2 (wersja testowa)\n\n"
                            "Opis elementów aplikacji:\n"
                            "- Listbox: Pozwala na przeciąganie i upuszczanie plików do analizy.\n"
                            "- Przycisk 'Integration': Uruchamia proces integracji.\n"
                            "- Przycisk 'Measurement': Uruchamia proces pomiaru.\n"
                            "- Przycisk 'Standalone': Uruchamia proces standalone.\n"
                            "- Przycisk 'Standalone zip': Uruchamia proces standalone i tworzy archiwum ZIP.\n"
                            "- Pole tekstowe: Umożliwia wprowadzenie ścieżki do solvera.\n"
                            "- Przycisk 'Minimalizuj': Minimalizuje aplikację do paska zadań.\n"
                            "- Przycisk 'Zakończ': Zamyka aplikację.\n"
                            "- Przycisk 'Wyczyść': Czyści listę plików.\n"
                            "- Ikona w zasobniku systemowym: Umożliwia szybki dostęp do aplikacji.\n"
                            "- Etykieta stanu: Wyświetla aktualny stan procesu.\n"
                            "\nAutor: Grzegorz Zych 2024\n")
        about_text.setWordWrap(True)

        layout.addWidget(about_text)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setup_tray_icon()
        self.setup_monitoring()


    def initUI(self):
        self.setWindowTitle("Kontrola wersji - v0.9.2")
        self.setGeometry(0, 0, 500, 300)  # tymczasowa geometria
        self.setWindowPosition()  

        self.setWindowIcon(QIcon(r"Kontrola_wersji_v_0_6\wrench-solid.ico"))
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Tworzenie widgetów
       #self.listWidget = DragDropListWidget(self)
        self.listbox = DragDropListWidget(self)

        # self.add_button = QPushButton("Dodaj pliki", self)
        # self.add_button.clicked.connect(lambda: dodaj_pliki(self.listbox))

        self.drag_drop_label = QLabel("Przeciągnij i upuść pliki tutaj", self)
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        self.drag_drop_label.setStyleSheet("color: gray; font-style: italic;")

        self.integration_button = QPushButton("Integration", self)
        self.integration_button.clicked.connect(lambda: self.run_app_process(["--integration", "--file"]))

        self.measurement_button = QPushButton("Measurement", self)
        self.measurement_button.clicked.connect(lambda: self.run_app_process(["--measurement", "--file"]))

        self.standalone_button = QPushButton("Standalone", self)
        self.standalone_button.clicked.connect(lambda: self.run_app_process(["--gen-standalone", "--input-model"]))

        self.standalone_button_zip = QPushButton("Standalone zip", self)
        self.standalone_button_zip.clicked.connect(lambda: self.run_app_process(["--gen-standalone", "--zip", "--input-model"]))

        self.copy_button =QPushButton("Kopiuj", self)
        self.copy_button.clicked.connect(lambda: self.copy_model())

        self.minimize_button = QPushButton("Minimalizuj", self)
        self.minimize_button.clicked.connect(self.hide_window)

        self.close_button = QPushButton("Zakończ", self)
        self.close_button.clicked.connect(self.close_app)

        self.delete_button = QPushButton("Wyczyść", self)
        self.delete_button.clicked.connect(self.clear_list)

        self.about_button = QPushButton("O aplikacji", self)
        self.about_button.clicked.connect(self.show_about_dialog)

        self.open_simpack_button = QPushButton("Otwórz w Simpack Pre", self)
        self.open_simpack_button.clicked.connect(self.otworz_w_simpack_pre)

        
        self.status_label = QLabel("Stan procesu: Nieaktywny", self)
        self.status_gui_label = QLabel("Simpack Pre GUI: Zamknięte", self)

        
        self.solver_path_edit = QLineEdit(self)
        self.solver_path_edit.setPlaceholderText("Wprowadź ścieżkę do solvera")
        self.solver_path_edit.setText(r"C:\Program Files\Simpack-2023x.3\run\bin\win64\simpack-slv")

        self.pre_path_edit = QLineEdit(self)
        self.pre_path_edit.setPlaceholderText("Wprowadź ścieżkę do pre")
        self.pre_path_edit.setText(r"C:\Program Files\Simpack-2023x.3\run\bin\win64\simpack-gui")

        # POŁĄCZENIE Z SERWEREM

        self.connectButton = QPushButton('Połącz', self)
        self.connectButton.clicked.connect(self.connectToFtp)
        self.resultField = QTextEdit(self)      


        # Układanie widgetów
        buttons_layout = QHBoxLayout()
        buttons_layout_2 = QHBoxLayout()
        buttons_layout_end = QHBoxLayout()

        serwer_layout = QHBoxLayout()
        
        # buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.open_simpack_button)
        buttons_layout.addWidget(self.integration_button)
        buttons_layout.addWidget(self.measurement_button)

        buttons_layout_2.addWidget(self.standalone_button)
        buttons_layout_2.addWidget(self.standalone_button_zip)
        buttons_layout_2.addWidget(self.copy_button)

        buttons_layout_end.addWidget(self.about_button)
        buttons_layout_end.addWidget(self.minimize_button)
        buttons_layout_end.addWidget(self.close_button)

        serwer_layout.addWidget(self.connectButton)
        serwer_layout.addWidget(self.resultField)

        main_layout = QVBoxLayout()
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.solver_path_edit)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.pre_path_edit)
        main_layout.addWidget(self.status_gui_label)
        main_layout.addLayout(buttons_layout_2)
        main_layout.addWidget(self.drag_drop_label)
        main_layout.addWidget(self.listbox)        
        main_layout.addLayout(serwer_layout)      
        main_layout.addWidget(self.delete_button)
        main_layout.addLayout(buttons_layout_end)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def close_app(self):
        self.close()

    def connectToFtp(self):
        try:
            with open('ftp_dane.txt', 'r') as file:
                address, user, password = [line.strip() for line in file]

            with FTP(address) as ftp:
                ftp.login(user, password)
                ftp.retrlines('LIST', self.updateResult)
        except Exception as e:
            self.updateResult(str(e))

    def updateResult(self, line):
        self.resultField.append(line)

    def copy_model(self):
        selected_items = self.listbox.selectedItems()
        if not selected_items:
            self.info_label.setText("Wybierz plik")
            return

        for item in selected_items:
            full_path = item.text()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S__")  # Formatowanie znacznika czasu
            directory, filename = os.path.split(full_path)  # Oddzielenie nazwy pliku od ścieżki
            new_filename = f"{timestamp}_{filename}"  # Dodanie znacznika czasu do nazwy pliku
            new_full_path = os.path.join(directory, new_filename)  # Nowa ścieżka z uwzględnieniem znacznika czasu

            shutil.copy2(full_path, new_full_path)
            self.info_label.setText(f"Skopiowano: {new_filename}")

            # Dodanie nowej ścieżki do listbox
            self.listbox.addItem(QListWidgetItem(new_full_path))


    def otworz_w_simpack_pre(self):
        # Pobranie aktualnie wybranego pliku z listboxa
        selected_items = self.listbox.selectedItems()
        if selected_items:
            pre_path = self.pre_path_edit.text()
            process_args = []
            aktywuj_simpack_pre_i_otworz_plik(self.listbox, self.info_label, self, process_args, pre_path)
        else:
            self.info_label.setText("Proszę wybrać plik z listy.")

    def show_about_dialog(self):
        # Funkcja wywoływana po kliknięciu przycisku "About"
        about_dialog = AboutDialog(self)
        about_dialog.exec_()

    def run_app_process(self, process_args):
        # Pobranie ścieżki do solvera z pola tekstowego
        solver_path = self.solver_path_edit.text()
        # Wywołanie funkcji app_process z odpowiednimi argumentami
        app_process(self.listbox, self.info_label, self, process_args, solver_path)

    def setup_monitoring(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.timeout.connect(self.check_simpack_window)
        self.timer.start(1000)  # Sprawdzanie co sekundę

    def update_status(self):
        if process_active.is_set():
            self.status_label.setText("Stan procesu: Aktywny")
            self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setText("Stan procesu: Nieaktywny")
            self.status_label.setStyleSheet("color: green;")
        if simpack_pre_active.is_set():
            self.status_gui_label.setText("Simpack Pre GUI: Aktywny")
            self.status_gui_label.setStyleSheet("color: green;")
        else:
            self.status_gui_label.setText("Simpack Pre GUI: Nieaktywny")
            self.status_gui_label.setStyleSheet("color: red;")

    def check_simpack_window(self):
        global simpack_pre_active
        okna = [okno for okno in gw.getAllWindows() if "Simpack 2023x.3 - " in okno.title]
        if okna:
            simpack_pre_active.set()  # Ustawienie flagi, jeśli okno jest otwarte
        else:
            simpack_pre_active.clear()  

    def check_queue(self):
        while not self.output_queue.empty():
            message = self.output_queue.get()
            # Aktualizuj UI na podstawie wiadomości
            self.statusBar().showMessage(message)

    def focusInEvent(self, event):
        self.setWindowOpacity(1.0)  # Normalna przezroczystość
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setWindowOpacity(0.2)  # Zmniejszona przezroczystość
        super().focusOutEvent(event)

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(r"Kontrola_wersji_v_0_6\favicon.ico"))

        show_action = QAction("Pokaż", self)
        show_action.triggered.connect(self.show_window)
        exit_action = QAction("Wyjdź", self)
        exit_action.triggered.connect(self.close)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show_window()

    def show_window(self):
        if self.isMinimized() or not self.isVisible():
            self.showNormal()
        self.activateWindow()

    
    def setWindowPosition(self):
        desktop = QDesktopWidget()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        position_right = screen_width - 520  # szerokość okna = 200
        position_down = screen_height - 400  # wysokość okna = 100
        self.setGeometry(position_right, position_down, 500, 300)

    def hide_window(self):
        self.hide()
        self.tray_icon.showMessage("Informacja", "Aplikacja została zminimalizowana do zasobnika systemowego.")
    
    def clear_list(self):
        # Funkcja czyszcząca listę
        self.listbox.clear()

if __name__ == "__main__":
    app = QApplication([])
    main_app = MainApp()
    main_app.show()
    app.exec_()