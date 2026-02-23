import json
from typing import Dict

from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from domain.models import Model
from infrastructure.repositories import ExperimentRepository, ModelRepository
from services.calculation_service import CalculationService


METHOD_NAMES = {
    0: 'Имитация отжига',
    1: 'Гаусса-Зейделя',
    2: 'Хукка-Дживса',
    3: 'Антиградиент',
    4: 'Ньютона'
}


class CalculationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = uic.loadUi('ui/AttemptWidget.ui', self)
        
        self.experiment_repo = ExperimentRepository()
        self.model_repo = ModelRepository()
        self.calc_service = CalculationService()
        
        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ui.mainLayout.addWidget(self.canvas)
        
        self._setup_ui()

    def _setup_ui(self):
        models = self.model_repo.get_all()
        for model in models:
            self.ui.modelComboBox.addItem(model.name)
        
        for method_id, method_name in METHOD_NAMES.items():
            self.ui.methodComboBox.addItem(method_name)
        
        self.ui.calculateButton.clicked.connect(self._on_calculate)
        self.ui.multiStartCheckBox.stateChanged.connect(self._on_multistart_changed)
        
        self._toggle_multistart_fields(False)

    def _toggle_multistart_fields(self, is_multistart: bool):
        self.ui.initialParamsEdit.setEnabled(not is_multistart)
        self.ui.minParamsEdit.setEnabled(is_multistart)
        self.ui.maxParamsEdit.setEnabled(is_multistart)
        self.ui.countEdit.setEnabled(is_multistart)

    def _on_multistart_changed(self):
        is_checked = self.ui.multiStartCheckBox.isChecked()
        self._toggle_multistart_fields(is_checked)

    def _on_calculate(self):
        try:
            experiment_id = int(self.ui.experimentIdEdit.text())
            model_name = self.ui.modelComboBox.currentText()
            method_id = self.ui.methodComboBox.currentIndex()
            
            model = self.model_repo.get_by_name(model_name)
            if not model:
                QMessageBox.warning(self, 'Ошибка', 'Модель не найдена')
                return
            
            if self.ui.multiStartCheckBox.isChecked():
                self._run_multistart(experiment_id, model, method_id)
            else:
                self._run_single(experiment_id, model, method_id)
                
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при расчете: {str(e)}')

    def _run_single(self, experiment_id: int, model: Model, method_id: int):
        initial_params_str = self.ui.initialParamsEdit.text()
        initial_params = self._parse_params(initial_params_str)
        
        result, cost = self.calc_service.optimize(
            experiment_id, 
            model, 
            method_id, 
            initial_params
        )
        
        self._display_results(experiment_id, model, method_id, initial_params, result, cost)

    def _run_multistart(self, experiment_id: int, model: Model, method_id: int):
        mins = self._parse_params(self.ui.minParamsEdit.text())
        maxs = self._parse_params(self.ui.maxParamsEdit.text())
        count = int(self.ui.countEdit.text())
        
        results = self.calc_service.multi_start_optimize(
            experiment_id,
            model,
            method_id,
            mins,
            maxs,
            count
        )
        
        self._display_multistart_results(
            experiment_id, 
            model, 
            method_id, 
            {'mins': mins, 'maxs': maxs, 'count': count},
            results
        )

    def _display_results(
        self, 
        experiment_id: int, 
        model: Model, 
        method_id: int,
        initial_params: Dict[str, float],
        result: Dict[str, float],
        cost: float
    ):
        self.ui.initTextBrowser.clear()
        self.ui.initTextBrowser.append(f'Эксперимент: {experiment_id}')
        self.ui.initTextBrowser.append(f'Модель: {model.name}')
        self.ui.initTextBrowser.append(f'Метод: {METHOD_NAMES[method_id]}')
        self.ui.initTextBrowser.append('\nНачальные параметры:')
        for key, value in initial_params.items():
            self.ui.initTextBrowser.append(f'  {key}: {value}')
        
        self.ui.resultTextBrowser.clear()
        self.ui.resultTextBrowser.append('Результат оптимизации:')
        for key, value in result.items():
            self.ui.resultTextBrowser.append(f'  {key}: {value:.6f}')
        self.ui.resultTextBrowser.append(f'\nЦелевая функция: {cost:.6f}')
        
        self._plot_results(experiment_id, model, result)

    def _display_multistart_results(
        self,
        experiment_id: int,
        model: Model,
        method_id: int,
        init_data: Dict,
        results: list
    ):
        self.ui.initTextBrowser.clear()
        self.ui.initTextBrowser.append(f'Эксперимент: {experiment_id}')
        self.ui.initTextBrowser.append(f'Модель: {model.name}')
        self.ui.initTextBrowser.append(f'Метод: {METHOD_NAMES[method_id]}')
        self.ui.initTextBrowser.append(f'\nМультистарт: {init_data["count"]} запусков')
        self.ui.initTextBrowser.append(f'Диапазоны:')
        for key in init_data['mins']:
            self.ui.initTextBrowser.append(
                f'  {key}: [{init_data["mins"][key]}, {init_data["maxs"][key]}]'
            )
        
        self.ui.resultTextBrowser.clear()
        self.ui.resultTextBrowser.append(f'Найдено решений: {len(results)}')
        for i, result in enumerate(results, 1):
            self.ui.resultTextBrowser.append(f'\nРешение {i}:')
            for key, value in result.items():
                self.ui.resultTextBrowser.append(f'  {key}: {value:.6f}')
        
        if results:
            self._plot_results(experiment_id, model, results[0])

    def _plot_results(self, experiment_id: int, model: Model, optimized_params: Dict[str, float]):
        experiment = self.experiment_repo.get_by_id(experiment_id)
        if not experiment:
            return
        
        x_model, y_model, x_exp, y_exp = self.calc_service.generate_plot_data(
            experiment, 
            model, 
            optimized_params
        )
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.plot(x_model, y_model, 'g-', linewidth=2, label='Модель')
        ax.plot(x_exp, y_exp, 'ro', markersize=8, label='Эксперимент')
        
        ax.set_xlabel('x₂', fontsize=12)
        ax.set_ylabel(model.calculated_parameter, fontsize=12)
        ax.set_title(f'T = {experiment.temperature} K', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        self.canvas.draw()

    def _parse_params(self, params_str: str) -> Dict[str, float]:
        params_str = params_str.strip()
        if params_str.startswith('{'):
            return json.loads(params_str)
        
        params_str = '{' + params_str + '}'
        return json.loads(params_str)