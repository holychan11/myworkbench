"""选股策略基类与注册表：可插拔，新增策略零侵入。"""
import importlib
import pkgutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class StockPick:
    code: str
    name: str
    target_price: float
    watch_period: str
    reasons: list[str]


@dataclass
class StrategyContext:
    trade_date: str
    extra: dict = field(default_factory=dict)


class ScreeningStrategy(ABC):
    id: str = "base"
    name: str = "基类策略"

    @abstractmethod
    def run(self, ctx: StrategyContext) -> list[StockPick]:
        """执行筛选，返回推荐清单。"""


_REGISTRY: dict[str, ScreeningStrategy] = {}


def register(cls):
    _REGISTRY[cls.id] = cls()
    return cls


def get_strategy(sid: str) -> ScreeningStrategy | None:
    return _REGISTRY.get(sid)


def all_strategies() -> dict[str, ScreeningStrategy]:
    return dict(_REGISTRY)


def discover(package: str = "app.stock.strategies") -> None:
    """扫描策略目录并注册（import 副作用触发 @register）。"""
    pkg = importlib.import_module(package)
    for m in pkgutil.iter_modules(pkg.__path__):
        importlib.import_module(f"{package}.{m.name}")
