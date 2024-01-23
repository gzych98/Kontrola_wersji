from PyQt5.QtWidgets import QMessageBox
from ftplib import FTP
import os
import shutil
import datetime


def current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S__")


def copy_file_with_timestamp(source_path):
    timestamp = current_timestamp()
    directory, filename = os.path.split(source_path)
    new_filename = f"{timestamp}_{filename}"
    new_full_path = os.path.join(directory, new_filename)
    shutil.copy2(source_path, new_full_path)
    return new_full_path


def connect_to_ftp(address, port, user, password):
    with FTP() as ftp:
        ftp.connect(host=address, port=port)
        ftp.login(user, password)
        return ftp


def show_message(title, message):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec_()
