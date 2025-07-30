from __future__ import annotations
from typing import List, Optional, Literal, Union, Callable, Dict, Any
import pandas as pd
from pydantic import BaseModel, Field, ConfigDict, model_validator
from .cashflow import CashFlow, Payment
from .settings import settings

class FloatingRateConfig(BaseModel):
    """
    Конфигурация для плавающей ставки облигации.

    Parameters
    ----------
    base_rate : Union[float, List[float], Callable[[pd.Timestamp], float]]
        Базовая ставка. Может быть фиксированной (float), списком ставок (List[float]) 
        или функцией от даты (Callable[[pd.Timestamp], float]).
    spread : float, default=0.0
        Спред к базовой ставке (дополнительная надбавка).
    cap : Optional[float], default=None
        Максимальная ставка (кап). Если None, ограничения нет.
    floor : Optional[float], default=None
        Минимальная ставка (флор). Если None, ограничения нет.
    reset_frequency : Optional[int], default=None
        Частота пересмотра ставки в год.

    Examples
    --------
    >>> from assetlab import FloatingRateConfig
    >>> # Fixed base rate
    >>> config = FloatingRateConfig(base_rate=0.05, spread=0.02, cap=0.10)
    >>> # List of rates
    >>> config = FloatingRateConfig(base_rate=[0.04, 0.05, 0.06], spread=0.01)
    >>> # Function of date
    >>> def rate_func(date): return 0.03 + 0.01 * (date.year - 2024)
    >>> config = FloatingRateConfig(base_rate=rate_func, spread=0.015)
    """
    base_rate: Union[float, List[float], Callable[[pd.Timestamp], float]] = Field(
        ..., description="Base rate (fixed, list, or function)"
    )
    spread: float = Field(default=0.0, description="Spread to base rate")
    cap: Optional[float] = Field(default=None, description="Maximum rate (cap)")
    floor: Optional[float] = Field(default=None, description="Minimum rate (floor)")
    reset_frequency: Optional[int] = Field(default=None, description="Rate reset frequency")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @model_validator(mode='after')
    def check_cap_floor(self) -> 'FloatingRateConfig':
        """Checks that cap is greater than floor."""
        if self.cap is not None and self.floor is not None and self.cap <= self.floor:
            raise ValueError("Cap must be greater than floor")
        return self

