from ftplib import FTP


def przeslij_plik(sciezka_pliku, cel):
    """
    Funkcja do przesyłania pliku na serwer FTP.

    Args:
    - sciezka_pliku: Ścieżka do pliku, który ma być przesłany.
    - cel: Ścieżka na serwerze, gdzie plik ma być zapisany.
    """
    with open(r'D:\PY_SCRIPT\Kolejkowanie_HELLER\v0_1\ftp_dane.txt', 'r') as file:
        address, user, password = [line.strip() for line in file]

    port = 5000
    with FTP() as ftp:
        try:
            ftp.connect(host=address, port=port)
            ftp.login(user, password)
            with open(sciezka_pliku, 'rb') as plik:
                ftp.storbinary(f'STOR {cel}', plik)
            print(f'Plik {sciezka_pliku} został przesłany.')
            ftp.retrlines('LIST')
        except Exception as e:
            print(f'Błąd podczas przesyłania pliku: {e}')


# Ścieżka do pliku, który chcesz przesłać
sciezka_pliku = r'D:\PY_SCRIPT\Kolejkowanie_HELLER\v0_1\plik_lokalny.txt'
# Nazwa, pod którą plik ma być zapisany na serwerze
cel = 'nazwa_pliku_na_serwerze.txt'

przeslij_plik(sciezka_pliku, cel)
