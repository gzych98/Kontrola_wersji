# klient.py
from datetime import datetime
import os
import subprocess
import requests
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QPushButton, QLabel, QListWidget, QVBoxLayout, QHBoxLayout, QWidget, QDesktopWidget
from PyQt5.QtGui import QIcon, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt

LOCAL_SOLVER_PATH = r'C:\Program Files\Simpack-2023x.3\run\bin\win64\simpack-slv'


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


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Kontrola wersji - v0.9.2")
        self.setGeometry(0, 0, 400, 300)  # tymczasowa geometria

        screenSize = QDesktopWidget().screenGeometry()
        windowSize = self.geometry()

        # Obliczanie nowych współrzędnych x i y
        x = screenSize.width() - windowSize.width()
        y = screenSize.height() - windowSize.height()

        # Ustawianie nowej pozycji okna
        self.move(x, y-200)

        # Tworzenie widgetów
       # self.listWidget = DragDropListWidget(self)
        self.listbox = DragDropListWidget(self)

        # self.add_button = QPushButton("Dodaj pliki", self)
        # self.add_button.clicked.connect(lambda: dodaj_pliki(self.listbox))

        self.drag_drop_label = QLabel("Przeciągnij i upuść pliki tutaj", self)
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        self.drag_drop_label.setStyleSheet("color: gray; font-style: italic;")

        self.integration_button = QPushButton("Integration", self)
        self.integration_button.clicked.connect(
            lambda: self.integration())

        self.measurement_button = QPushButton("Measurement", self)
        self.measurement_button.clicked.connect(
            lambda: self.measurement())

        self.about_button = QPushButton("O aplikacji", self)
        self.about_button.clicked.connect(self.show_about_dialog)

        self.fetch_data_button = QPushButton("Pobierz dane", self)
        self.fetch_data_button.clicked.connect(self.fetch_data)

        self.data_label = QLabel("Tutaj pojawią się dane...", self)

        # Układanie widgetów
        buttons_layout = QHBoxLayout()
        buttons_layout_end = QHBoxLayout()

        serwer_layout = QHBoxLayout()

        # buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.integration_button)
        buttons_layout.addWidget(self.measurement_button)
        buttons_layout.addWidget(self.fetch_data_button)

        buttons_layout_end.addWidget(self.about_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.data_label)
        main_layout.addWidget(self.drag_drop_label)
        main_layout.addWidget(self.listbox)
        main_layout.addLayout(serwer_layout)
        main_layout.addLayout(buttons_layout_end)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def integration(self):
        start_time = datetime.now()
        selected_items = self.listbox.selectedItems()
        if not selected_items:
            print(f"ERROR:\tNie wybrano pliku")
            return
        for input_model in selected_items:
            input_path = input_model.text()
            print(f'SELECTED ITEM:\t{input_path}')
            self.standalone(input_path)
            zip_path = self.find_recent_zip_file(
                start_time, os.path.dirname(input_path))
            print(zip_path)
            if zip_path:
                self.send_file(zip_path, 'integration')

    def standalone(self, input_model):
        subprocess.run(
            f'{LOCAL_SOLVER_PATH} --gen-standalone --zip --input-model {input_model}')
        return (1)

    def send_file(self, filepath, flag='integration'):
        url = 'http://192.168.1.113:5000/upload'  # Zaktualizuj adres serwera
        with open(filepath, 'rb') as f:
            files = {'file': (filepath, f)}
            data = {'flag': flag}  # flaga jako dane formularza
            r = requests.post(url, files=files, data=data)
            print(r.json())

    def show_about_dialog(self):
        # Funkcja wywoływana po kliknięciu przycisku "About"
        about_dialog = AboutDialog(self)
        about_dialog.exec_()

    def find_recent_zip_file(self, start_time, directory):
        # Przekształć start_time do timestampa
        start_timestamp = start_time.timestamp()
        zip_files = [f for f in os.listdir(directory) if f.endswith('.zip')]
        recent_files = []
        for zip_file in zip_files:
            zip_path = os.path.join(directory, zip_file)
            # Pobierz timestamp modyfikacji pliku
            file_timestamp = os.path.getmtime(zip_path)
            if file_timestamp >= start_timestamp:
                recent_files.append((zip_path, file_timestamp))
        # Sortuj pliki po timestampie, od najnowszego
        recent_files.sort(key=lambda x: x[1], reverse=True)
        # Zwróć ścieżkę do najnowszego pliku, jeśli istnieje
        return recent_files[0][0] if recent_files else None

    def fetch_data(self):
        url = 'http://192.168.1.113:5000/get-data'  # Zmień na właściwy adres URL
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            display_text = ""
            for item in data:
                filename = file_name = item['file_path'].replace(
                    '\\', '/').split('/')[-1]
                display_text += f"ID: {item['id']}, Ścieżka pliku: {filename}, Etykieta: {item['file_label']}, Kolejność: {item['order']}\n"
            self.data_label.setText(display_text)
        else:
            self.data_label.setText("Błąd podczas pobierania danych.")


if __name__ == "__main__":

    app = QApplication([])
    main_app = MainApp()
    main_app.show()
    app.exec_()
