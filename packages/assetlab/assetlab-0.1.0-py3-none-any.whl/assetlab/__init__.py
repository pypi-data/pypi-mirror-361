# assetlab/__init__.py

from .cashflow import Payment, CashFlow
from .deposit import Deposit
from .bond import Bond, FloatingRateConfig
from . import settings

# Определяем, что будет импортировано при `from assetlab import *`
# и что будет видно для автодополнения в IDE
__all__ = [
    "Payment",
    "CashFlow",
    "Deposit",
    "Bond",
    "FloatingRateConfig",
    "settings"  # <-- Добавляем settings в экспорт
]
