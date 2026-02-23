from PyQt5.QtWidgets import (
    QMainWindow, QTableWidgetItem, QMessageBox, 
    QMenu, QAbstractItemView, QHeaderView
)
from PyQt5 import uic

from infrastructure.repositories import (
    ExperimentRepository, ElementRepository,
    ModelRepository, ArticleRepository
)
from services.search_service import SearchService
from ui.dialogs.import_dialog import ImportDialog
from ui.dialogs.model_dialog import ModelDialog
from ui.dialogs.experiment_info_dialog import ExperimentInfoDialog
from ui.widgets.calculation_widget import CalculationWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('ui/UiForChem.ui', self)
        
        self.experiment_repo = ExperimentRepository()
        self.element_repo = ElementRepository()
        self.model_repo = ModelRepository()
        self.article_repo = ArticleRepository()
        self.search_service = SearchService()
        
        self.selected_experiment_row = -1
        self.selected_model_row = -1
        
        self._setup_ui()
        self._connect_signals()
        self._load_initial_data()

    def _setup_ui(self):
        self.setWindowTitle('Chemical Calculations')
        self.ui.experimentsTab.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.modelsTab.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.setStyleSheet('''
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #000000;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                background-color: #2196F3;
                color: white;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        ''')

    def _connect_signals(self):
        self.ui.add_button.clicked.connect(self._on_add_experiment)
        self.ui.update_button_experiments.clicked.connect(self._load_experiments)
        self.ui.filterButton.clicked.connect(self._on_filter_experiments)
        self.ui.swapButton.clicked.connect(self._on_swap_filters)
        self.ui.experimentsTab.clicked.connect(self._on_experiment_clicked)
        
        self.ui.addModelButton.clicked.connect(self._on_add_model)
        self.ui.modelsTab.clicked.connect(self._on_model_clicked)
        
        self.ui.update_button_elements.clicked.connect(self._load_elements)

    def _load_initial_data(self):
        self._load_experiments()
        self._load_elements()
        self._load_models()
        self._load_articles()

    def _load_experiments(self, first_filter: str = None, second_filter: str = None):
        self.ui.experimentsTab.setRowCount(0)
        
        if not first_filter:
            first_filter = self.ui.firstElementEdit.text() or 'Any'
        if not second_filter:
            second_filter = self.ui.secondElementEdit.text() or 'Any'
        
        first_elements = self.search_service.get_elements_by_filter(first_filter)
        second_elements = self.search_service.get_elements_by_filter(second_filter)
        
        experiments = self.experiment_repo.get_all()
        
        for exp in experiments:
            if (exp.first_element in first_elements or first_filter == 'Any') and \
               (exp.second_element in second_elements or second_filter == 'Any'):
                self._add_experiment_row(exp)
        
        self._resize_table_columns(self.ui.experimentsTab)

    def _add_experiment_row(self, exp):
        row = self.ui.experimentsTab.rowCount()
        self.ui.experimentsTab.insertRow(row)
        
        self.ui.experimentsTab.setItem(row, 0, QTableWidgetItem(str(exp.id)))
        self.ui.experimentsTab.setItem(row, 1, QTableWidgetItem(exp.first_element))
        self.ui.experimentsTab.setItem(row, 2, QTableWidgetItem(exp.second_element))
        
        process_type = 'ИЗОБАРНЫЙ' if exp.is_isobaric else 'ИЗОТЕРМИЧЕСКИЙ'
        self.ui.experimentsTab.setItem(row, 3, QTableWidgetItem(process_type))
        
        temp = '-' if exp.temperature is None else str(exp.temperature)
        pressure = '-' if exp.pressure is None else str(exp.pressure)
        self.ui.experimentsTab.setItem(row, 4, QTableWidgetItem(temp))
        self.ui.experimentsTab.setItem(row, 5, QTableWidgetItem(pressure))
        
        article = self.article_repo.get_by_id(exp.article_id)
        article_name = article.name if article else '-'
        self.ui.experimentsTab.setItem(row, 6, QTableWidgetItem(article_name))

    def _load_elements(self):
        self.ui.elementsTab.setRowCount(0)
        elements = self.element_repo.get_all()
        
        for i, element in enumerate(elements):
            self.ui.elementsTab.insertRow(i)
            self.ui.elementsTab.setItem(i, 0, QTableWidgetItem(element.name))
            branches_str = '\n'.join(element.branches)
            self.ui.elementsTab.setItem(i, 1, QTableWidgetItem(branches_str))

    def _load_models(self):
        self.ui.modelsTab.setRowCount(0)
        models = self.model_repo.get_all()
        
        for i, model in enumerate(models):
            self.ui.modelsTab.insertRow(i)
            self.ui.modelsTab.setItem(i, 0, QTableWidgetItem(model.name))
            self.ui.modelsTab.setItem(i, 1, QTableWidgetItem(model.equation))
        
        self._resize_table_columns(self.ui.modelsTab)

    def _load_articles(self):
        articles = self.article_repo.get_all()
        for article in articles:
            info = f'Имя: {article.name}\nАвтор: {article.author}\nГод: {article.year}'
            self.articles_list.addItem(info)
            self.articles_list.addItem(article.link)
            self.articles_list.addItem('')

    def _resize_table_columns(self, table):
        header = table.horizontalHeader()
        for i in range(table.columnCount() - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(table.columnCount() - 1, QHeaderView.Stretch)

    def _on_add_experiment(self):
        dialog = ImportDialog(self)
        if dialog.exec_():
            self._load_experiments()

    def _on_filter_experiments(self):
        first_filter = self.ui.firstElementEdit.text()
        second_filter = self.ui.secondElementEdit.text()
        self._load_experiments(first_filter, second_filter)

    def _on_swap_filters(self):
        first = self.ui.firstElementEdit.text()
        second = self.ui.secondElementEdit.text()
        self.ui.firstElementEdit.setText(second)
        self.ui.secondElementEdit.setText(first)

    def _on_experiment_clicked(self):
        current_row = self.ui.experimentsTab.currentRow()
        if self.selected_experiment_row == current_row:
            self.ui.experimentsTab.clearSelection()
            self.selected_experiment_row = -1
        else:
            self.selected_experiment_row = current_row

    def _on_model_clicked(self):
        current_row = self.ui.modelsTab.currentRow()
        if self.selected_model_row == current_row:
            self.ui.modelsTab.clearSelection()
            self.selected_model_row = -1
        else:
            self.selected_model_row = current_row

    def _on_add_model(self):
        dialog = ModelDialog(self)
        if dialog.exec_():
            self._load_models()

    def contextMenuEvent(self, event):
        if self.ui.tabWidget.currentIndex() == 0:
            self._show_experiment_context_menu(event)
        elif self.ui.tabWidget.currentIndex() == 3:
            self._show_model_context_menu(event)

    def _show_experiment_context_menu(self, event):
        if self.selected_experiment_row == -1:
            return
        
        menu = QMenu(self)
        calc_action = menu.addAction('Рассчитать')
        info_action = menu.addAction('Информация')
        
        action = menu.exec_(self.mapToGlobal(event.pos()))
        
        if action == calc_action:
            exp_id = int(self.ui.experimentsTab.item(self.selected_experiment_row, 0).text())
            self._open_calculation(exp_id)
        elif action == info_action:
            exp_id = int(self.ui.experimentsTab.item(self.selected_experiment_row, 0).text())
            dialog = ExperimentInfoDialog(exp_id, self)
            dialog.exec_()

    def _show_model_context_menu(self, event):
        if self.selected_model_row == -1:
            return
        
        menu = QMenu(self)
        edit_action = menu.addAction('Изменить')
        
        action = menu.exec_(self.mapToGlobal(event.pos()))
        
        if action == edit_action:
            model_name = self.ui.modelsTab.item(self.selected_model_row, 0).text()
            model = self.model_repo.get_by_name(model_name)
            if model:
                dialog = ModelDialog(self, model)
                if dialog.exec_():
                    self._load_models()

    def _open_calculation(self, experiment_id: int):
        self.ui.tabWidget.setCurrentIndex(4)
        self.ui.id_exp_edit.setText(str(experiment_id))

    @staticmethod
    def show_error(message: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText('Ошибка')
        msg.setInformativeText(message)
        msg.setWindowTitle('Ошибка')
        msg.exec_()