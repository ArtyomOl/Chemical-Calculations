# Миграция на новую архитектуру

## Изменения в структуре проекта

### Старая структура → Новая структура

```
foundation/basis.py     → src/domain/models.py + src/infrastructure/repositories.py
storage/db.py           → src/infrastructure/database.py
storage/from_file_imports.py → src/services/import_service.py
maths/functions.py      → src/calculation/function.py
maths/methods.py        → src/calculation/optimizer.py
maths/calc.py           → src/services/calculation_service.py
search/search.py        → src/services/search_service.py
screens/mainWindow.py   → src/ui/main_window.py
screens/attemptWidget.py → src/ui/widgets/calculation_widget.py
config/config.py        → src/core/config.py + .env
```

## Ключевые улучшения

### 1. Конфигурация

**Было:**
```python
from config import config
connection_type = config.connection_type
```

**Стало:**
```python
from src.core.config import settings
db_type = settings.db_type
```

Конфигурация теперь через `.env` файл и Pydantic Settings.

### 2. Работа с БД

**Было:**
```python
connection = create_connection()  # Глобальное соединение
cursor = connection.cursor()
```

**Стало:**
```python
from src.infrastructure.database import db_connection

with db_connection.get_connection() as conn:
    cursor = conn.cursor()
    # работа с БД
```

Использование контекстных менеджеров для безопасной работы с БД.

### 3. Доменные модели

**Было:**
```python
class Experiment:
    def __init__(self, first_element, second_element, ...):
        self.first_element = first_element
        # ...
    
    def addIntoDB(self):
        # SQL запросы внутри модели
```

**Стало:**
```python
@dataclass
class Experiment:
    first_element: str
    second_element: str
    # ...

# Отдельный репозиторий
experiment_repo = ExperimentRepository()
experiment_repo.create(experiment)
```

Разделение данных и логики работы с БД.

### 4. Математические вычисления

**Было:**
```python
class Method(abc.ABC):
    def __init__(self, id_exp, used_function):
        self.experiment_data = foundation.basis.getExperimentAsID(id_exp)
        # Смешение логики
```

**Стало:**
```python
class OptimizationMethod(ABC):
    def __init__(self, func: MathFunction, data: List[Tuple], temperature: float):
        self.func = func
        self.data = data
        # Чистая математика без зависимостей от БД
```

### 5. UI и бизнес-логика

**Было:**
```python
class MainWindow(QMainWindow):
    def calculateButton_clicked(self):
        # SQL запросы
        # Математические вычисления
        # Обновление UI
        # Всё в одном методе
```

**Стало:**
```python
class MainWindow(QMainWindow):
    def __init__(self):
        self.calc_service = CalculationService()
        self.experiment_repo = ExperimentRepository()
    
    def _on_calculate(self):
        result = self.calc_service.optimize(...)
        self._display_results(result)
```

Разделение UI и бизнес-логики через сервисы.

## Шаги миграции

### 1. Установка новых зависимостей

```bash
pip install pydantic pydantic-settings
```

### 2. Создание .env файла

```bash
cp .env.example .env
# Отредактируйте .env под свои нужды
```

### 3. Обновление импортов

Замените старые импорты на новые:

```python
# Старое
from foundation.basis import Experiment, getAllElements
from storage.db import create_connection
from maths.methods import MethodOfSimulatedAnnealing

# Новое
from src.domain.models import Experiment
from src.infrastructure.repositories import ExperimentRepository
from src.calculation.optimizer import SimulatedAnnealing
```

### 4. Запуск приложения

```bash
# Старый способ
python main.py

# Новый способ
python -m src.main
# или
chem-calc
```

## Преимущества новой архитектуры

### Разделение ответственности
- Каждый модуль отвечает за одну задачу
- Легче тестировать и поддерживать

### Отсутствие глобального состояния
- Нет глобальных соединений с БД
- Безопасная работа в многопоточной среде

### Типизация
- Использование dataclasses и type hints
- Лучшая поддержка IDE

### Конфигурация
- Централизованная через .env
- Валидация через Pydantic
- Безопасное хранение секретов

### Тестируемость
- Легко мокировать зависимости
- Изолированные unit-тесты

### Расширяемость
- Легко добавлять новые методы оптимизации
- Простое добавление новых источников данных

## Обратная совместимость

Старые модули остаются в проекте для обратной совместимости, но помечены как deprecated. Рекомендуется постепенно мигрировать на новую архитектуру.

## Поддержка

При возникновении проблем с миграцией создайте Issue в репозитории.