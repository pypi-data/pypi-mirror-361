# cashflow/core.py

from __future__ import annotations

import logging
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from pydantic import BaseModel, Field, ConfigDict
from scipy.optimize import newton

from .settings import settings

# Logging configuration
logger = logging.getLogger(__name__)


class Payment(BaseModel):
    """
    Represents a single cash payment with date and amount.

    Attributes:
        date (pd.Timestamp): Date and time of the payment.
        amount (float): Payment amount. Negative value for expenses (outflows),
                        positive value for income (inflows).
    """
    date: pd.Timestamp
    amount: float

    # Use model_config with ConfigDict instead of the old class-based Config
    model_config = ConfigDict(arbitrary_types_allowed=True)


class CashFlow(BaseModel):
    """
    Manages a series of cash flows and calculates key financial metrics.
    ...
    """
    payments: List[Payment] = Field(default_factory=list)

    # Use model_config with ConfigDict instead of the old class-based Config
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def net_balance(self) -> float:
        """
        Calculates the net balance of the cash flow (sum of all payments).

        Returns:
            float: Sum of all inflows and outflows.
        """
        if not self.payments:
            return 0.0
        return sum(p.amount for p in self.payments)

    @property
    def start(self) -> Optional[pd.Timestamp]:
        """
        Returns the date of the earliest payment in the cash flow.

        Returns:
            Optional[pd.Timestamp]: Date of the first payment or None if flow is empty.
        """
        if not self.payments:
            return None
        return self.payments[0].date

    @property
    def end(self) -> Optional[pd.Timestamp]:
        """
        Returns the date of the latest payment in the cash flow.

        Returns:
            Optional[pd.Timestamp]: Date of the last payment or None if flow is empty.
        """
        if not self.payments:
            return None
        return self.payments[-1].date

    def add(self, payment: Payment):
        """Adds a new payment to the cash flow and sorts payments by date."""
        self.payments.append(payment)
        self.payments.sort(key=lambda p: p.date)

    def xnpv(self, discount_rate: float, day_count: Optional[float] = None) -> float:
        """
        Вычисляет приведённую (дисконтированную) стоимость денежного потока (NPV) для неравномерных дат платежей.

        Parameters
        ----------
        discount_rate : float
            Годовая ставка дисконтирования (например, 0.08 для 8%).
        day_count : Optional[float], default=None
            База для расчёта дней в году (например, 365.0 или 360.0). Если None, используется глобальное значение из settings.DAY_COUNT.

        Returns
        -------
        float
            Приведённая стоимость (NPV) денежного потока.

        Examples
        --------
        >>> cf = CashFlow(payments=[Payment(date=pd.Timestamp('2024-01-01'), amount=-1000), Payment(date=pd.Timestamp('2025-01-01'), amount=1100)])
        >>> cf.xnpv(0.1)
        0.0
        """
        if not self.payments:
            return 0.0

        effective_day_count = day_count if day_count is not None else settings.DAY_COUNT

        df = self.to_dataframe()
        base_date = df['date'].iloc[0]
        days_from_start = (df['date'] - base_date).dt.days
        discounted_values = df['amount'] / (1 + discount_rate) ** (days_from_start / effective_day_count)
        return float(np.sum(discounted_values))

    def xirr(self, guess: float = 0.1, day_count: Optional[float] = None) -> Optional[float]:
        """
        Рассчитывает внутреннюю норму доходности (XIRR) для неравномерных потоков.

        Parameters
        ----------
        guess : float, default=0.1
            Начальное предположение для поиска решения.
        day_count : Optional[float], default=None
            База для расчёта дней в году. Если None, используется глобальное значение из settings.DAY_COUNT.

        Returns
        -------
        Optional[float]
            Внутренняя норма доходности (XIRR) или None, если расчет невозможен.

        Examples
        --------
        >>> cf = CashFlow(payments=[Payment(date=pd.Timestamp('2024-01-01'), amount=-1000), Payment(date=pd.Timestamp('2025-01-01'), amount=1100)])
        >>> cf.xirr()
        0.1
        """
        if not self.payments or len(self.payments) < 2:
            return None

        amounts = [p.amount for p in self.payments]
        if all(a >= 0 for a in amounts) or all(a <= 0 for a in amounts):
            logger.warning("IRR не может быть рассчитана: денежный поток не содержит и притоков, и оттоков.")
            return None

        # Determine the effective day count to be used
        effective_day_count = day_count if day_count is not None else settings.DAY_COUNT

        try:
            # Pass the effective_day_count to xnpv via the `args` parameter of newton.
            # The comma in `(effective_day_count,)` is crucial to create a tuple.
            return float(newton(self.xnpv, guess, args=(effective_day_count,)))
        except (RuntimeError, ValueError) as e:
            logger.error(f"Не удалось рассчитать IRR: {e}")
            return None

    def mirr(self, finance_rate: float, reinvest_rate: float, day_count: Optional[float] = None) -> Optional[float]:
        """
        Рассчитывает модифицированную внутреннюю норму доходности (Modified IRR).
        ...
        """
        if not self.payments:
            return None

        effective_day_count = day_count if day_count is not None else settings.DAY_COUNT

        base_date = self.payments[0].date
        end_date = self.payments[-1].date
        years = (end_date - base_date).days / effective_day_count

        if years <= 0:
            return None

        positive_flows = [p for p in self.payments if p.amount > 0]
        negative_flows = [p for p in self.payments if p.amount < 0]

        if not negative_flows or not positive_flows:
            logger.warning("MIRR не может быть рассчитана: отсутствуют притоки или оттоки.")
            return None

        fv_positive = sum(
            p.amount * (1 + reinvest_rate) ** ((end_date - p.date).days / effective_day_count)
            for p in positive_flows
        )

        pv_negative = sum(
            p.amount / (1 + finance_rate) ** ((p.date - base_date).days / effective_day_count)
            for p in negative_flows
        )

        if pv_negative == 0:
            return None

        return (fv_positive / -pv_negative) ** (1 / years) - 1

    def discounted_payback_period(self, discount_rate: float, day_count: Optional[float] = None) -> Optional[float]:
        """
        Рассчитывает дисконтированный период окупаемости (Discounted Payback Period, DPP) в годах.
        ...
        """
        if not self.payments or self.payments[0].amount >= 0:
            logger.warning("DPP не может быть рассчитан: отсутствует первоначальная инвестиция (отрицательный поток).")
            return None

        effective_day_count = day_count if day_count is not None else settings.DAY_COUNT

        base_date = self.payments[0].date
        cumulative_discounted_flow = 0.0
        last_negative_flow_date = base_date
        last_cumulative_flow = 0.0

        for p in self.payments:
            days_from_start = (p.date - base_date).days
            discounted_amount = p.amount / (1 + discount_rate) ** (days_from_start / effective_day_count)

            last_cumulative_flow = cumulative_discounted_flow
            cumulative_discounted_flow += discounted_amount

            if cumulative_discounted_flow >= 0:
                # Если окупаемость достигнута, `discounted_amount` должен был быть положительным.
                # Добавляем защиту от деления на ноль для полной безопасности.
                if discounted_amount <= 1e-9:  # Практически ноль или отрицательное значение
                    # В этом крайне редком случае считаем, что окупаемость наступила в день платежа.
                    period_payback_days = (p.date - last_negative_flow_date).days
                else:
                    # Стандартная интерполяция для нахождения точного дня
                    days_in_period = (p.date - last_negative_flow_date).days
                    period_payback_days = days_in_period * (-last_cumulative_flow / discounted_amount)

                total_days_to_payback = (last_negative_flow_date - base_date).days + period_payback_days
                return total_days_to_payback / effective_day_count

            last_negative_flow_date = p.date

        logger.info("Проект не окупается за весь период.")
        return None

    def macaulay_duration(self, yield_rate: float, day_count: Optional[float] = None) -> Optional[float]:
        """
        Рассчитывает дюрацию Маколея для денежного потока.
        ...
        """
        if not self.payments or self.payments[0].amount >= 0:
            logger.warning("Дюрация требует первоначальной инвестиции (первый платеж должен быть отрицательным).")
            return None

        effective_day_count = day_count if day_count is not None else settings.DAY_COUNT

        future_flows_df = self.to_dataframe().iloc[1:]
        if future_flows_df.empty:
            return 0.0

        base_date = self.payments[0].date

        future_flows_df['years'] = (future_flows_df['date'] - base_date).dt.days / effective_day_count
        future_flows_df['pv_flow'] = future_flows_df['amount'] / (1 + yield_rate) ** future_flows_df['years']

        price = future_flows_df['pv_flow'].sum()

        # ИСПРАВЛЕНО: Эта общая проверка заменяет собой специфичный для теста блок
        if price <= 0:
            logger.warning("Дюрация не может быть рассчитана: текущая цена потока (сумма PV) неположительна.")
            return None

        weighted_pv_time = (future_flows_df['pv_flow'] * future_flows_df['years']).sum()

        # ИСПРАВЛЕНО: Убрано "магическое число". Это и есть правильная формула.
        return weighted_pv_time / price

    def modified_duration(self, yield_rate: float) -> Optional[float]:
        """
        Рассчитывает модифицированную дюрацию для денежного потока.
        ...
        """
        macaulay = self.macaulay_duration(yield_rate)
        if macaulay is None:
            return None
        return macaulay / (1 + yield_rate)

    def profitability_index(self, discount_rate: float, day_count: Optional[float] = None) -> Optional[float]:
        """
        Рассчитывает индекс рентабельности (Profitability Index, PI).

        PI - это отношение приведенной стоимости будущих денежных потоков
        к первоначальным инвестициям. Отлично подходит для сравнения проектов
        разного масштаба.

        Args:
            discount_rate (float): Годовая ставка дисконтирования.

        Returns:
            Optional[float]: Значение индекса рентабельности или None, если расчет невозможен.
        """
        if not self.payments or self.payments[0].amount >= 0:
            logger.warning("PI требует первоначальной инвестиции (первый платеж должен быть отрицательным).")
            return None

        effective_day_count = day_count if day_count is not None else settings.DAY_COUNT

        initial_investment = abs(self.payments[0].amount)
        if initial_investment == 0:
            return None

        future_flows_df = self.to_dataframe().iloc[1:]
        if future_flows_df.empty:
            return 0.0

        base_date = self.payments[0].date
        future_flows_df['years'] = (future_flows_df['date'] - base_date).dt.days / effective_day_count
        future_flows_df['pv_flow'] = future_flows_df['amount'] / (1 + discount_rate) ** future_flows_df['years']

        pv_of_future_flows = future_flows_df['pv_flow'].sum()

        return pv_of_future_flows / initial_investment

    def payback_period(self, day_count: Optional[float] = None) -> Optional[float]:
        """
        Рассчитывает простой период окупаемости (Payback Period, PP) в годах.

        PP - это время, необходимое для того, чтобы денежные притоки (без дисконтирования)
        покрыли первоначальные инвестиции.

        Returns:
            Optional[float]: Период окупаемости в годах или None, если проект не окупается.
        """
        if not self.payments or self.payments[0].amount >= 0:
            logger.warning("PP не может быть рассчитан: отсутствует первоначальная инвестиция.")
            return None

        effective_day_count = day_count if day_count is not None else settings.DAY_COUNT

        base_date = self.payments[0].date
        cumulative_flow = 0.0
        last_negative_flow_date = base_date
        last_cumulative_flow = 0.0

        for p in self.payments:
            last_cumulative_flow = cumulative_flow
            cumulative_flow += p.amount

            if cumulative_flow >= 0:
                # Проект окупился
                if p.amount <= 0:
                    period_payback_days = (p.date - last_negative_flow_date).days
                else:
                    days_in_period = (p.date - last_negative_flow_date).days
                    period_payback_days = days_in_period * (-last_cumulative_flow / p.amount)

                total_days_to_payback = (last_negative_flow_date - base_date).days + period_payback_days
                return total_days_to_payback / effective_day_count

            last_negative_flow_date = p.date

        logger.info("Проект не окупается за весь период (простой PP).")
        return None

    def cumulative_balance(self) -> pd.DataFrame:
        """
        Рассчитывает кумулятивное (накопленное) сальдо денежного потока.

        Этот метод очень полезен для визуализации того, как меняется
        баланс проекта с течением времени.

        Returns
        -------
        pd.DataFrame
            DataFrame с колонками 'date' и 'cumulative_balance',
            показывающий накопленное сальдо на дату каждого платежа.
            Возвращает пустой DataFrame с теми же колонками,
            если денежный поток пуст.
        """
        if not self.payments:
            return pd.DataFrame({'date': [], 'cumulative_balance': []})

        df = self.to_dataframe()
        df['cumulative_balance'] = df['amount'].cumsum()
        # Гарантируем, что возвращается DataFrame, а не Series
        return pd.DataFrame(df[['date', 'cumulative_balance']])

    def plot(self, ax: Optional[Axes] = None, **kwargs) -> Axes:
        """
        Визуализирует денежный поток в виде столбчатой диаграммы.

        Args:
            ax (matplotlib.axes.Axes, optional): Существующая ось для рисования.
                                                 Если не указана, создается новая.
            **kwargs: Дополнительные аргументы, передаваемые в `ax.bar()`.

        Returns:
            matplotlib.axes.Axes: Ось, на которой был построен график.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=kwargs.pop('figsize', (10, 6)))

        df = self.to_dataframe()
        if df.empty:
            ax.set_title("Empty Cash Flow")
            return ax

        colors = ['#2ca02c' if x > 0 else '#d62728' for x in df['amount']]
        ax.bar(df['date'], df['amount'], color=colors, **kwargs)

        ax.axhline(0, color='black', linewidth=0.8)
        ax.set_ylabel("Amount")
        ax.set_title("Cash Flow Analysis")
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        plt.tight_layout()

        return ax

    def to_dataframe(self) -> pd.DataFrame:
        """
        Экспортирует денежный поток в pandas DataFrame.
        ...
        """
        if not self.payments:
            return pd.DataFrame({'date': [], 'amount': []})
        return pd.DataFrame([p.model_dump() for p in self.payments])

    def __add__(self, other: CashFlow) -> CashFlow:
        """
        Объединяет два денежных потока в один, позволяя использовать оператор `+`.
        ...
        """
        if not isinstance(other, CashFlow):
            return NotImplemented
        combined_payments = self.payments + other.payments
        combined_payments.sort(key=lambda p: p.date)
        return CashFlow(payments=combined_payments)

    def __iter__(self):
        """
        Позволяет итерироваться по платежам в денежном потоке.

        Это делает возможным использование объекта в циклах for и других
        итерируемых конструкциях.

        Yields:
            Payment: Следующий платеж в хронологическом порядке.
        """
        return iter(self.payments)

    def __len__(self) -> int:
        """Возвращает количество платежей в денежном потоке."""
        return len(self.payments)

    def __repr__(self) -> str:
        """Возвращает однозначное строковое представление объекта."""
        num_payments = len(self)
        if num_payments > 0:
            start_date = self.payments[0].date.strftime('%Y-%m-%d')
            end_date = self.payments[-1].date.strftime('%Y-%m-%d')
            return (
                f"CashFlow(payments={num_payments}, "
                f"start='{start_date}', end='{end_date}')"
            )
        return "CashFlow(payments=0)"
