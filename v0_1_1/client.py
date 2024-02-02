# klient.py
import requests


def send_file(url, filepath):
    with open(filepath, 'rb') as f:
        files = {'file': (filepath, f)}
        r = requests.post(url, files=files)
        print(r.json())


if __name__ == "__main__":
    url = 'http://192.168.1.113:5000/upload'  # Zaktualizuj adres serwera
    # Ścieżka do pliku, który chcesz wysłać
    filepath = r'D:/PY_SCRIPT/Kolejkowanie_HELLER/v0_1_1/plik_lokalny.txt'
    send_file(url, filepath)
