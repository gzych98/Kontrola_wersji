# serwer.py
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


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Brak pliku w żądaniu"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nie wybrano pliku"}), 400
    if file and allowed_file(file.filename):
        # Tutaj można dodać logikę przetwarzania pliku
        filename = os.path.basename(file.filename)
        filepath = 'D:/PY_SCRIPT/Kolejkowanie_HELLER/v0_1_1/INPUT/' + filename
        file.save(filepath)
        # Informacja zwrotna dla klienta
        return jsonify({"message": "Plik został przesłany i jest przetwarzany."}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