class Bond(BaseModel):
    """
    Класс для моделирования облигации с поддержкой амортизации, досрочного погашения, 
    фиксированного и плавающего купона с расширенными возможностями.

    Parameters
    ----------
    issue_date : pd.Timestamp
        Дата выпуска облигации.
    maturity_date : pd.Timestamp
        Дата погашения облигации.
    face_value : float
        Номинал облигации (должен быть положительным).
    currency : str, default="USD"
        Валюта номинала облигации.
    coupon_rate : Union[float, List[float], FloatingRateConfig]
        Купонная ставка. Может быть фиксированной (float), списком ставок (List[float]) 
        или конфигурацией плавающей ставки (FloatingRateConfig).
    coupon_frequency : int
        Частота выплат купона в год (например, 2 - полугодовой, 4 - ежеквартальный).
    day_count_convention : str, default="30/360"
        Конвенция подсчета дней.
    business_day_convention : str, default="following"
        Конвенция рабочих дней.
    amortizations : Optional[List[Payment]], default=None
        Список амортизационных выплат.
    early_redemptions : Optional[List[Payment]], default=None
        Список досрочных погашений.
    schedule : Optional[List[Payment]], default=None
        Переопределенное расписание купонов (если есть).

    Examples
    --------
    >>> from assetlab import Bond, FloatingRateConfig
    >>> import pandas as pd
    >>> # Фиксированная ставка
    >>> bond = Bond(
    ...     issue_date=pd.Timestamp('2024-01-01'),
    ...     maturity_date=pd.Timestamp('2029-01-01'),
    ...     face_value=1000,
    ...     coupon_rate=0.05,
    ...     coupon_frequency=2
    ... )
    >>> # Плавающая ставка
    >>> floating_config = FloatingRateConfig(base_rate=0.03, spread=0.02, cap=0.08)
    >>> floating_bond = Bond(
    ...     issue_date=pd.Timestamp('2024-01-01'),
    ...     maturity_date=pd.Timestamp('2029-01-01'),
    ...     face_value=1000,
    ...     coupon_rate=floating_config,
    ...     coupon_frequency=2
    ... )
    """
    issue_date: pd.Timestamp = Field(..., description="Дата выпуска")
    maturity_date: pd.Timestamp = Field(..., description="Дата погашения")
    face_value: float = Field(..., gt=0, description="Номинал облигации")
    currency: str = Field(default="USD", description="Валюта номинала")
    
    # Поддержка как простых, так и сложных купонных ставок
    coupon_rate: Union[float, List[float], FloatingRateConfig] = Field(
        ..., description="Купонная ставка (фиксированная, список или конфигурация плавающей ставки)"
    )
    coupon_frequency: int = Field(..., gt=0, description="Частота выплат купона в год (например, 2 - полугодовой)")
    
    # Дополнительные параметры для плавающих ставок
    day_count_convention: str = Field(default="30/360", description="Конвенция подсчета дней")
    business_day_convention: str = Field(default="following", description="Конвенция рабочих дней")
    
    amortizations: Optional[List[Payment]] = Field(default=None, description="Список амортизационных выплат")
    early_redemptions: Optional[List[Payment]] = Field(default=None, description="Список досрочных погашений")
    schedule: Optional[List[Payment]] = Field(default=None, description="Переопределенное расписание купонов (если есть)")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode='after')
    def check_dates(self) -> 'Bond':
        # Проверка, что все даты событий в пределах срока обращения
        for event_list in [self.amortizations, self.early_redemptions, self.schedule]:
            if event_list:
                for event in event_list:
                    if not (self.issue_date <= event.date <= self.maturity_date):
                        raise ValueError(f"Дата события {event} выходит за рамки срока облигации.")
        return self

    def get_coupon_dates(self) -> List[pd.Timestamp]:
        """Генерирует даты купонных выплат с учетом конвенций."""
        if self.schedule is not None:
            # Если schedule задан (даже пустой), используем его
            return [e.date for e in self.schedule]
        
        # Генерируем стандартное расписание по календарным датам
        freq_map = {
            1: pd.DateOffset(years=1),
            2: pd.DateOffset(months=6),
            4: pd.DateOffset(months=3),
            12: pd.DateOffset(months=1)
        }
        offset = freq_map.get(self.coupon_frequency, pd.DateOffset(months=12 // self.coupon_frequency))
        dates = []
        current = self.issue_date
        
        while True:
            current = current + offset
            if current > self.maturity_date:
                break
            dates.append(current)
        
        # Исключаем maturity_date, если она не совпадает с очередным купоном
        if dates and dates[-1] != self.maturity_date:
            dates = [d for d in dates if d < self.maturity_date]
        
        return dates

    def get_base_rate(self, date: pd.Timestamp, period_idx: int) -> float:
        """Получает базовую ставку для указанной даты."""
        if isinstance(self.coupon_rate, FloatingRateConfig):
            base_rate = self.coupon_rate.base_rate
            
            if callable(base_rate):
                return base_rate(date)
            elif isinstance(base_rate, list):
                return base_rate[period_idx] if period_idx < len(base_rate) else base_rate[-1]
            else:
                return base_rate
        else:
            # Для фиксированных ставок возвращаем 0 как базовую ставку
            return 0.0

    def get_effective_rate(self, date: pd.Timestamp, period_idx: int) -> float:
        """Рассчитывает эффективную ставку с учетом спреда, капа и флора."""
        if isinstance(self.coupon_rate, FloatingRateConfig):
            base_rate = self.get_base_rate(date, period_idx)
            effective_rate = base_rate + self.coupon_rate.spread
            
            # Применяем кап и флор
            if self.coupon_rate.cap is not None:
                effective_rate = min(effective_rate, self.coupon_rate.cap)
            if self.coupon_rate.floor is not None:
                effective_rate = max(effective_rate, self.coupon_rate.floor)
                
            return effective_rate
        else:
            # Для фиксированных ставок
            if isinstance(self.coupon_rate, list):
                rate = self.coupon_rate[period_idx] if period_idx < len(self.coupon_rate) else self.coupon_rate[-1]
            else:
                rate = self.coupon_rate
            return rate

    def get_coupon_amount(self, period_idx: int, date: Optional[pd.Timestamp] = None) -> float:
        """Рассчитывает сумму купонного платежа с поддержкой плавающих ставок."""
        if date is None:
            coupon_dates = self.get_coupon_dates()
            if period_idx < len(coupon_dates):
                date = coupon_dates[period_idx]
            else:
                date = self.maturity_date
        
        effective_rate = self.get_effective_rate(date, period_idx)
        return self.face_value * effective_rate / self.coupon_frequency

    def get_coupon_schedule(self) -> List[Dict[str, Any]]:
        """Возвращает детальное расписание купонов с информацией о ставках."""
        schedule = []
        coupon_dates = self.get_coupon_dates()
        
        for i, date in enumerate(coupon_dates):
            if isinstance(self.coupon_rate, FloatingRateConfig):
                base_rate = self.get_base_rate(date, i)
                effective_rate = self.get_effective_rate(date, i)
                coupon_amount = self.get_coupon_amount(i, date)
                
                schedule.append({
                    'date': date,
                    'period': i + 1,
                    'base_rate': base_rate,
                    'spread': self.coupon_rate.spread,
                    'effective_rate': effective_rate,
                    'coupon_amount': coupon_amount,
                    'cap_applied': self.coupon_rate.cap is not None and effective_rate == self.coupon_rate.cap,
                    'floor_applied': self.coupon_rate.floor is not None and effective_rate == self.coupon_rate.floor
                })
            else:
                coupon_amount = self.get_coupon_amount(i, date)
                schedule.append({
                    'date': date,
                    'period': i + 1,
                    'rate': self.get_effective_rate(date, i),
                    'coupon_amount': coupon_amount
                })
        
        return schedule

    def get_amortization_by_date(self, date: pd.Timestamp) -> float:
        if not self.amortizations:
            return 0.0
        return sum(a.amount for a in self.amortizations if a.date == date)

    def get_early_redemption_by_date(self, date: pd.Timestamp) -> float:
        """Возвращает сумму досрочного погашения на указанную дату."""
        if self.early_redemptions:
            for redemption in self.early_redemptions:
                if redemption.date == date:
                    return redemption.amount
        return 0.0

    def next_coupon_date(self, analysis_date: pd.Timestamp) -> Optional[pd.Timestamp]:
        """
        Возвращает дату следующего купона после указанной даты.

        Parameters
        ----------
        analysis_date : pd.Timestamp
            Дата анализа.

        Returns
        -------
        Optional[pd.Timestamp]
            Дата следующего купона или None, если купонов больше нет.

        Examples
        --------
        >>> bond = Bond(issue_date=pd.Timestamp('2024-01-01'),
        ...            maturity_date=pd.Timestamp('2029-01-01'),
        ...            face_value=1000, coupon_rate=0.05, coupon_frequency=2)
        >>> bond.next_coupon_date(pd.Timestamp('2024-03-15'))
        Timestamp('2024-07-01 00:00:00')
        >>> bond.next_coupon_date(pd.Timestamp('2028-12-01'))
        Timestamp('2029-01-01 00:00:00')
        """
        coupon_dates = self.get_coupon_dates()
        
        # Ищем первый купон после даты анализа
        for date in coupon_dates:
            if date > analysis_date:
                return date
        
        return None

    def previous_coupon_date(self, analysis_date: pd.Timestamp) -> Optional[pd.Timestamp]:
        """
        Возвращает дату предыдущего купона до указанной даты.

        Parameters
        ----------
        analysis_date : pd.Timestamp
            Дата анализа.

        Returns
        -------
        Optional[pd.Timestamp]
            Дата предыдущего купона или None, если купонов до этой даты не было.

        Examples
        --------
        >>> bond = Bond(issue_date=pd.Timestamp('2024-01-01'),
        ...            maturity_date=pd.Timestamp('2029-01-01'),
        ...            face_value=1000, coupon_rate=0.05, coupon_frequency=2)
        >>> bond.previous_coupon_date(pd.Timestamp('2024-03-15'))
        Timestamp('2024-01-01 00:00:00')
        >>> bond.previous_coupon_date(pd.Timestamp('2024-07-15'))
        Timestamp('2024-07-01 00:00:00')
        """
        coupon_dates = self.get_coupon_dates()
        
        # Если дата анализа на дату выпуска или после неё, но до первого купона
        if analysis_date >= self.issue_date:
            if not coupon_dates or analysis_date < coupon_dates[0]:
                return self.issue_date
        
        # Ищем последний купон до даты анализа
        for date in reversed(coupon_dates):
            if date <= analysis_date:
                return date
        
        # Если не нашли купон в списке, но дата анализа после даты выпуска
        if analysis_date >= self.issue_date:
            return self.issue_date
        
        return None

    def accrued_interest(self, analysis_date: pd.Timestamp) -> float:
        """
        Рассчитывает накопленный купонный доход (NKD) на указанную дату.

        NKD = (Купон * Дни с последнего купона) / (Дни в купонном периоде)

        Parameters
        ----------
        analysis_date : pd.Timestamp
            Дата анализа.

        Returns
        -------
        float
            Накопленный купонный доход.

        Examples
        --------
        >>> bond = Bond(issue_date=pd.Timestamp('2024-01-01'),
        ...            maturity_date=pd.Timestamp('2029-01-01'),
        ...            face_value=1000, coupon_rate=0.05, coupon_frequency=2)
        >>> bond.accrued_interest(pd.Timestamp('2024-03-15'))
        20.83
        >>> bond.accrued_interest(pd.Timestamp('2024-07-01'))
        0.0
        """
        prev_coupon_date = self.previous_coupon_date(analysis_date)
        next_coupon_date = self.next_coupon_date(analysis_date)
        
        if prev_coupon_date is None or next_coupon_date is None:
            return 0.0
        
        # Если анализ на дату купона, NKD = 0
        if analysis_date == prev_coupon_date:
            return 0.0
        
        # Рассчитываем купон для текущего периода
        coupon_dates = self.get_coupon_dates()
        
        # Определяем индекс периода
        if prev_coupon_date == self.issue_date:
            # Для первого периода (от даты выпуска до первого купона)
            period_idx = 0
        else:
            # Для остальных периодов
            period_idx = coupon_dates.index(prev_coupon_date) if prev_coupon_date in coupon_dates else 0
        
        coupon_amount = self.get_coupon_amount(period_idx, prev_coupon_date)
        
        # Рассчитываем дни с последнего купона и дни в купонном периоде
        days_since_coupon = (analysis_date - prev_coupon_date).days
        days_in_period = (next_coupon_date - prev_coupon_date).days
        
        if days_in_period == 0:
            return 0.0
        
        # Рассчитываем NKD
        accrued = (coupon_amount * days_since_coupon) / days_in_period
        
        return accrued

    def clean_price(self, dirty_price: float, analysis_date: pd.Timestamp) -> float:
        """
        Рассчитывает чистую цену облигации из грязной цены.

        Чистая цена = Грязная цена - Накопленный купонный доход

        Parameters
        ----------
        dirty_price : float
            Грязная цена облигации (включая NKD).
        analysis_date : pd.Timestamp
            Дата анализа.

        Returns
        -------
        float
            Чистая цена облигации.

        Examples
        --------
        >>> bond = Bond(issue_date=pd.Timestamp('2024-01-01'),
        ...            maturity_date=pd.Timestamp('2029-01-01'),
        ...            face_value=1000, coupon_rate=0.05, coupon_frequency=2)
        >>> bond.clean_price(dirty_price=1025.83, analysis_date=pd.Timestamp('2024-03-15'))
        1005.0
        """
        accrued = self.accrued_interest(analysis_date)
        return dirty_price - accrued

    def dirty_price(self, clean_price: float, analysis_date: pd.Timestamp) -> float:
        """
        Рассчитывает грязную цену облигации из чистой цены.

        Грязная цена = Чистая цена + Накопленный купонный доход

        Parameters
        ----------
        clean_price : float
            Чистая цена облигации (без NKD).
        analysis_date : pd.Timestamp
            Дата анализа.

        Returns
        -------
        float
            Грязная цена облигации.

        Examples
        --------
        >>> bond = Bond(issue_date=pd.Timestamp('2024-01-01'),
        ...            maturity_date=pd.Timestamp('2029-01-01'),
        ...            face_value=1000, coupon_rate=0.05, coupon_frequency=2)
        >>> bond.dirty_price(clean_price=1005.0, analysis_date=pd.Timestamp('2024-03-15'))
        1025.83
        """
        accrued = self.accrued_interest(analysis_date)
        return clean_price + accrued

    def get_remaining_cashflow(self, analysis_date: pd.Timestamp) -> CashFlow:
        """
        Генерирует оставшийся денежный поток по облигации с указанной даты анализа.

        Parameters
        ----------
        analysis_date : pd.Timestamp
            Дата, на которую проводится анализ облигации.

        Returns
        -------
        CashFlow
            Оставшийся денежный поток с даты анализа.

        Examples
        --------
        >>> bond = Bond(issue_date=pd.Timestamp('2024-01-01'), 
        ...            maturity_date=pd.Timestamp('2029-01-01'),
        ...            face_value=1000, coupon_rate=0.05, coupon_frequency=2)
        >>> remaining_cf = bond.get_remaining_cashflow(pd.Timestamp('2025-06-01'))
        """
        if analysis_date < self.issue_date:
            raise ValueError("Дата анализа не может быть раньше даты выпуска")
        
        if analysis_date >= self.maturity_date:
            return CashFlow(payments=[])
        
        payments = []
        outstanding = self.face_value
        coupon_dates = self.get_coupon_dates()
        
        # Учитываем уже произведенные амортизации и досрочные погашения
        if self.amortizations:
            for amort in self.amortizations:
                if amort.date <= analysis_date:
                    outstanding -= amort.amount
        
        if self.early_redemptions:
            for early in self.early_redemptions:
                if early.date <= analysis_date:
                    outstanding -= early.amount
        
        # Если облигация уже полностью погашена, возвращаем пустой поток
        if outstanding <= 0:
            return CashFlow(payments=[])
        
        # Фильтруем только будущие даты
        future_dates = [d for d in coupon_dates if d > analysis_date]
        
        # Собираем все уникальные будущие даты событий
        all_future_dates = set(future_dates)
        if self.amortizations:
            all_future_dates.update(a.date for a in self.amortizations if a.date > analysis_date)
        if self.early_redemptions:
            all_future_dates.update(e.date for e in self.early_redemptions if e.date > analysis_date)
        
        # Сортируем даты
        all_future_dates = sorted(all_future_dates)
        
        for date in all_future_dates:
            # Купон (если дата купонная)
            if date in future_dates:
                period_idx = coupon_dates.index(date)
                coupon = self.get_coupon_amount(period_idx, date)
                if coupon != 0:
                    payments.append(Payment(date=date, amount=coupon))
            
            # Амортизация
            amort = self.get_amortization_by_date(date)
            if amort > 0:
                payments.append(Payment(date=date, amount=amort))
                outstanding -= amort
            
            # Досрочное погашение
            early = self.get_early_redemption_by_date(date)
            if early > 0:
                payments.append(Payment(date=date, amount=early))
                outstanding -= early
                # После полного погашения больше платежей нет
                if outstanding <= 0:
                    break
        
        # Погашение номинала в конце, если не был погашен досрочно
        if outstanding > 0:
            payments.append(Payment(date=self.maturity_date, amount=outstanding))
        
        return CashFlow(payments=payments)

    def to_cashflow(self) -> CashFlow:
        """
        Генерирует денежный поток по облигации с учетом купонов, амортизации и досрочного погашения.
        """
        cf = self.get_remaining_cashflow(self.issue_date)
        # Добавляем начальный платеж за покупку облигации
        cf.payments.insert(0, Payment(date=self.issue_date, amount=-self.face_value))
        return cf

    def ytm(self, price: float, analysis_date: Optional[pd.Timestamp] = None, 
            day_count: Optional[float] = None, guess: float = 0.1) -> Optional[float]:
        """
        Рассчитывает доходность к погашению (YTM) по текущей цене на указанную дату.

        Parameters
        ----------
        price : float
            Текущая цена облигации.
        analysis_date : Optional[pd.Timestamp], default=None
            Дата анализа. Если None, используется дата выпуска.
        day_count : Optional[float], default=None
            База для расчёта дней в году. Если None, используется глобальное значение из settings.DAY_COUNT.
        guess : float, default=0.1
            Начальное предположение для поиска YTM.

        Returns
        -------
        Optional[float]
            Доходность к погашению (YTM) или None, если расчет невозможен.

        Examples
        --------
        >>> bond = Bond(issue_date=pd.Timestamp('2018-04-03'), 
        ...            maturity_date=pd.Timestamp('2028-04-15'),
        ...            face_value=1000, coupon_rate=0.05, coupon_frequency=2)
        >>> # YTM на дату выпуска
        >>> bond.ytm(price=856.25)
        0.0712
        >>> # YTM на текущую дату
        >>> bond.ytm(price=856.25, analysis_date=pd.Timestamp('2024-12-01'))
        0.0689
        """
        if analysis_date is None:
            analysis_date = self.issue_date
        
        cf = self.get_remaining_cashflow(analysis_date)
        if not cf.payments:
            return None
        
        # Добавляем платеж за покупку облигации на дату анализа
        cf.payments.insert(0, Payment(date=analysis_date, amount=-price))
        return cf.xirr(guess=guess, day_count=day_count)

    def price_from_ytm(self, ytm: float, analysis_date: Optional[pd.Timestamp] = None,
                      day_count: Optional[float] = None) -> Optional[float]:
        """
        Рассчитывает цену облигации на основе доходности к погашению (YTM) на указанную дату.

        Parameters
        ----------
        ytm : float
            Доходность к погашению (YTM).
        analysis_date : Optional[pd.Timestamp], default=None
            Дата анализа. Если None, используется дата выпуска.
        day_count : Optional[float], default=None
            База для расчёта дней в году. Если None, используется глобальное значение из settings.DAY_COUNT.

        Returns
        -------
        Optional[float]
            Цена облигации или None, если расчет невозможен.

        Examples
        --------
        >>> bond = Bond(issue_date=pd.Timestamp('2018-04-03'), 
        ...            maturity_date=pd.Timestamp('2028-04-15'),
        ...            face_value=1000, coupon_rate=0.05, coupon_frequency=2)
        >>> # Цена на дату выпуска при YTM = 7.12%
        >>> bond.price_from_ytm(ytm=0.0712)
        856.25
        >>> # Цена на текущую дату при YTM = 6.89%
        >>> bond.price_from_ytm(ytm=0.0689, analysis_date=pd.Timestamp('2024-12-01'))
        875.30
        """
        if analysis_date is None:
            analysis_date = self.issue_date
        
        cf = self.get_remaining_cashflow(analysis_date)
        if not cf.payments:
            return None
        
        # Рассчитываем чистую приведенную стоимость (NPV) денежного потока
        # с заданной доходностью YTM
        npv = cf.xnpv(ytm, day_count=day_count)
        
        # Цена облигации - это NPV (положительная, так как это стоимость будущих платежей)
        return npv

    def current_yield(self, price: float, analysis_date: Optional[pd.Timestamp] = None) -> float:
        """
        Рассчитывает текущую доходность облигации на указанную дату.

        Текущая доходность = годовой купон / чистая цена.

        Parameters
        ----------
        price : float
            Текущая цена облигации (грязная цена, включая NKD).
        analysis_date : Optional[pd.Timestamp], default=None
            Дата анализа. Если None, используется дата выпуска.

        Returns
        -------
        float
            Текущая доходность облигации.

        Examples
        --------
        >>> bond = Bond(issue_date=pd.Timestamp('2018-04-03'), 
        ...            maturity_date=pd.Timestamp('2028-04-15'),
        ...            face_value=1000, coupon_rate=0.05, coupon_frequency=2)
        >>> bond.current_yield(price=856.25)
        0.0584
        >>> # На дату между купонами
        >>> bond.current_yield(price=1025.83, analysis_date=pd.Timestamp('2024-03-15'))
        0.0498
        """
        if analysis_date is None:
            analysis_date = self.issue_date
        
        # Рассчитываем чистую цену (без NKD)
        clean_price = self.clean_price(price, analysis_date)
        
        # Рассчитываем годовой купон
        annual_coupon = 0
        if isinstance(self.coupon_rate, FloatingRateConfig):
            # Для плавающих ставок используем следующую ставку
            next_coupon_date = self.next_coupon_date(analysis_date)
            if next_coupon_date:
                coupon_dates = self.get_coupon_dates()
                period_idx = coupon_dates.index(next_coupon_date) if next_coupon_date in coupon_dates else 0
                next_coupon = self.get_coupon_amount(period_idx, next_coupon_date)
                annual_coupon = next_coupon * self.coupon_frequency
        else:
            if isinstance(self.coupon_rate, list):
                # Для списка ставок используем следующую ставку
                next_coupon_date = self.next_coupon_date(analysis_date)
                if next_coupon_date:
                    coupon_dates = self.get_coupon_dates()
                    period_idx = coupon_dates.index(next_coupon_date) if next_coupon_date in coupon_dates else 0
                    if period_idx < len(self.coupon_rate):
                        rate = self.coupon_rate[period_idx]
                    else:
                        rate = self.coupon_rate[-1]
                    annual_coupon = self.face_value * rate
            else:
                annual_coupon = self.face_value * self.coupon_rate
        
        return annual_coupon / clean_price if clean_price > 0 else 0.0

    def macaulay_duration(self, price: float, analysis_date: Optional[pd.Timestamp] = None,
                         day_count: Optional[float] = None) -> Optional[float]:
        """
        Рассчитывает дюрацию Маколея по текущей цене на указанную дату.

        Parameters
        ----------
        price : float
            Текущая цена облигации.
        analysis_date : Optional[pd.Timestamp], default=None
            Дата анализа. Если None, используется дата выпуска.
        day_count : Optional[float], default=None
            База для расчёта дней в году. Если None, используется глобальное значение из settings.DAY_COUNT.

        Returns
        -------
        Optional[float]
            Дюрация Маколея в годах или None, если расчет невозможен.

        Examples
        --------
        >>> bond = Bond(issue_date=pd.Timestamp('2018-04-03'), 
        ...            maturity_date=pd.Timestamp('2028-04-15'),
        ...            face_value=1000, coupon_rate=0.05, coupon_frequency=2)
        >>> bond.macaulay_duration(price=856.25)
        7.23
        >>> bond.macaulay_duration(price=856.25, analysis_date=pd.Timestamp('2024-12-01'))
        3.45
        """
        if analysis_date is None:
            analysis_date = self.issue_date
        
        cf = self.get_remaining_cashflow(analysis_date)
        if not cf.payments:
            return None
        
        cf.payments.insert(0, Payment(date=analysis_date, amount=-price))
        ytm = self.ytm(price, analysis_date=analysis_date, day_count=day_count)
        if ytm is None:
            return None
        return cf.macaulay_duration(ytm, day_count=day_count)

    def modified_duration(self, price: float, analysis_date: Optional[pd.Timestamp] = None,
                         day_count: Optional[float] = None) -> Optional[float]:
        """
        Рассчитывает модифицированную дюрацию по текущей цене на указанную дату.

        Parameters
        ----------
        price : float
            Текущая цена облигации.
        analysis_date : Optional[pd.Timestamp], default=None
            Дата анализа. Если None, используется дата выпуска.
        day_count : Optional[float], default=None
            База для расчёта дней в году. Если None, используется глобальное значение из settings.DAY_COUNT.

        Returns
        -------
        Optional[float]
            Модифицированная дюрация в годах или None, если расчет невозможен.

        Examples
        --------
        >>> bond = Bond(issue_date=pd.Timestamp('2018-04-03'), 
        ...            maturity_date=pd.Timestamp('2028-04-15'),
        ...            face_value=1000, coupon_rate=0.05, coupon_frequency=2)
        >>> bond.modified_duration(price=856.25)
        6.98
        >>> bond.modified_duration(price=856.25, analysis_date=pd.Timestamp('2024-12-01'))
        3.34
        """
        if analysis_date is None:
            analysis_date = self.issue_date
        
        macaulay = self.macaulay_duration(price, analysis_date=analysis_date, day_count=day_count)
        ytm = self.ytm(price, analysis_date=analysis_date, day_count=day_count)
        if macaulay is None or ytm is None:
            return None
        return macaulay / (1 + ytm / self.coupon_frequency)

    def __repr__(self) -> str:
        if isinstance(self.coupon_rate, FloatingRateConfig):
            return (f"Bond(face_value={self.face_value}, floating_rate={self.coupon_rate}, "
                    f"freq={self.coupon_frequency}, issue='{self.issue_date.date()}', "
                    f"maturity='{self.maturity_date.date()}', currency='{self.currency}')")
        else:
            return (f"Bond(face_value={self.face_value}, coupon_rate={self.coupon_rate}, "
                    f"freq={self.coupon_frequency}, issue='{self.issue_date.date()}', "
                    f"maturity='{self.maturity_date.date()}', currency='{self.currency}')") 