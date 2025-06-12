import sys
from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from foundation.basis import Attempt, getAllElements, crash, Experiment, addAttempt
from maths.methods import *
from maths.calc import *

'''
Виджет с информацией о попытках расчетов
'''

class AttemptWidget(QWidget):
    def __init__(self, attempt: Attempt):
        super().__init__()

        self.ui = uic.loadUi('ui/AttemptWidget.ui', self)

        self.attempt = attempt

        #self.ui.addAttemptButton.clicked.connect(self.addAttempt)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.ui.mainLayout.addWidget(self.canvas)
        self.drawChart()

        self.showInits()
        self.showResults()

    def drawChart(self):
        method = get_method(self.attempt.func, self.attempt.id_method, self.attempt.id_exp)
        ax = self.figure.add_subplot(111)
        method.draw_chart(self.attempt.init,ax)
        self.canvas.draw()

    def showInits(self):
        self.methods_dict = {0:'Имитации отжига', 1:'Гаусса-Зейделя', 2:'Хукка-Дживса', 3:'Антиградиент', 4:'Ньютона'}
        self.ui.initTextBrowser.append(f'№ Эксп.: {self.attempt.id_exp}')
        self.ui.initTextBrowser.append(f'Метод опт.: {self.methods_dict[self.attempt.id_method]}')
        for item in self.attempt.init.items():
            self.ui.initTextBrowser.append(f'{item[0]}: {item[1]}')

    def showResults(self):
        for item in self.attempt.result.items():
            if type(item[1]) == list:
                for i in item[1]:
                    self.ui.resultTextBrowser.append(f'{i}\n')
            elif type(item[1]) == dict:
                for i in item[1]:
                    self.ui.resultTextBrowser.append(f'{i}\n')
            else:
                self.ui.resultTextBrowser.append(f'{item[0]}: {item[1]}\n')

    def addAttempt(self):
        self.attempt.add_into_global_bd()