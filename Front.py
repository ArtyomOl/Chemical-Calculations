import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QLabel, QTableWidget, QWidget, \
     QTableWidgetItem, QMessageBox, QMenu, QAbstractItemView, QFileDialog
from PyQt5 import uic, QtWidgets
import json
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

import storage
import foundation.basis
from foundation.basis import Attempt, getAllElements, crash, Experiment, addAttempt
from maths.methods import *
from maths.calc import *


# виджет попыток
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


# окно для добавления экспериментов
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



# окно с информацией об эксперименте
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


# окно с фильтрами экспериментов для поиска по элементам
class FiltersDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('ui/FiltersDialog.ui')


# окно для открытия файла для импорта данных эксперимента
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
            
    
    def saveChanges(self):
        name = self.ui.nameEdit.text()
        equation = self.ui.equationEdit.text()
        initials = self.ui.initialEdit.toPlainText()

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
                if value.isnumeric():
                    initial_dict[key] = float(value)
                else:
                    initial_dict[key] = value
                    
        new_model = foundation.basis.Model(name, equation, initial_dict)
        
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


#   ОСНОВНОЕ ОКНО   ##################################################################################################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = uic.loadUi('ui/UiForChem.ui', self)

        self.EXP_PAGE_NUM = 0
        self.ATTEMPT_PAGE_NUM = 4
        self.MODELS_PAGE_NUM = 3

        # для экспериментов
        self.ui.add_button.clicked.connect(self.addButtonClicked)
        self.ui.update_button_experiments.clicked.connect(self.updateTableExperiments)
        self.ui.filterButton.clicked.connect(self.filterButton_clicked)
        self.ui.swapButton.clicked.connect(self.swapButtonClicked)

        self.createTableExperiments()
        self.ui.experimentsTab.clicked.connect(self.clickedOnExperimentsTab)

        self.exp_current_row = -1
        self.model_current_row = -1

        # для расчетов
        self.makeCalculatePage()

        # для статей
        self.showArticles()

        # для элементов
        self.ui.update_button_elements.clicked.connect(self.createTableElements)

        # для моделей
        self.ui.addModelButton.clicked.connect(self.addModel)
        self.ui.modelsTab.clicked.connect(self.clickedOnModelsTab)

        self.createTableElements()
        self.createTableModels()


    # создание таблицы экспериментов
    def createTableExperiments(self, first_element_filter: str = None, second_element_filter: str = None):
        if (first_element_filter == None or first_element_filter == ''):
            first_element_filter = 'Any'
        if (second_element_filter == None or second_element_filter == ''):
            second_element_filter = 'Any'

        first_element_list = foundation.basis.getElementsListByFilter(first_element_filter)
        second_element_list = foundation.basis.getElementsListByFilter(second_element_filter)

        self.ui.experimentsTab.setRowCount(0)
        self.ui.experimentsTab.setSelectionBehavior(QAbstractItemView.SelectRows) #  при нажатии на таблицу выделяется не ячейка, а выбранная строка целиком

        self.setStyleSheet("""
                    QTableWidget::item:selected{
                        background-color: #F0FFF0;
                        color: #000000;
                    }
                    """)

        experiments = getAllElements('experiments')

        j = 0
        for i in range(0, len(experiments)):
            if (experiments[i]['first_element'] in first_element_list or first_element_filter == 'Any') and (experiments[i]['second_element'] in second_element_list or second_element_filter == 'Any'):
                self.ui.experimentsTab.insertRow(self.ui.experimentsTab.rowCount())
                exp_arr = json.loads(experiments[i]['source_data'])
                self.ui.experimentsTab.setItem(j, 0, QTableWidgetItem(str(experiments[i]['id'])))
                self.ui.experimentsTab.setItem(j, 1, QTableWidgetItem(experiments[i]['first_element']))
                self.ui.experimentsTab.setItem(j, 2, QTableWidgetItem(experiments[i]['second_element']))
                process_type = 'ИЗОБАРНЫЙ' if str(experiments[i]['temperature']) == 'None' else 'ИЗОТЕРМИЧЕСКИЙ'
                self.ui.experimentsTab.setItem(j, 3, QTableWidgetItem(process_type))
                temperature = '-' if str(experiments[i]['temperature']) == 'None' else str(experiments[i]['temperature'])
                pressure = '-' if str(experiments[i]['pressure']) == 'None' else str(experiments[i]['pressure'])
                self.ui.experimentsTab.setItem(j, 4, QTableWidgetItem(temperature))
                self.ui.experimentsTab.setItem(j, 5, QTableWidgetItem(pressure))
                self.ui.experimentsTab.setItem(j, 6, QTableWidgetItem(foundation.basis.getArticleName(experiments[i]['article'])))
                j += 1
    

        # подгон размера столбцов под данные
        horizontalHeader = self.ui.experimentsTab.horizontalHeader()
        for i in range(self.ui.experimentsTab.columnCount() - 1):
            horizontalHeader.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        horizontalHeader.setSectionResizeMode(self.ui.experimentsTab.columnCount() - 1, QtWidgets.QHeaderView.Stretch)

    # обновление таблицы элементов
    def updateTableExperiments(self):
        self.createTableExperiments()

    # создание таблицы элементов
    def createTableElements(self):
        self.ui.elementsTab.setRowCount(0)
        self.ui.elementsTab.setRowCount(1)

        elements = getAllElements('elements')
        
        for i in range(0, len(elements)):
            self.ui.elementsTab.insertRow(self.ui.elementsTab.rowCount())
            spec_arr = elements[i]['branch'].split(';')
            self.ui.elementsTab.setItem(i, 0, QTableWidgetItem(elements[i]['name']))
            self.ui.elementsTab.setItem(i, 1, QTableWidgetItem(crash(spec_arr)))

    # обработка нажатия на таблицу экспериментов
    def clickedOnExperimentsTab(self, event = None):
        if self.exp_current_row != self.ui.experimentsTab.currentRow():
            self.exp_current_row = self.ui.experimentsTab.currentRow()
        else:
            if event:
                self.ui.experimentsTab.clearSelection()
                self.ui.experimentsTab.setCurrentCell(-1, 0)
                self.exp_current_row = -1

    # обработка нажатия на таблицу моделей
    def clickedOnModelsTab(self, event = None):
        if self.model_current_row != self.ui.modelsTab.currentRow():
            self.model_current_row = self.ui.modelsTab.currentRow()
        else:
            if event:
                self.ui.modelsTab.clearSelection()
                self.ui.modelsTab.setCurrentCell(-1, 0)
                self.model_current_row = -1


    # функция для обработки нажатия на кнопку "Добавить" во вкладке Эксперименты
    def addButtonClicked(self):
        add_window = ImportExperimentDialog()
        add_window.exec()


    # вывод информации об статьях
    def showArticles(self):
        items = getAllElements('articles')
        for item in items:
            item_string = 'Имя: ' +  item['name'] + '\n' + 'Автор: ' + item['author'] + '\n' + 'Год издания: ' + str(item['year'])
            self.articles_list.addItem(item_string)
            self.articles_list.addItem(item['link'])
            self.articles_list.addItem('')

    # Контекстное меню во вкладке эксперименты
    def contextMenuEvent(self, event):
        try:
            if self.ui.tabWidget.currentIndex() == self.EXP_PAGE_NUM:
                top_row = self.ui.experimentsTab.selectionModel().selectedRows()
                rows = [i for i in range(self.ui.experimentsTab.currentRow() - len(self.ui.experimentsTab.selectionModel().selectedRows()) + 1, self.ui.experimentsTab.currentRow() + 1)]
                id_exp = [int(self.ui.experimentsTab.item(row, 0).text()) for row in rows]
                id_exp_string = ''
                for i in id_exp:
                    id_exp_string += f'{i},'
                id_exp_string = id_exp_string[:-1]

                item = self.ui.experimentsTab.itemAt(event.pos())
                #now_exp_current_row = self.ui.experimentsTab.currentRow()
                self.clickedOnExperimentsTab()
                if self.exp_current_row != -1:
                    contextMenu = QMenu(self)
                    calcAct = contextMenu.addAction("Рассчитать")
                    showAct = contextMenu.addAction("Информация")
                    action = contextMenu.exec_(self.mapToGlobal(event.pos()))
                    if action == calcAct:
                        self.ui.tabWidget.setCurrentIndex(self.ATTEMPT_PAGE_NUM)
                        self.ui.id_exp_edit.setText(id_exp_string)
                    elif action == showAct:
                        d = ExperimentInfoDialog(id_exp)
                        d.exec()

            elif self.ui.tabWidget.currentIndex() == self.MODELS_PAGE_NUM:
                row = self.ui.modelsTab.currentRow()
                name = self.ui.modelsTab.item(row, 0).text()
                _, model_id = foundation.basis.getModelByName(name)

                self.clickedOnModelsTab()
                if self.model_current_row != -1:
                    contextMenu = QMenu(self)
                    changeAct = contextMenu.addAction("Изменить")
                    action = contextMenu.exec_(self.mapToGlobal(event.pos()))
                    if action == changeAct:
                        self.addModel(model_id)
        except Exception as ex:
            print(ex)
    

    # создание таблицы элементов
    def createTableModels(self):
        self.ui.modelsTab.setRowCount(0)
        self.ui.modelsTab.setRowCount(1)

        self.ui.modelsTab.setSelectionBehavior(QAbstractItemView.SelectRows)

        models = getAllElements('models')
        
        for i,model in enumerate(models):
            self.ui.modelsTab.insertRow(self.ui.modelsTab.rowCount())
            self.ui.modelsTab.setItem(i, 0, QTableWidgetItem(model['name']))
            self.ui.modelsTab.setItem(i, 1, QTableWidgetItem(model['equation']))

    # Создание страницы рассчета
    def makeCalculatePage(self):
        self.ui.calculateButton.clicked.connect(self.calculateButton_clicked)

        self.ui.modelComboBox.addItem('Margulis')
        
        self.ui.methodsComboBox.addItem('Имитации отжига')
        self.ui.methodsComboBox.addItem('Гаусса-Зейделя')
        self.ui.methodsComboBox.addItem('Хукка-Дживса')
        self.ui.methodsComboBox.addItem('Антиградиент')
        self.ui.methodsComboBox.addItem('Ньютона')

        self.fillModelComboBox()

        self.methods_dict = {'Имитации отжига': 0, 'Гаусса-Зейделя': 1, 'Хукка-Дживса': 2, 'Антиградиент': 3, 'Ньютона': 4}
        self.method_name = 'Имитации отжига'

        self.model = maths.functions.margulis

        self.ui.modelComboBox.activated.connect(self.updateModelComboBox)
        self.ui.methodsComboBox.activated.connect(self.updateMethodsComboBox)
        self.attemptsTabWidget.tabCloseRequested.connect(self.closeAttemptTab)

        self.ui.attemptsTabWidget.removeTab(0)
        self.ui.attemptsTabWidget.removeTab(0)

        self.ui.multistartCheckBox.stateChanged.connect(self.multistartCheckBoxChanged)
        self.turnVisibility(visibility=True)

    # Изменение видимости полей на странице рассчета
    def turnVisibility(self, visibility: bool = True):
        self.ui.attempt_label_4.setEnabled(visibility)
        self.ui.init_edit.setEnabled(visibility)
        self.ui.attempt_label_5.setEnabled(not visibility)
        self.ui.attempt_label_6.setEnabled(not visibility)
        self.ui.attempt_label_7.setEnabled(not visibility)
        self.ui.min_edit.setEnabled(not visibility)
        self.ui.max_edit.setEnabled(not visibility)
        self.ui.count_edit.setEnabled(not visibility)

    # Переключение на мультизапуск и обратно
    def multistartCheckBoxChanged(self):
        if self.ui.multistartCheckBox.isChecked():
            self.turnVisibility(visibility=False)
        else:
            self.turnVisibility(visibility=True)

    # Заполнение modelComboBox
    def fillModelComboBox(self):
        """
        Заполняет QComboBox (modelComboBox) названиями моделей из базы данных.
        Очищает существующие элементы перед заполнением.
        """
        try:
            self.ui.modelComboBox.clear()
            
            models = foundation.basis.getAllModelsName()
            
            for model in models:
                self.ui.modelComboBox.addItem(model[0])
                
        except Exception as ex:
            print(f"Ошибка при заполнении комбобокса моделями: {ex}")

    # Изменение modelComboBox
    def updateModelComboBox(self):
        model_name = self.ui.modelComboBox.currentText()
        model, _ = foundation.basis.getModelByName(model_name)
        self.model = model.createFunction()

    # Изменение methodsComboBox
    def updateMethodsComboBox(self):
        self.method_name = self.ui.methodsComboBox.currentText()

    # функция для проверки корректности ввода данных пользователем
    def checkingExperimentsNumberImput(self):
        id_experiments = self.ui.id_exp_edit.text()
        if not id_experiments: return False
        for i in id_experiments:
            if i not in '0123456789, ':
                return False
        return True

    # Проверка на корректность ввода данных
    def checkingInput(self):
        return self.checkingExperimentsNumberImput()

    # функция вызова предупреждения об ошибке в случае некорректного ввода
    @staticmethod
    def errorMessage():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Ошибка ввода")
        msg.setInformativeText('Некорректный ввод')
        msg.setWindowTitle("Сообщение об ошибке")
        msg.exec_()

    # Обработка нажатия кнопки Добавить
    def calculateButton_clicked(self):
        try:
            if self.checkingInput():
                id_experiments = self.ui.id_exp_edit.text()
                id_experiments.replace(' ', '')
                for id_experiment in id_experiments.split(','):
                    id_exp = int(id_experiment)

                    if self.ui.multistartCheckBox.isChecked():
                        mins_string = '{' + self.ui.min_edit.text() + '}'
                        maxs_string = '{' + self.ui.max_edit.text() + '}'
                        try:
                            maxs = json.loads(maxs_string)
                            mins = json.loads(mins_string)
                            if not maxs.keys() == mins.keys():
                                raise ValueError("maxs and mins signatures don't match")
                        except Exception as ex:
                            self.errorMessage()
                            return
                        
                        count = int(self.ui.count_edit.text())
                        result = multi_start(id_exp, mins,maxs, count, self.methods_dict[self.method_name], self.model)
                        attempt = Attempt(id_exp, self.model, self.methods_dict[self.method_name],
                                          {'mins':mins, 'maxs':maxs}, {'result':result})
                    else:
                        init_data_string = '{' + self.ui.init_edit.text() + '}'
                        try:
                            init_data = json.loads(init_data_string)
                        except Exception as ex:
                            self.errorMessage()
                        result = simple_calculation(id_exp, init_data, self.methods_dict[self.method_name], self.model)
                        attempt = Attempt(id_exp, self.model, self.methods_dict[self.method_name], init_data, result)
                    page = AttemptWidget(attempt)
                    n = attempt.number
                    self.ui.attemptsTabWidget.addTab(page, f'Расчёт {n}')
                    self.ui.attemptsTabWidget.setCurrentIndex(self.ui.attemptsTabWidget.count() - 1)
            else:
                self.errorMessage()
        except Exception as ex:
            print(ex)

    # Закрытие вкладки расчета
    def closeAttemptTab(self, index):
        self.attemptsTabWidget.removeTab(index)

    # Обработка нажатия на кнопку Найти
    def filterButton_clicked(self):
        first_element_filter = self.ui.firstElementEdit.text()
        second_element_filter = self.ui.secondElementEdit.text()
        self.createTableExperiments(first_element_filter=first_element_filter, second_element_filter=second_element_filter)

    # Обработка нажатия на кнопку замены местами названий первого и второго веществ
    def swapButtonClicked(self):
        first_element = self.ui.firstElementEdit.text()
        second_element = self.ui.secondElementEdit.text()
        self.ui.firstElementEdit.setText(second_element)
        self.ui.secondElementEdit.setText(first_element)

    def addModel(self, model_id = None):
        print(model_id)
        modelDialog = ModelDialog(model_id)
        modelDialog.finished.connect(self.onModelDialogClosed)
        modelDialog.show()

    def onModelDialogClosed(self):
        self.createTableModels()
        self.fillModelComboBox()


##################################################################################################################################################################


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()