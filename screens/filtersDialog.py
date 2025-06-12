from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

'''
Диалоговое окно для настройки фильтров 
'''

class FiltersDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('ui/FiltersDialog.ui')