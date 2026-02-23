from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt5 import uic

from services.import_service import ImportService


class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = uic.loadUi('ui/ImportExperimentDialog.ui', self)
        self.import_service = ImportService()
        self.file_path = None
        
        self._connect_signals()

    def _connect_signals(self):
        self.ui.fileDialogButton.clicked.connect(self._select_file)
        self.ui.addButton.clicked.connect(self._import_experiment)

    def _select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Выберите файл',
            '',
            'CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*)'
        )
        
        if file_path:
            self.file_path = file_path
            self.ui.pathLineEdit.setText(file_path)

    def _import_experiment(self):
        if not self.file_path:
            QMessageBox.warning(self, 'Ошибка', 'Выберите файл для импорта')
            return
        
        try:
            article_id = 1
            self.import_service.import_and_save(self.file_path, article_id)
            QMessageBox.information(self, 'Успех', 'Эксперимент успешно импортирован')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при импорте: {str(e)}')