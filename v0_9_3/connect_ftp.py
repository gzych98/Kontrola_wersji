from ftplib import FTP

# Dane do połączenia
serwer = '127.0.0.1'  # np. '127.0.0.1' dla lokalnego serwera
uzytkownik = 'user'
haslo = '12345'
# Łączenie z serwerem
with FTP(serwer) as ftp:
    ftp.login(uzytkownik, haslo)

    # Wylistowanie plików i katalogów
    ftp.retrlines('LIST')

    # Tutaj możesz dodawać inne operacje, np. przesyłanie plików