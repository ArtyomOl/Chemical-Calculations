from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Experiment:
    id: Optional[int] = None
    first_element: str = ''
    second_element: str = ''
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    source_data: Dict[str, List[float]] = field(default_factory=dict)
    article_id: Optional[int] = None

    @property
    def is_isobaric(self) -> bool:
        return self.temperature is None

    @property
    def is_isothermal(self) -> bool:
        return self.temperature is not None


@dataclass
class Element:
    id: Optional[int] = None
    name: str = ''
    branch: str = ''

    @property
    def branches(self) -> List[str]:
        return [b for b in self.branch.split(';') if b]


@dataclass
class Model:
    id: Optional[int] = None
    name: str = ''
    equation: str = ''
    initial_data: Dict[str, float] = field(default_factory=dict)
    calculated_parameter: str = ''
    argument: str = ''


@dataclass
class Article:
    id: Optional[int] = None
    name: str = ''
    author: str = ''
    year: Optional[int] = None
    link: str = ''


@dataclass
class Attempt:
    id: Optional[int] = None
    experiment_id: int = 0
    model_id: Optional[int] = None
    method_id: int = 0
    init_data: Dict[str, Any] = field(default_factory=dict)
    result_data: Dict[str, Any] = field(default_factory=dict)