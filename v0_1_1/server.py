# serwer.py
from flask import jsonify
import zipfile
import time
import subprocess
import datetime
from flask import Flask, request, jsonify
import os
from functions import allowed_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Konfiguracja SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///file_labels.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definicja modelu bazy danych


class FileLabel(db.Model):
    __tablename__ = 'file_label'
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String, unique=True, nullable=False)
    file_label = db.Column(db.String, nullable=False)
    order = db.Column(db.Integer)  # Nowa kolumna do przechowywania kolejności


# Inicjalizacja bazy danych
with app.app_context():
    db.create_all()


def label_items():
    # Pobieranie aktualnej listy plików z bazy danych
    current_files = FileLabel.query.order_by(FileLabel.order).all()
    # Tworzenie zbioru istniejących ścieżek plików
    existing_file_paths = set(f.file_path for f in current_files)
    # Wyszukiwanie nowych plików w folderze UPLOAD
    new_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER'])
                 if f.endswith(app.config['EXTENSION_LIST']) and f not in existing_file_paths]
    for file in new_files:
        # Dodawanie nowego rekordu
        # Domyślnie label '2' dla nowych plików
        new_record = FileLabel(file_path=file, file_label='2')
        db.session.add(new_record)
    # Zatwierdzanie zmian w bazie danych
    db.session.commit()


SOLVER_PATH = r"/simpack/Simpack-2023x.3/run/bin/linux64/simpack-slv"
LOCAL_SOLVER_PATH = r'C:\Program Files\Simpack-2023x.3\run\bin\win64\simpack-slv'


def uruchom_analize(arguments, solver_path):
    start_time = datetime.datetime.now()
    print(f"Rozpoczęcie analizy! {start_time} ")

    for argument in arguments:
        subprocess.run([solver_path] + argument)

    print(f"Analiza zakończona ({start_time} : {datetime.datetime.now()})")


def unpack_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f'Rozpakowano plik ZIP do: {extract_to}')


def find_spck_file(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.spck') and 'main_model' in root:
                return os.path.join(root, file)
    return None


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Brak pliku w żądaniu"}), 400
    file = request.files['file']
    flag = request.form.get('flag')
    if file.filename == '':
        return jsonify({"error": "Nie wybrano pliku"}), 400
    if file and allowed_file(file.filename):
        filename = os.path.basename(file.filename)
        filepath = os.path.join(
            'D:/PY_SCRIPT/Kolejkowanie_HELLER/v0_1_1/INPUT', filename)

        # Sprawdzenie, czy ścieżka katalogu istnieje; jeśli nie, utwórz ją
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        file.save(filepath)

        # Rozpakowanie pliku ZIP
        extract_to = os.path.join(
            'D:/PY_SCRIPT/Kolejkowanie_HELLER/v0_1_1/UNPACKED', os.path.splitext(filename)[0])
        unpack_zip(filepath, extract_to)
        spck_file = find_spck_file(extract_to)

        if spck_file:
            print(f'Znaleziono plik .spck: {spck_file}')
            current_files = FileLabel.query.order_by(FileLabel.order).all()
            label = 1
            if current_files:
                label = 2
            new_file_label = FileLabel(
                file_path=spck_file, file_label=label, order=1)
            db.session.add(new_file_label)
            try:
                db.session.commit()
                print('Dodano plik do bazy danych.')
            except Exception as e:
                print(f'Błąd przy dodawaniu do bazy danych: {e}')
                db.session.rollback()
        else:
            print('Nie znaleziono pliku .spck w rozpakowanym folderze')

        if flag == 'integration':
            subprocess.Popen(
                f'{LOCAL_SOLVER_PATH} --integration --file {spck_file}', creationflags=subprocess.CREATE_NEW_CONSOLE)

        elif flag == 'measurement':
            subprocess.Popen(
                f'{LOCAL_SOLVER_PATH} --measurement --file {spck_file}', creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            print('Nie znaleziono pliku .spck w rozpakowanym folderze')

        return jsonify({"message": "Plik został przesłany i jest przetwarzany."}), 200


@app.route('/get-data', methods=['GET'])
def get_data():
    files = FileLabel.query.all()  # Pobranie wszystkich rekordów
    files_data = []
    for file in files:
        files_data.append({"id": file.id, "file_path": file.file_path,
                          "file_label": file.file_label, "order": file.order})
    return jsonify(files_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
