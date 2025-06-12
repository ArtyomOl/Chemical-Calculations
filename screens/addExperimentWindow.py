from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

from foundation.basis import Experiment
from maths.methods import *
from maths.calc import *

'''
Окно для добавления нового эксперимента 
'''

class AddExperimentWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = uic.loadUi('ui/AddExperimentWindow.ui', self)

        self.ui.add_button.clicked.connect(self.addButtonClicked)

    # обработка нажатия кнопки "Добавить"
    def addButtonClicked(self):
        first_element = self.ui.lineEdit.text()
        second_element = self.ui.lineEdit_2.text()
        temperature = self.ui.lineEdit_3.text()
        x2 = self.ui.textEdit.toPlainText().split('\n')
        PkPa = self.ui.textEdit_2.toPlainText().split('\n')
        dPPa = self.ui.textEdit_5.toPlainText().split('\n')
        y1 = self.ui.textEdit_3.toPlainText().split('\n')
        y2 = self.ui.textEdit_4.toPlainText().split('\n')
        GEJ = self.ui.textEdit_6.toPlainText().split('\n')
        x2 = list(filter(('').__ne__, x2))
        PkPa = list(filter(('').__ne__, PkPa))
        dPPa = list(filter(('').__ne__, dPPa))
        y1 = list(filter(('').__ne__, y1))
        y2 = list(filter(('').__ne__, y2))
        GEJ = list(filter(('').__ne__, GEJ))
        source_data = {'x2': x2, 'PkPa':PkPa, 'dPPa':dPPa, 'y1':y1, 'y2':y2, 'GEJ':GEJ}
        article = self.ui.lineEdit_4.text()
        if (first_element != '' and second_element != '' and temperature != '' and x2 != [] and PkPa != [] and dPPa != [] and y1 != [] and y2 != [] and GEJ != [] and article != ''):
            exp = Experiment(first_element, second_element, temperature, source_data, article)
            exp.add_into_db()
            self.ui.error_label.setText('')
            self.ui.lineEdit.setText('')
            self.ui.lineEdit_2.setText('')
            self.ui.lineEdit_3.setText('')
            self.ui.lineEdit_4.setText('')
            self.ui.textEdit.setPlainText('')
            self.ui.textEdit_2.setPlainText('')
            self.ui.textEdit_3.setPlainText('')
            self.ui.textEdit_4.setPlainText('')
            self.ui.textEdit_5.setPlainText('')
            self.ui.textEdit_6.setPlainText('')
        else:
            self.ui.error_label.setText("Не все поля заполнены")