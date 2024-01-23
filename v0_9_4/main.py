import sys
from PyQt5.QtWidgets import QApplication
from ui import MainApp  # Import klasy MainApp z pliku ui.py

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Tworzenie instancji QApplication
    main_app = MainApp()  # Tworzenie instancji klasy MainApp
    main_app.show()  # Wyświetlenie okna głównego
    # Rozpoczęcie pętli zdarzeń i wyjście z aplikacji po jej zamknięciu
    sys.exit(app.exec_())
