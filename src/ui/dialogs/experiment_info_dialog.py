from PyQt5.QtWidgets import QDialog
from PyQt5 import uic

from infrastructure.repositories import ExperimentRepository, ArticleRepository


class ExperimentInfoDialog(QDialog):
    def __init__(self, experiment_id: int, parent=None):
        super().__init__(parent)
        self.ui = uic.loadUi('ui/experimentInfoDialog.ui', self)
        
        self.experiment_repo = ExperimentRepository()
        self.article_repo = ArticleRepository()
        
        self._load_experiment_info(experiment_id)

    def _load_experiment_info(self, experiment_id: int):
        experiment = self.experiment_repo.get_by_id(experiment_id)
        
        if not experiment:
            self.ui.infoText.setText('Эксперимент не найден')
            return
        
        info_lines = [
            f'ID: {experiment.id}',
            f'Первое вещество: {experiment.first_element}',
            f'Второе вещество: {experiment.second_element}',
            f'Температура: {experiment.temperature if experiment.temperature else "-"}',
            f'Давление: {experiment.pressure if experiment.pressure else "-"}',
            f'Тип процесса: {"ИЗОБАРНЫЙ" if experiment.is_isobaric else "ИЗОТЕРМИЧЕСКИЙ"}',
            ''
        ]
        
        if experiment.article_id:
            article = self.article_repo.get_by_id(experiment.article_id)
            if article:
                info_lines.extend([
                    'Статья:',
                    f'  Название: {article.name}',
                    f'  Автор: {article.author}',
                    f'  Год: {article.year}',
                    f'  Ссылка: {article.link}',
                    ''
                ])
        
        info_lines.append('Данные эксперимента:')
        for key, values in experiment.source_data.items():
            info_lines.append(f'  {key}: {len(values)} точек')
        
        self.ui.infoText.setText('\n'.join(info_lines))