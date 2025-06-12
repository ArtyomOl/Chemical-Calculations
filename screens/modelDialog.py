from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic

import foundation.basis

'''
Диалоговое окно для создания новой модели
'''

class ModelDialog(QDialog):
    def __init__(self, model_id = None):
        super().__init__()
        self.model_id = model_id
        self.ui = uic.loadUi('ui/ModelDialog.ui', self)
        self.ui.saveButton.clicked.connect(self.saveChanges)

        if self.model_id:
            model = foundation.basis.getModelById(self.model_id)
            self.ui.nameEdit.setText(model.name)
            self.ui.equationEdit.setText(model.equation)
            self.ui.initialEdit.setText('')
            for item in model.initial_data.items():
                self.ui.initialEdit.append(str(item[0]) + ' : ' + str(item[1]))
            self.ui.calcParamEdit.setText(model.calculated_parameter)
            self.ui.argParamEdit.setText(model.argument)
            
    
    def saveChanges(self):
        name = self.ui.nameEdit.text()
        equation = self.ui.equationEdit.text()
        initials = self.ui.initialEdit.toPlainText()
        calc_param = self.ui.calcParamEdit.text()
        argument = self.ui.argParamEdit.text()

        initial_dict = {}

        if initials:
            initials_array = initials.split('\n')
            for expression in initials_array:
                while '  ' in expression:
                    expression = expression.replace('  ', ' ')
                expression = expression.replace(': ', ':')
                expression = expression.replace(' :', ':')
                if len(expression.split(':')) < 2:
                    self.showError('Некорректный ввод')
                    return
                key, value = expression.split(':')[0], expression.split(':')[1]
                initial_dict[key] = value
                    
        new_model = foundation.basis.Model(name, equation, initial_dict, calc_param, argument)
        
        if self.model_id:
            new_model.updateInDB(self.model_id)
        else:
            new_model.addIntoDB()
        
        self.reject()

    @staticmethod
    def showError(message):
        """Показать окно с ошибкой"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Ошибка")
        msg.setInformativeText(message)
        msg.setWindowTitle("Ошибка")
        msg.exec_()
