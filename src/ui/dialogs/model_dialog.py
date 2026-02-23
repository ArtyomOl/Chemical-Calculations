from typing import Optional

from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic

from domain.models import Model
from infrastructure.repositories import ModelRepository


class ModelDialog(QDialog):
    def __init__(self, parent=None, model: Optional[Model] = None):
        super().__init__(parent)
        self.ui = uic.loadUi('ui/ModelDialog.ui', self)
        self.model_repo = ModelRepository()
        self.model = model
        
        if model:
            self._load_model_data()
        
        self._connect_signals()

    def _connect_signals(self):
        self.ui.saveButton.clicked.connect(self._save_model)
        self.ui.cancelButton.clicked.connect(self.reject)

    def _load_model_data(self):
        self.ui.nameEdit.setText(self.model.name)
        self.ui.equationEdit.setText(self.model.equation)
        self.ui.calculatedParamEdit.setText(self.model.calculated_parameter)
        self.ui.argumentEdit.setText(self.model.argument)
        
        initial_data_str = '\n'.join([f'{k}: {v}' for k, v in self.model.initial_data.items()])
        self.ui.initialDataEdit.setPlainText(initial_data_str)

    def _save_model(self):
        try:
            name = self.ui.nameEdit.text().strip()
            equation = self.ui.equationEdit.text().strip()
            calc_param = self.ui.calculatedParamEdit.text().strip()
            argument = self.ui.argumentEdit.text().strip()
            
            if not all([name, equation, calc_param, argument]):
                QMessageBox.warning(self, 'Ошибка', 'Заполните все обязательные поля')
                return
            
            initial_data = self._parse_initial_data()
            
            if self.model:
                self.model.name = name
                self.model.equation = equation
                self.model.calculated_parameter = calc_param
                self.model.argument = argument
                self.model.initial_data = initial_data
                self.model_repo.update(self.model)
            else:
                new_model = Model(
                    name=name,
                    equation=equation,
                    calculated_parameter=calc_param,
                    argument=argument,
                    initial_data=initial_data
                )
                self.model_repo.create(new_model)
            
            QMessageBox.information(self, 'Успех', 'Модель успешно сохранена')
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при сохранении: {str(e)}')

    def _parse_initial_data(self) -> dict:
        text = self.ui.initialDataEdit.toPlainText()
        result = {}
        
        for line in text.split('\n'):
            line = line.strip()
            if not line or ':' not in line:
                continue
            
            key, value = line.split(':', 1)
            result[key.strip()] = float(value.strip())
        
        return result