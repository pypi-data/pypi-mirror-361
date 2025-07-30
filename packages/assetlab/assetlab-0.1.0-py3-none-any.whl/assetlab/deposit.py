# assetlab/deposit.py

from __future__ import annotations
from typing import List, Optional, Tuple

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict, model_validator

from .cashflow import CashFlow, Payment
from .settings import settings


class Deposit(BaseModel):
    """
    Представляет банковский депозит с поддержкой пополнений, снятий,
    капитализации или регулярных выплат процентов.

    Parameters
    ----------
    principal : float
        Первоначальная сумма вклада (должна быть положительной).
    annual_rate : float
        Годовая процентная ставка (должна быть неотрицательной).
    start_date : pd.Timestamp
        Дата начала депозита.
    end_date : pd.Timestamp
        Дата окончания депозита.
    interest_frequency : int, default=1
        Частота начисления/выплаты процентов в год (1: ежегодно, 4: ежеквартально, 12: ежемесячно).
    payout_interest : bool, default=False
        Если True, проценты выплачиваются, а не капитализируются.
    replenishments : Optional[List[Payment]], default=None
        Список пополнений вклада (положительные суммы).
    withdrawals : Optional[List[Payment]], default=None
        Список частичных снятий (положительные суммы).

    Examples
    --------
    >>> from assetlab import Deposit, Payment
    >>> import pandas as pd
    >>> deposit = Deposit(
    ...     principal=100000,
    ...     annual_rate=0.08,
    ...     start_date=pd.Timestamp('2024-01-01'),
    ...     end_date=pd.Timestamp('2026-01-01'),
    ...     compounding_frequency=4
    ... )
    >>> deposit.final_value()
    117191.37
    """
    principal: float = Field(gt=0, description="Первоначальная сумма вклада.")
    annual_rate: float = Field(ge=0, description="Годовая процентная ставка.")
    start_date: pd.Timestamp
    end_date: pd.Timestamp

    interest_frequency: int = Field(
        default=1,
        gt=0,
        description="Частота начисления/выплаты процентов в год (1: ежегодно, 12: ежемесячно)."
    )
    payout_interest: bool = Field(
        default=False,
        description="Если True, проценты выплачиваются, а не капитализируются."
    )
    replenishments: Optional[List[Payment]] = Field(
        default=None,
        description="Список пополнений вклада (положительные суммы)."
    )
    withdrawals: Optional[List[Payment]] = Field(
        default=None,
        description="Список частичных снятий (положительные суммы)."
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode='after')
    def check_dates(self) -> 'Deposit':
        """Проверяет, что даты пополнений и снятий находятся в пределах срока вклада."""
        for event_list in [self.replenishments, self.withdrawals]:
            if event_list:
                for event in event_list:
                    if not (self.start_date <= event.date <= self.end_date):
                        raise ValueError(f"Дата события {event} выходит за рамки срока вклада.")
        return self

    def _process_timeline(self, day_count: Optional[float] = None) -> Tuple[float, float, List[Payment]]:
        """
        Основной движок расчета, который делегирует вычисления
        специализированным методам в зависимости от типа депозита.
        """
        if self.payout_interest:
            return self._calculate_payout(day_count)
        else:
            return self._calculate_capitalizing(day_count)

    def _calculate_capitalizing(self, day_count: Optional[float] = None) -> Tuple[float, float, List[Payment]]:
        """Расчет для депозита с капитализацией процентов."""
        effective_day_count = day_count if day_count is not None else settings.DAY_COUNT
        rate_per_period = self.annual_rate / self.interest_frequency

        all_flows = [Payment(date=self.start_date, amount=self.principal)]
        if self.replenishments:
            all_flows.extend(self.replenishments)
        if self.withdrawals:
            all_flows.extend([Payment(date=w.date, amount=-w.amount) for w in self.withdrawals])

        final_balance = 0.0
        total_invested = 0.0
        for flow in all_flows:
            t_years = (self.end_date - flow.date).days / effective_day_count
            num_periods = self.interest_frequency * t_years
            final_balance += flow.amount * (1 + rate_per_period) ** num_periods
            if flow.amount > 0:
                total_invested += flow.amount

        total_interest = final_balance - total_invested + sum(w.amount for w in self.withdrawals or [])
        return final_balance, total_interest, []

    # ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ: Полностью переработанная и более точная логика для выплат
    def _calculate_payout(self, day_count: Optional[float] = None) -> Tuple[float, float, List[Payment]]:
        """Расчет для депозита с выплатой процентов."""
        effective_day_count = day_count if day_count is not None else settings.DAY_COUNT

        # 1. Собираем все движения основного тела долга
        principal_events = [Payment(date=self.start_date, amount=self.principal)]
        if self.replenishments:
            principal_events.extend(self.replenishments)
        if self.withdrawals:
            principal_events.extend([Payment(date=w.date, amount=-w.amount) for w in self.withdrawals])

        # 2. Генерируем даты выплаты процентов
        freq_map = {1: 'YE', 4: 'QE', 12: 'ME'}  # ИСПРАВЛЕНО: 'A' -> 'YE' и т.д.
        freq_code = freq_map.get(self.interest_frequency)
        if not freq_code:
            raise ValueError(f"Неподдерживаемая частота выплат: {self.interest_frequency}")

        interest_dates = pd.date_range(start=self.start_date, end=self.end_date, freq=freq_code)

        # 3. Создаем единую временную шкалу всех событий
        timeline_dates = {self.start_date, self.end_date}
        for event in principal_events:
            timeline_dates.add(event.date)
        for d in interest_dates:
            timeline_dates.add(d)

        sorted_timeline = sorted(list(timeline_dates))

        # 4. Итерируемся по временной шкале, рассчитывая проценты и обновляя баланс
        balance = 0.0
        total_interest = 0.0
        interest_payouts = []

        for i in range(len(sorted_timeline) - 1):
            start_interval = sorted_timeline[i]
            end_interval = sorted_timeline[i + 1]

            # Обновляем баланс в начале интервала
            for event in principal_events:
                if event.date == start_interval:
                    balance += event.amount

            # Рассчитываем проценты за интервал
            period_days = (end_interval - start_interval).days
            if period_days > 0:
                interest_accrued = balance * self.annual_rate * (period_days / effective_day_count)
                total_interest += interest_accrued

                # Если конец интервала - это дата выплаты, создаем платеж
                if end_interval in interest_dates:
                    interest_payouts.append(Payment(date=end_interval, amount=interest_accrued))

        # Обновляем баланс последним событием, если оно на end_date
        for event in principal_events:
            if event.date == self.end_date:
                balance += event.amount

        return balance, total_interest, interest_payouts

    def final_value(self, day_count: Optional[float] = None) -> float:
        """
        Рассчитывает итоговую сумму на счете депозита.

        Parameters
        ----------
        day_count : Optional[float], default=None
            База для расчёта дней в году. Если None, используется глобальное значение из settings.DAY_COUNT.

        Returns
        -------
        float
            Итоговая сумма на счете депозита.

        Examples
        --------
        >>> deposit = Deposit(principal=100000, annual_rate=0.08, 
        ...                  start_date=pd.Timestamp('2024-01-01'), 
        ...                  end_date=pd.Timestamp('2025-01-01'))
        >>> deposit.final_value()
        108000.0
        """
        final_balance, _, _ = self._process_timeline(day_count)
        return final_balance

    def total_interest(self, day_count: Optional[float] = None) -> float:
        """
        Рассчитывает общую сумму начисленных процентов.

        Parameters
        ----------
        day_count : Optional[float], default=None
            База для расчёта дней в году. Если None, используется глобальное значение из settings.DAY_COUNT.

        Returns
        -------
        float
            Сумма начисленных процентов.

        Examples
        --------
        >>> deposit = Deposit(principal=100000, annual_rate=0.08, 
        ...                  start_date=pd.Timestamp('2024-01-01'), 
        ...                  end_date=pd.Timestamp('2025-01-01'))
        >>> deposit.total_interest()
        8000.0
        """
        _, total_interest_earned, _ = self._process_timeline(day_count)
        return total_interest_earned

    def to_cashflow(self, day_count: Optional[float] = None) -> CashFlow:
        """
        Преобразует депозит в денежный поток для дальнейшего анализа.

        Parameters
        ----------
        day_count : Optional[float], default=None
            База для расчёта дней в году. Если None, используется глобальное значение из settings.DAY_COUNT.

        Returns
        -------
        CashFlow
            Денежный поток, представляющий депозит.

        Examples
        --------
        >>> deposit = Deposit(principal=100000, annual_rate=0.08, 
        ...                  start_date=pd.Timestamp('2024-01-01'), 
        ...                  end_date=pd.Timestamp('2025-01-01'))
        >>> cf = deposit.to_cashflow()
        >>> cf.xirr()
        0.08
        """
        final_balance, _, interest_payouts = self._process_timeline(day_count)

        payments = [Payment(date=self.start_date, amount=-self.principal)]
        if self.replenishments:
            payments.extend([Payment(date=p.date, amount=-p.amount) for p in self.replenishments])
        if self.withdrawals:
            payments.extend(self.withdrawals)

        payments.extend(interest_payouts)
        payments.append(Payment(date=self.end_date, amount=final_balance))

        return CashFlow(payments=payments)

    def __repr__(self) -> str:
        parts = [
            f"principal={self.principal:,.2f}",
            f"rate={self.annual_rate:.2%}",
            f"start='{self.start_date.strftime('%Y-%m-%d')}'",
            f"end='{self.end_date.strftime('%Y-%m-%d')}'"
        ]
        if self.payout_interest:
            parts.append("payout_interest=True")
        if self.replenishments:
            parts.append(f"replenishments={len(self.replenishments)}")
        if self.withdrawals:
            parts.append(f"withdrawals={len(self.withdrawals)}")

        return f"Deposit({', '.join(parts)})"
