# Архитектура проекта

## Обзор

Проект следует принципам **Clean Architecture** с чётким разделением на слои и минимальной связанностью между модулями.

## Структура проекта

```
Chemical-Calculations/
├── src/                          # Исходный код приложения
│   ├── core/                     # Ядро приложения
│   │   ├── config.py            # Конфигурация через Pydantic
│   │   └── __init__.py
│   │
│   ├── domain/                   # Доменный слой
│   │   ├── models.py            # Доменные модели (dataclasses)
│   │   └── __init__.py
│   │
│   ├── infrastructure/           # Инфраструктурный слой
│   │   ├── database.py          # Подключение к БД
│   │   ├── repositories.py      # Репозитории для работы с данными
│   │   └── __init__.py
│   │
│   ├── calculation/              # Математический слой
│   │   ├── function.py          # Математические функции
│   │   ├── optimizer.py         # Методы оптимизации
│   │   └── __init__.py
│   │
│   ├── services/                 # Слой бизнес-логики
│   │   ├── calculation_service.py
│   │   ├── search_service.py
│   │   ├── import_service.py
│   │   └── __init__.py
│   │
│   ├── ui/                       # Слой представления
│   │   ├── dialogs/             # Диалоговые окна
│   │   │   ├── import_dialog.py
│   │   │   ├── model_dialog.py
│   │   │   ├── experiment_info_dialog.py
│   │   │   └── __init__.py
│   │   ├── widgets/             # Виджеты
│   │   │   ├── calculation_widget.py
│   │   │   └── __init__.py
│   │   ├── main_window.py       # Главное окно
│   │   └── __init__.py
│   │
│   ├── main.py                   # Точка входа
│   └── __init__.py
│
├── ui/                           # UI файлы Qt Designer
├── db/                           # База данных SQLite
├── articles/                     # Экспериментальные данные
├── tests/                        # Тесты
├── .env.example                  # Пример конфигурации
├── setup.py                      # Установка пакета
├── pyproject.toml               # Конфигурация проекта
└── README.md                     # Документация
```

## Слои архитектуры

### 1. Core (Ядро)

**Назначение:** Конфигурация и общие утилиты

**Компоненты:**
- `config.py` - Настройки через Pydantic Settings

**Зависимости:** Нет

**Принципы:**
- Централизованная конфигурация
- Валидация параметров
- Поддержка .env файлов

### 2. Domain (Доменный слой)

**Назначение:** Бизнес-сущности без зависимостей

**Компоненты:**
- `models.py` - Доменные модели (Experiment, Model, Element, Article, Attempt)

**Зависимости:** Только стандартная библиотека

**Принципы:**
- Чистые dataclasses
- Бизнес-логика в свойствах
- Независимость от фреймворков

### 3. Infrastructure (Инфраструктурный слой)

**Назначение:** Работа с внешними системами (БД, файлы)

**Компоненты:**
- `database.py` - Управление подключениями к БД
- `repositories.py` - CRUD операции для каждой сущности

**Зависимости:** 
- Domain
- Core

**Принципы:**
- Паттерн Repository
- Контекстные менеджеры для БД
- Изоляция SQL от бизнес-логики

### 4. Calculation (Математический слой)

**Назначение:** Математические вычисления и оптимизация

**Компоненты:**
- `function.py` - Работа с математическими функциями
- `optimizer.py` - Методы оптимизации

**Зависимости:** Только математические библиотеки

**Принципы:**
- Чистая математика
- Кэширование производных
- Абстрактные базовые классы для методов

### 5. Services (Слой бизнес-логики)

**Назначение:** Координация между слоями

**Компоненты:**
- `calculation_service.py` - Оркестрация расчётов
- `search_service.py` - Поиск и фильтрация
- `import_service.py` - Импорт данных

**Зависимости:**
- Domain
- Infrastructure
- Calculation

**Принципы:**
- Фасад для сложных операций
- Координация между репозиториями
- Бизнес-логика приложения

### 6. UI (Слой представления)

**Назначение:** Пользовательский интерфейс

**Компоненты:**
- `main_window.py` - Главное окно
- `dialogs/` - Диалоговые окна
- `widgets/` - Переиспользуемые виджеты

**Зависимости:**
- Services
- Infrastructure (только репозитории)

**Принципы:**
- Минимум логики в UI
- Делегирование сервисам
- Разделение на компоненты

## Потоки данных

### Чтение данных

```
UI → Service → Repository → Database
                ↓
            Domain Model
```

### Запись данных

```
UI → Service → Repository → Database
      ↑
  Domain Model
```

### Расчёты

```
UI → CalculationService → Optimizer → MathFunction
      ↓                      ↓
  Repository            Pure Math
```

## Паттерны проектирования

### Repository Pattern
Изоляция логики доступа к данным

```python
class ExperimentRepository:
    def get_all(self) -> List[Experiment]
    def get_by_id(self, id: int) -> Optional[Experiment]
    def create(self, experiment: Experiment) -> int
```

### Service Layer
Координация бизнес-логики

```python
class CalculationService:
    def __init__(self):
        self.experiment_repo = ExperimentRepository()
    
    def optimize(self, experiment_id, model, method_id, params):
        experiment = self.experiment_repo.get_by_id(experiment_id)
        # бизнес-логика
```

### Strategy Pattern
Различные методы оптимизации

```python
class OptimizationMethod(ABC):
    @abstractmethod
    def optimize(self, initial_params): pass

class SimulatedAnnealing(OptimizationMethod):
    def optimize(self, initial_params): ...
```

### Dependency Injection
Внедрение зависимостей через конструктор

```python
class MainWindow:
    def __init__(self):
        self.calc_service = CalculationService()
        self.experiment_repo = ExperimentRepository()
```

## Принципы SOLID

### Single Responsibility
Каждый класс отвечает за одну задачу

### Open/Closed
Легко добавлять новые методы оптимизации без изменения существующего кода

### Liskov Substitution
Все методы оптимизации взаимозаменяемы

### Interface Segregation
Репозитории имеют только нужные методы

### Dependency Inversion
Зависимость от абстракций, а не конкретных реализаций

## Преимущества архитектуры

### Тестируемость
- Легко мокировать зависимости
- Изолированные unit-тесты
- Независимые слои

### Поддерживаемость
- Чёткое разделение ответственности
- Легко найти нужный код
- Минимум дублирования

### Расширяемость
- Легко добавлять новые функции
- Не ломается существующий код
- Модульная структура

### Производительность
- Кэширование на уровне функций
- Эффективная работа с БД
- Оптимизированные вычисления

## Рекомендации по разработке

### Добавление нового метода оптимизации

1. Создать класс в `calculation/optimizer.py`:
```python
class NewMethod(OptimizationMethod):
    def optimize(self, initial_params, **kwargs):
        # реализация
```

2. Добавить в словарь методов:
```python
OPTIMIZATION_METHODS = {
    5: NewMethod,
}
```

### Добавление новой сущности

1. Создать модель в `domain/models.py`
2. Создать репозиторий в `infrastructure/repositories.py`
3. При необходимости создать сервис в `services/`
4. Добавить UI в `ui/`

### Изменение источника данных

Достаточно изменить только `infrastructure/database.py` и `infrastructure/repositories.py`

## Безопасность

- Параметризованные SQL запросы
- Валидация входных данных через Pydantic
- Безопасное хранение паролей в .env
- Контекстные менеджеры для БД

## Производительность

- Кэширование производных функций
- Эффективные SQL запросы
- Минимум обращений к БД
- Оптимизированные математические операции