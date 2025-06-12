from PyQt5.QtWidgets import QDialog
from PyQt5 import uic

import foundation.basis

'''
Диалоговое окно для просмотра информации данных эксперимента
'''

class ExperimentInfoDialog(QDialog):
    def __init__(self, id_experiments: list):
        super().__init__()

        self.ui = uic.loadUi('ui/experimentInfoDialog.ui', self)

        self.id_experiments = id_experiments
        self.showInfo()

    def showInfo(self):
        for id_exp in self.id_experiments:
            inform = foundation.basis.getExperimentAsID(id_exp)
            for item in inform.items():
                self.ui.listWidget.addItem(f'{item[0]}: {item[1]}')
            self.ui.listWidget.addItem('\n')

