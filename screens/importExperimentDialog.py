from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt5 import uic

import storage


class ImportExperimentDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('ui/ImportExperimentDialog.ui', self)
        self.ui.fileDialogButton.clicked.connect(self.openPathDialog)
        self.ui.addButton.clicked.connect(self.addButtonClicked)

    def openPathDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "All Files (*.csv *.xlsx);;CSV Files (*.csv);;Excel Files (*.xlsx)", options=options)
        self.ui.pathLineEdit.setText(fileName)
    
    def correctFileDirectoryCheck(self, file_path: str) -> bool:
        import os.path
        return os.path.exists(file_path)

    def addButtonClicked(self):
        if self.correctFileDirectoryCheck(self.ui.pathLineEdit.text()):
            exp = storage.from_file_imports.get_experiment_from_csv(self.ui.pathLineEdit.text())
            exp.add_into_db()
        else:
            self.filePathError()
    
    def filePathError(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Некорректный путь к файлу")
        msg.setInformativeText('Путь к файлу введен неверно или файла с таким путем не существует')
        msg.setWindowTitle("Сообщение об ошибке")
        msg.exec_()
