import json
from typing import Dict, List, Optional

from domain.models import Article, Attempt, Element, Experiment, Model
from infrastructure.database import db_connection


class BaseRepository:
    def __init__(self):
        self.db = db_connection

    def _row_to_dict(self, row) -> Dict:
        if hasattr(row, 'keys'):
            return {key: row[key] for key in row.keys()}
        return dict(row)


class ExperimentRepository(BaseRepository):
    def get_all(self) -> List[Experiment]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM experiments')
            rows = cursor.fetchall()
            return [self._row_to_experiment(row) for row in rows]

    def get_by_id(self, experiment_id: int) -> Optional[Experiment]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM experiments WHERE id = ?', (experiment_id,))
            row = cursor.fetchone()
            return self._row_to_experiment(row) if row else None

    def create(self, experiment: Experiment) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            source_data_json = json.dumps(experiment.source_data)
            cursor.execute(
                '''INSERT INTO experiments 
                   (first_element, second_element, temperature, pressure, source_data, article) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (experiment.first_element, experiment.second_element, 
                 experiment.temperature, experiment.pressure, 
                 source_data_json, experiment.article_id)
            )
            return cursor.lastrowid

    def delete(self, experiment_id: int) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM experiments WHERE id = ?', (experiment_id,))

    def filter_by_elements(self, first_elements: List[str], second_elements: List[str]) -> List[Experiment]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            placeholders_first = ','.join(['?'] * len(first_elements))
            placeholders_second = ','.join(['?'] * len(second_elements))
            query = f'''SELECT * FROM experiments 
                       WHERE first_element IN ({placeholders_first}) 
                       OR second_element IN ({placeholders_second})'''
            cursor.execute(query, tuple(first_elements) + tuple(second_elements))
            rows = cursor.fetchall()
            return [self._row_to_experiment(row) for row in rows]

    def _row_to_experiment(self, row) -> Experiment:
        data = self._row_to_dict(row)
        return Experiment(
            id=data['id'],
            first_element=data['first_element'],
            second_element=data['second_element'],
            temperature=data.get('temperature'),
            pressure=data.get('pressure'),
            source_data=json.loads(data['source_data']) if data.get('source_data') else {},
            article_id=data.get('article')
        )


class ElementRepository(BaseRepository):
    def get_all(self) -> List[Element]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM elements')
            rows = cursor.fetchall()
            return [self._row_to_element(row) for row in rows]

    def get_by_name(self, name: str) -> Optional[Element]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM elements WHERE name = ?', (name,))
            row = cursor.fetchone()
            return self._row_to_element(row) if row else None

    def create(self, element: Element) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO elements (name, branch) VALUES (?, ?)',
                (element.name, element.branch)
            )
            return cursor.lastrowid

    def _row_to_element(self, row) -> Element:
        data = self._row_to_dict(row)
        return Element(
            id=data['id'],
            name=data['name'],
            branch=data.get('branch', '')
        )


class ModelRepository(BaseRepository):
    def get_all(self) -> List[Model]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM models ORDER BY name')
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]

    def get_by_id(self, model_id: int) -> Optional[Model]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM models WHERE id = ?', (model_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def get_by_name(self, name: str) -> Optional[Model]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM models WHERE name = ?', (name,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def create(self, model: Model) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            initial_data_json = json.dumps(model.initial_data)
            cursor.execute(
                '''INSERT INTO models 
                   (name, equation, initial_data, calculated_parameter, argument) 
                   VALUES (?, ?, ?, ?, ?)''',
                (model.name, model.equation, initial_data_json, 
                 model.calculated_parameter, model.argument)
            )
            return cursor.lastrowid

    def update(self, model: Model) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            initial_data_json = json.dumps(model.initial_data)
            cursor.execute(
                '''UPDATE models 
                   SET name = ?, equation = ?, initial_data = ?, 
                       calculated_parameter = ?, argument = ? 
                   WHERE id = ?''',
                (model.name, model.equation, initial_data_json,
                 model.calculated_parameter, model.argument, model.id)
            )

    def _row_to_model(self, row) -> Model:
        data = self._row_to_dict(row)
        return Model(
            id=data['id'],
            name=data['name'],
            equation=data['equation'],
            initial_data=json.loads(data['initial_data']) if data.get('initial_data') else {},
            calculated_parameter=data.get('calculated_parameter', ''),
            argument=data.get('argument', '')
        )


class ArticleRepository(BaseRepository):
    def get_all(self) -> List[Article]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM articles')
            rows = cursor.fetchall()
            return [self._row_to_article(row) for row in rows]

    def get_by_id(self, article_id: int) -> Optional[Article]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
            row = cursor.fetchone()
            return self._row_to_article(row) if row else None

    def create(self, article: Article) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO articles (name, author, year, link) VALUES (?, ?, ?, ?)',
                (article.name, article.author, article.year, article.link)
            )
            return cursor.lastrowid

    def delete(self, article_id: int) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))

    def _row_to_article(self, row) -> Article:
        data = self._row_to_dict(row)
        return Article(
            id=data['id'],
            name=data['name'],
            author=data['author'],
            year=data.get('year'),
            link=data.get('link', '')
        )


class AttemptRepository(BaseRepository):
    def create(self, attempt: Attempt) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            init_data_json = json.dumps(attempt.init_data)
            result_data_json = json.dumps(attempt.result_data)
            cursor.execute(
                '''INSERT INTO attempts 
                   (experiment_id, method_id, init_data, result) 
                   VALUES (?, ?, ?, ?)''',
                (attempt.experiment_id, attempt.method_id, 
                 init_data_json, result_data_json)
            )
            return cursor.lastrowid