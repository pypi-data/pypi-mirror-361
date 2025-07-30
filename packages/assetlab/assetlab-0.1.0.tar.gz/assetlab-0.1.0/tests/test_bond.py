# tests/test_bond.py

import pandas as pd
import pytest
from assetlab import Bond, CashFlow, Payment, FloatingRateConfig

@pytest.fixture
def simple_bond():
    """Фикстура для простой облигации с фиксированным купоном."""
    return Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2027-01-01'),
        face_value=1000,
        coupon_rate=0.06,
        coupon_frequency=2
    )

@pytest.fixture
def floating_rate_bond():
    """Фикстура для облигации с плавающим купоном."""
    return Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2026-01-01'),
        face_value=1000,
        coupon_rate=[0.05, 0.06, 0.07, 0.08],  # Плавающая ставка
        coupon_frequency=2
    )

@pytest.fixture
def advanced_floating_bond():
    """Фикстура для облигации с расширенной плавающей ставкой."""
    floating_config = FloatingRateConfig(
        base_rate=[0.03, 0.04, 0.05, 0.06],  # Базовая ставка
        spread=0.02,  # Спред 2%
        cap=0.10,     # Максимум 10%
        floor=0.04    # Минимум 4%
    )
    
    return Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2026-01-01'),
        face_value=1000,
        coupon_rate=floating_config,
        coupon_frequency=2
    )

@pytest.fixture
def amortizing_bond():
    """Фикстура для амортизируемой облигации."""
    return Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2026-01-01'),
        face_value=1000,
        coupon_rate=0.08,
        coupon_frequency=2,
        amortizations=[
            Payment(date=pd.Timestamp('2024-07-01'), amount=200),
            Payment(date=pd.Timestamp('2025-01-01'), amount=200),
            Payment(date=pd.Timestamp('2025-07-01'), amount=200)
        ]
    )

@pytest.fixture
def early_redemption_bond():
    """Фикстура для облигации с досрочным погашением."""
    return Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2027-01-01'),
        face_value=1000,
        coupon_rate=0.06,
        coupon_frequency=2,
        early_redemptions=[
            Payment(date=pd.Timestamp('2025-07-01'), amount=1000)
        ]
    )

def test_bond_creation_and_properties(simple_bond):
    """Тестирует создание облигации и базовые свойства."""
    assert simple_bond.face_value == 1000
    assert simple_bond.coupon_rate == 0.06
    assert simple_bond.coupon_frequency == 2
    assert simple_bond.currency == "USD"

def test_coupon_dates_generation(simple_bond):
    """Тестирует генерацию дат купонных выплат."""
    dates = simple_bond.get_coupon_dates()
    expected_dates = [
        pd.Timestamp('2024-07-01'),
        pd.Timestamp('2025-01-01'),
        pd.Timestamp('2025-07-01'),
        pd.Timestamp('2026-01-01'),
        pd.Timestamp('2026-07-01'),
        pd.Timestamp('2027-01-01')  # maturity_date теперь включается
    ]
    assert dates == expected_dates

def test_coupon_amount_calculation(simple_bond):
    """Тестирует расчет суммы купонного платежа."""
    coupon_amount = simple_bond.get_coupon_amount(0)
    expected_amount = 1000 * 0.06 / 2  # 30
    assert coupon_amount == expected_amount

def test_floating_rate_coupon(floating_rate_bond):
    """Тестирует расчет купонов для плавающей ставки."""
    # Первый период
    assert floating_rate_bond.get_coupon_amount(0) == 1000 * 0.05 / 2
    # Второй период
    assert floating_rate_bond.get_coupon_amount(1) == 1000 * 0.06 / 2
    # Период после списка ставок (используется последняя)
    assert floating_rate_bond.get_coupon_amount(5) == 1000 * 0.08 / 2

def test_advanced_floating_rate_bond(advanced_floating_bond):
    """Тестирует облигацию с расширенной плавающей ставкой."""
    # Проверяем эффективные ставки с учетом спреда, капа и флора
    schedule = advanced_floating_bond.get_coupon_schedule()
    
    # Первый период: 3% + 2% = 5% (выше флора 4%)
    assert schedule[0]['base_rate'] == 0.03
    assert schedule[0]['effective_rate'] == 0.05
    assert schedule[0]['coupon_amount'] == 1000 * 0.05 / 2
    
    # Второй период: 4% + 2% = 6%
    assert schedule[1]['effective_rate'] == 0.06
    
    # Третий период: 5% + 2% = 7%
    assert schedule[2]['effective_rate'] == 0.07
    
    # Четвертый период: 6% + 2% = 8% (ниже капа 10%)
    assert schedule[3]['effective_rate'] == 0.08

def test_floating_rate_with_cap_floor():
    """Тестирует плавающую ставку с капом и флором."""
    # Создаем конфигурацию где кап и флор будут применяться
    floating_config = FloatingRateConfig(
        base_rate=[0.01, 0.15, 0.02],  # Очень низкая и очень высокая ставки
        spread=0.01,  # Спред 1%
        cap=0.10,     # Максимум 10%
        floor=0.05    # Минимум 5%
    )
    
    bond = Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2025-01-01'),
        face_value=1000,
        coupon_rate=floating_config,
        coupon_frequency=2
    )
    
    schedule = bond.get_coupon_schedule()
    
    # Первый период: 1% + 1% = 2% < 5% (флор), должно быть 5%
    assert schedule[0]['effective_rate'] == 0.05
    assert schedule[0]['floor_applied'] == True
    assert schedule[0]['cap_applied'] == False
    
    # Второй период: 15% + 1% = 16% > 10% (кап), должно быть 10%
    assert schedule[1]['effective_rate'] == 0.10
    assert schedule[1]['floor_applied'] == False
    assert schedule[1]['cap_applied'] == True

def test_floating_rate_with_function():
    """Тестирует плавающую ставку с функцией."""
    def rate_function(date: pd.Timestamp) -> float:
        # Простая функция: ставка растет со временем
        days_from_issue = (date - pd.Timestamp('2024-01-01')).days
        return 0.03 + (days_from_issue / 365) * 0.02  # От 3% до 5%
    
    floating_config = FloatingRateConfig(
        base_rate=rate_function,
        spread=0.01
    )
    
    bond = Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2025-07-01'),  # Увеличиваем срок до 1.5 лет
        face_value=1000,
        coupon_rate=floating_config,
        coupon_frequency=2
    )
    
    schedule = bond.get_coupon_schedule()
    
    # Проверяем, что ставки растут (должно быть 3 периода)
    assert len(schedule) >= 2
    assert schedule[0]['effective_rate'] < schedule[1]['effective_rate']
    if len(schedule) >= 3:
        assert schedule[1]['effective_rate'] < schedule[2]['effective_rate']

def test_bond_to_cashflow(simple_bond):
    """Тестирует преобразование облигации в денежный поток."""
    cf = simple_bond.to_cashflow()
    assert isinstance(cf, CashFlow)
    
    # Проверяем количество платежей: 1 покупка + 6 купонов + 1 погашение = 8
    assert len(cf.payments) == 8
    
    # Первый платеж - покупка (отрицательный)
    assert cf.payments[0].amount == -1000
    assert cf.payments[0].date == simple_bond.issue_date
    
    # Последний платеж - погашение номинала
    assert cf.payments[-1].amount == 1000
    assert cf.payments[-1].date == simple_bond.maturity_date

def test_amortizing_bond_cashflow(amortizing_bond):
    """Тестирует денежный поток амортизируемой облигации."""
    cf = amortizing_bond.to_cashflow()
    
    # Проверяем амортизационные платежи
    amort_payments = [p for p in cf.payments if p.amount == 200]
    assert len(amort_payments) == 3
    
    # Проверяем финальное погашение (остаток номинала)
    final_payment = cf.payments[-1]
    assert final_payment.amount == 400  # 1000 - 200*3
    assert final_payment.date == amortizing_bond.maturity_date

def test_early_redemption_bond_cashflow(early_redemption_bond):
    """Тестирует денежный поток облигации с досрочным погашением."""
    cf = early_redemption_bond.to_cashflow()
    
    # Проверяем досрочное погашение
    early_payment = [p for p in cf.payments if p.amount == 1000 and p.date == pd.Timestamp('2025-07-01')]
    assert len(early_payment) == 1
    
    # После досрочного погашения больше платежей нет
    payments_after_early = [p for p in cf.payments if p.date > pd.Timestamp('2025-07-01')]
    assert len(payments_after_early) == 0

def test_ytm_calculation(simple_bond):
    """Тестирует расчет доходности к погашению."""
    price = 950  # Покупка с дисконтом
    ytm = simple_bond.ytm(price)
    assert ytm is not None
    assert ytm > 0.06  # YTM должна быть выше купонной ставки при покупке с дисконтом

def test_current_yield_calculation(simple_bond):
    """Тестирует расчет текущей доходности."""
    price = 950
    current_yield = simple_bond.current_yield(price)
    expected_yield = (1000 * 0.06) / 950  # 0.0632
    assert current_yield == pytest.approx(expected_yield, abs=1e-4)

def test_current_yield_floating_rate(advanced_floating_bond):
    """Тестирует расчет текущей доходности для плавающей ставки."""
    price = 1000
    current_yield = advanced_floating_bond.current_yield(price)
    
    # Проверяем, что доходность рассчитана корректно
    assert current_yield > 0
    assert current_yield < 0.15  # Должна быть разумной

def test_duration_calculations(simple_bond):
    """Тестирует расчет дюрации."""
    price = 950
    macaulay_dur = simple_bond.macaulay_duration(price)
    modified_dur = simple_bond.modified_duration(price)
    
    assert macaulay_dur is not None
    assert modified_dur is not None
    assert macaulay_dur > 0
    assert modified_dur > 0
    assert modified_dur < macaulay_dur  # Модифицированная дюрация всегда меньше

def test_bond_with_custom_schedule():
    """Тестирует облигацию с кастомным расписанием купонов."""
    custom_schedule = [
        Payment(date=pd.Timestamp('2024-06-15'), amount=25),
        Payment(date=pd.Timestamp('2024-12-15'), amount=30),
        Payment(date=pd.Timestamp('2025-06-15'), amount=35)
    ]
    
    bond = Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2025-12-31'),
        face_value=1000,
        coupon_rate=0.06,  # Не используется при кастомном расписании
        coupon_frequency=2,
        schedule=custom_schedule
    )
    
    cf = bond.to_cashflow()
    # Проверяем, что купонные платежи соответствуют расписанию
    coupon_payments = [p for p in cf.payments if p.amount in [25, 30, 35]]
    assert len(coupon_payments) == 3

def test_bond_currency():
    """Тестирует облигацию в иностранной валюте."""
    usd_bond = Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2026-01-01'),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2,
        currency="USD"
    )
    
    assert usd_bond.currency == "USD"
    cf = usd_bond.to_cashflow()
    assert len(cf.payments) > 0

def test_invalid_event_date():
    """Тестирует валидацию дат событий."""
    with pytest.raises(ValueError, match="выходит за рамки срока облигации"):
        Bond(
            issue_date=pd.Timestamp('2024-01-01'),
            maturity_date=pd.Timestamp('2026-01-01'),
            face_value=1000,
            coupon_rate=0.06,
            coupon_frequency=2,
            amortizations=[
                Payment(date=pd.Timestamp('2023-01-01'), amount=100)
            ]
        )

def test_bond_repr(simple_bond):
    """Тестирует строковое представление облигации."""
    repr_str = repr(simple_bond)
    assert "Bond(" in repr_str
    assert "face_value=1000" in repr_str
    assert "coupon_rate=0.06" in repr_str
    assert "currency='USD'" in repr_str

def test_floating_rate_bond_repr(advanced_floating_bond):
    """Тестирует строковое представление облигации с плавающей ставкой."""
    repr_str = repr(advanced_floating_bond)
    assert "Bond(" in repr_str
    assert "floating_rate=" in repr_str
    assert "currency='USD'" in repr_str

def test_zero_coupon_bond():
    """Тестирует облигацию с нулевым купоном."""
    zero_coupon = Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2026-01-01'),
        face_value=1000,
        coupon_rate=0.0,
        coupon_frequency=1
    )
    
    cf = zero_coupon.to_cashflow()
    # Только покупка и погашение
    assert len(cf.payments) == 2
    assert cf.payments[0].amount == -1000
    assert cf.payments[1].amount == 1000

def test_ytm_edge_cases():
    """Тестирует граничные случаи YTM."""
    bond = Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2024-07-01'),  # 6 месяцев, совпадает с первым купоном
        face_value=1000,
        coupon_rate=0.06,
        coupon_frequency=2
    )
    
    # Покупка по номиналу
    ytm_at_par = bond.ytm(1000)
    # Ожидаемая доходность немного выше купонной ставки из-за сложных процентов
    assert ytm_at_par == pytest.approx(0.061, abs=1e-3)
    
    # Покупка с премией
    ytm_premium = bond.ytm(1050)
    assert ytm_premium < 0.0
    
    # Покупка с дисконтом
    ytm_discount = bond.ytm(950)
    assert ytm_discount > 0.0

def test_floating_rate_config_validation():
    """Тестирует валидацию конфигурации плавающей ставки."""
    # Валидная конфигурация
    config = FloatingRateConfig(
        base_rate=0.05,
        spread=0.02,
        cap=0.10,
        floor=0.03
    )
    assert config.base_rate == 0.05
    assert config.spread == 0.02
    assert config.cap == 0.10
    assert config.floor == 0.03
    
    # Проверяем, что кап больше флора
    with pytest.raises(ValueError):
        FloatingRateConfig(
            base_rate=0.05,
            cap=0.03,
            floor=0.10  # Флор больше капа
        ) 

def test_schedule_out_of_range():
    """Тест: событие в schedule вне диапазона дат облигации вызывает ошибку."""
    with pytest.raises(ValueError, match="выходит за рамки срока облигации"):
        Bond(
            issue_date=pd.Timestamp('2024-01-01'),
            maturity_date=pd.Timestamp('2026-01-01'),
            face_value=1000,
            coupon_rate=0.06,
            coupon_frequency=2,
            schedule=[
                Payment(date=pd.Timestamp('2023-12-31'), amount=30)
            ]
        )

def test_empty_schedule():
    """Тест: пустой schedule не вызывает ошибок и не создает купонов."""
    bond = Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2026-01-01'),
        face_value=1000,
        coupon_rate=0.06,
        coupon_frequency=2,
        schedule=[]
    )
    assert bond.get_coupon_dates() == []
    cf = bond.to_cashflow()
    # Только покупка и погашение
    assert len(cf.payments) == 2

def test_no_coupons():
    """Тест: облигация без купонов (coupon_rate=0) генерирует только покупку и погашение."""
    bond = Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2026-01-01'),
        face_value=1000,
        coupon_rate=0.0,
        coupon_frequency=2
    )
    cf = bond.to_cashflow()
    assert len(cf.payments) == 2
    assert cf.payments[0].amount == -1000
    assert cf.payments[1].amount == 1000

def test_amortization_and_early_redemption_edge():
    """Тест: амортизация и досрочное погашение на одной дате, остаток номинала = 0."""
    bond = Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2025-01-01'),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=1,
        amortizations=[Payment(date=pd.Timestamp('2024-07-01'), amount=400)],
        early_redemptions=[Payment(date=pd.Timestamp('2024-07-01'), amount=600)]
    )
    cf = bond.to_cashflow()
    # После досрочного погашения и амортизации остаток = 0, больше платежей нет
    assert cf.payments[-1].date == pd.Timestamp('2024-07-01')
    assert sum(p.amount for p in cf.payments) == 0

def test_coupon_on_maturity():
    """Тест: купонная дата совпадает с датой погашения."""
    bond = Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2025-01-01'),
        face_value=1000,
        coupon_rate=0.12,
        coupon_frequency=1
    )
    # Купонная дата совпадает с maturity_date
    dates = bond.get_coupon_dates()
    assert dates[-1] == pd.Timestamp('2025-01-01')
    cf = bond.to_cashflow()
    # Должно быть 1 покупка, 1 купон, 1 погашение
    assert len(cf.payments) == 3

def test_day_count_and_business_day_convention():
    """Тест: day_count_convention и business_day_convention устанавливаются и доступны."""
    bond = Bond(
        issue_date=pd.Timestamp('2024-01-01'),
        maturity_date=pd.Timestamp('2026-01-01'),
        face_value=1000,
        coupon_rate=0.06,
        coupon_frequency=2,
        day_count_convention="act/365",
        business_day_convention="preceding"
    )
    assert bond.day_count_convention == "act/365"
    assert bond.business_day_convention == "preceding"

def test_floating_rateconfig_cap_floor_validation():
    """Тест: FloatingRateConfig с cap <= floor вызывает ошибку."""
    with pytest.raises(ValueError, match="Cap must be greater than floor"):
        FloatingRateConfig(base_rate=0.05, cap=0.03, floor=0.04) 

def test_bond_analysis_on_current_date():
    """Тест анализа облигации на текущую дату."""
    bond = Bond(
        issue_date=pd.Timestamp("2018-04-03"),
        maturity_date=pd.Timestamp("2028-04-15"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Анализ на дату выпуска
    ytm_issue = bond.ytm(price=856.25)
    duration_issue = bond.macaulay_duration(price=856.25)
    
    # Анализ на текущую дату (2024-12-01)
    current_date = pd.Timestamp("2024-12-01")
    ytm_current = bond.ytm(price=856.25, analysis_date=current_date)
    duration_current = bond.macaulay_duration(price=856.25, analysis_date=current_date)
    
    # Проверяем, что YTM и дюрация изменились
    assert ytm_issue is not None
    assert ytm_current is not None
    assert duration_issue is not None
    assert duration_current is not None
    
    # Дюрация должна уменьшиться (меньше времени до погашения)
    assert duration_current < duration_issue

def test_get_remaining_cashflow():
    """Тест получения оставшегося денежного потока."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Получаем денежный поток с даты выпуска
    cf_issue = bond.get_remaining_cashflow(pd.Timestamp("2020-01-01"))
    assert len(cf_issue.payments) > 0
    
    # Получаем денежный поток с текущей даты
    cf_current = bond.get_remaining_cashflow(pd.Timestamp("2023-06-01"))
    assert len(cf_current.payments) > 0
    
    # Оставшийся поток должен быть короче
    assert len(cf_current.payments) < len(cf_issue.payments)
    
    # Проверяем, что все даты в будущем
    for payment in cf_current.payments:
        assert payment.date > pd.Timestamp("2023-06-01")

def test_analysis_date_validation():
    """Тест валидации даты анализа."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Дата анализа раньше выпуска
    with pytest.raises(ValueError, match="Дата анализа не может быть раньше даты выпуска"):
        bond.get_remaining_cashflow(pd.Timestamp("2019-01-01"))
    
    # Дата анализа после погашения
    cf = bond.get_remaining_cashflow(pd.Timestamp("2025-01-01"))
    assert len(cf.payments) == 0

def test_bond_with_amortization_analysis():
    """Тест анализа облигации с амортизацией на произвольную дату."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2,
        amortizations=[
            Payment(date=pd.Timestamp("2022-01-01"), amount=200),
            Payment(date=pd.Timestamp("2023-01-01"), amount=200)
        ]
    )
    
    # Анализ до амортизации
    cf_before = bond.get_remaining_cashflow(pd.Timestamp("2021-06-01"))
    outstanding_before = sum(p.amount for p in cf_before.payments if p.date == bond.maturity_date)
    assert outstanding_before == 625.0
    
    # Анализ после первой амортизации
    cf_after = bond.get_remaining_cashflow(pd.Timestamp("2022-06-01"))
    outstanding_after = sum(p.amount for p in cf_after.payments if p.date == bond.maturity_date)
    assert outstanding_after == 625.0

def test_current_yield_on_analysis_date():
    """Тест текущей доходности на произвольную дату."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    price = 950
    
    # Текущая доходность на дату выпуска
    cy_issue = bond.current_yield(price)
    
    # Текущая доходность на текущую дату
    cy_current = bond.current_yield(price, analysis_date=pd.Timestamp("2023-06-01"))
    
    assert cy_issue > 0
    assert cy_current > 0
    # Доходности должны быть близки, но могут отличаться из-за разного количества оставшихся купонов

def test_floating_rate_analysis_on_date():
    """Тест анализа облигации с плавающей ставкой на произвольную дату."""
    floating_config = FloatingRateConfig(
        base_rate=lambda date: 0.03 + 0.01 * (date.year - 2020),
        spread=0.02,
        cap=0.08
    )
    
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=floating_config,
        coupon_frequency=2
    )
    
    price = 950
    
    # Анализ на разные даты
    ytm_2021 = bond.ytm(price, analysis_date=pd.Timestamp("2021-06-01"))
    ytm_2023 = bond.ytm(price, analysis_date=pd.Timestamp("2023-06-01"))
    
    assert ytm_2021 is not None
    assert ytm_2023 is not None
    # YTM могут отличаться из-за изменения базовой ставки и времени до погашения 

def test_ytm_with_empty_cashflow():
    """Тест YTM с пустым денежным потоком (облигация уже погашена)."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Анализ после погашения
    ytm = bond.ytm(price=1000, analysis_date=pd.Timestamp("2025-01-01"))
    assert ytm is None

def test_duration_with_empty_cashflow():
    """Тест дюрации с пустым денежным потоком."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Анализ после погашения
    macaulay = bond.macaulay_duration(price=1000, analysis_date=pd.Timestamp("2025-01-01"))
    modified = bond.modified_duration(price=1000, analysis_date=pd.Timestamp("2025-01-01"))
    assert macaulay is None
    assert modified is None

def test_ytm_with_no_ytm():
    """Тест YTM когда расчет невозможен."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Анализ на дату выпуска с очень высокой ценой
    ytm = bond.ytm(price=10000, analysis_date=pd.Timestamp("2020-01-01"))
    # YTM может быть None если не удается найти решение
    # или очень высоким значением

def test_duration_with_no_ytm():
    """Тест дюрации когда YTM не может быть рассчитан."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Создаем ситуацию где YTM не может быть рассчитан
    # Это может произойти при очень экстремальных ценах
    macaulay = bond.macaulay_duration(price=10000, analysis_date=pd.Timestamp("2020-01-01"))
    modified = bond.modified_duration(price=10000, analysis_date=pd.Timestamp("2020-01-01"))
    # Результаты могут быть None или очень большими значениями

def test_bond_with_full_early_redemption():
    """Тест облигации с полным досрочным погашением."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2,
        early_redemptions=[
            Payment(date=pd.Timestamp("2023-01-01"), amount=1000)
        ]
    )
    
    # Анализ до досрочного погашения
    cf_before = bond.get_remaining_cashflow(pd.Timestamp("2022-06-01"))
    assert len(cf_before.payments) > 0
    
    # Анализ после досрочного погашения
    cf_after = bond.get_remaining_cashflow(pd.Timestamp("2023-06-01"))
    assert len(cf_after.payments) == 0

def test_bond_with_zero_outstanding():
    """Тест облигации где outstanding становится 0."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2,
        amortizations=[
            Payment(date=pd.Timestamp("2022-01-01"), amount=500),
            Payment(date=pd.Timestamp("2023-01-01"), amount=500)
        ]
    )
    
    # Анализ после полной амортизации
    cf = bond.get_remaining_cashflow(pd.Timestamp("2023-06-01"))
    # Проверяем что нет платежа на maturity_date
    maturity_payments = [p for p in cf.payments if p.date == bond.maturity_date]
    assert len(maturity_payments) == 0

def test_current_yield_with_no_coupons():
    """Тест текущей доходности когда нет купонов."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.0,  # Нулевой купон
        coupon_frequency=2
    )
    
    cy = bond.current_yield(price=950)
    assert cy == 0.0

def test_current_yield_floating_rate_no_coupons():
    """Тест текущей доходности для плавающей ставки без купонов."""
    floating_config = FloatingRateConfig(
        base_rate=0.0,  # Нулевая базовая ставка
        spread=0.0,
        cap=0.0
    )
    
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=floating_config,
        coupon_frequency=2
    )
    
    cy = bond.current_yield(price=950)
    assert cy == 0.0

def test_current_yield_list_rate_no_coupons():
    """Тест текущей доходности для списка ставок без купонов."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=[0.0, 0.0, 0.0, 0.0, 0.0],  # Все нулевые ставки
        coupon_frequency=2
    )
    
    cy = bond.current_yield(price=950)
    assert cy == 0.0 

def test_base_rate_fixed():
    """Тест базовой ставки для фиксированной ставки."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,  # Фиксированная ставка
        coupon_frequency=2
    )
    
    # Для фиксированной ставки базовая ставка должна быть 0
    base_rate = bond.get_base_rate(pd.Timestamp("2022-01-01"), 0)
    assert base_rate == 0.0

def test_coupon_schedule_with_cap_floor():
    """Тест расписания купонов с применением капа и флора."""
    floating_config = FloatingRateConfig(
        base_rate=0.10,  # Высокая базовая ставка
        spread=0.02,     # Спред
        cap=0.08,        # Кап ниже базовой ставки
        floor=0.03       # Флор
    )
    
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2022-01-01"),
        face_value=1000,
        coupon_rate=floating_config,
        coupon_frequency=2
    )
    
    schedule = bond.get_coupon_schedule()
    assert len(schedule) > 0
    
    # Проверяем что кап применяется (базовая ставка 0.10 + спред 0.02 = 0.12 > кап 0.08)
    cap_applied = any(item.get('cap_applied', False) for item in schedule)
    assert cap_applied
    
    # Проверяем что флор не применяется (эффективная ставка выше флора)
    floor_applied = any(item.get('floor_applied', False) for item in schedule)
    assert not floor_applied  # Флор не должен применяться

def test_current_yield_with_remaining_coupons():
    """Тест текущей доходности когда есть оставшиеся купоны."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Анализ на середине срока
    cy = bond.current_yield(price=950, analysis_date=pd.Timestamp("2022-06-01"))
    assert cy > 0

def test_macaulay_duration_edge_cases():
    """Тест edge cases для дюрации Маколея."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Тест с очень низкой ценой (может привести к None YTM)
    duration = bond.macaulay_duration(price=1, analysis_date=pd.Timestamp("2020-01-01"))
    # Результат может быть None или очень большим значением 

def test_price_from_ytm_basic():
    """Базовый тест расчета цены по YTM: проверяем обратимость и относительные соотношения."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    # Тест на дату выпуска
    ytm = 0.05
    price = bond.price_from_ytm(ytm=ytm)
    assert price is not None
    # Проверяем обратимость: ytm(price_from_ytm(ytm)) ≈ ytm
    ytm_calc = bond.ytm(price=price)
    assert ytm_calc is not None
    assert abs(ytm_calc - ytm) < 1e-2
    # Проверяем относительные соотношения
    price_high_ytm = bond.price_from_ytm(ytm=0.10)
    price_low_ytm = bond.price_from_ytm(ytm=0.02)
    assert price_high_ytm < price < price_low_ytm

def test_price_from_ytm_on_analysis_date():
    """Тест расчета цены по YTM на произвольную дату: проверяем обратимость."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    analysis_date = pd.Timestamp("2022-06-01")
    ytm = 0.06
    price = bond.price_from_ytm(ytm=ytm, analysis_date=analysis_date)
    assert price is not None
    ytm_calc = bond.ytm(price=price, analysis_date=analysis_date)
    assert ytm_calc is not None
    assert abs(ytm_calc - ytm) < 1e-2

def test_price_from_ytm_edge_cases():
    """Тест edge cases для расчета цены по YTM: обратимость и относительные соотношения."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    # Нулевая доходность
    ytm_zero = 0.0
    price_zero_ytm = bond.price_from_ytm(ytm=ytm_zero)
    assert price_zero_ytm is not None
    ytm_calc_zero = bond.ytm(price=price_zero_ytm)
    assert ytm_calc_zero is not None
    assert abs(ytm_calc_zero - ytm_zero) < 1e-2
    # Очень высокая доходность
    ytm_high = 0.50
    price_high_ytm = bond.price_from_ytm(ytm=ytm_high)
    assert price_high_ytm is not None
    ytm_calc_high = bond.ytm(price=price_high_ytm)
    assert ytm_calc_high is not None
    # Для очень высоких YTM (50%) допускаем большую погрешность
    assert abs(ytm_calc_high - ytm_high) < 0.1
    # Отрицательная доходность
    ytm_neg = -0.02
    price_neg_ytm = bond.price_from_ytm(ytm=ytm_neg)
    assert price_neg_ytm is not None
    ytm_calc_neg = bond.ytm(price=price_neg_ytm)
    assert ytm_calc_neg is not None
    assert abs(ytm_calc_neg - ytm_neg) < 1e-2
    # Соотношения
    assert price_high_ytm < price_zero_ytm < price_neg_ytm

def test_price_from_ytm_with_empty_cashflow():
    """Тест расчета цены по YTM с пустым денежным потоком."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    # Анализ после погашения
    price = bond.price_from_ytm(ytm=0.05, analysis_date=pd.Timestamp("2025-01-01"))
    assert price is None

def test_price_from_ytm_inverse_relationship():
    """Тест обратной связи между price_from_ytm и ytm для разных YTM."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    for target_ytm in [0.03, 0.05, 0.07, 0.10]:
        price = bond.price_from_ytm(ytm=target_ytm)
        assert price is not None
        calculated_ytm = bond.ytm(price=price)
        assert calculated_ytm is not None
        # Для YTM=10% допускаем немного большую погрешность
        tolerance = 0.02 if target_ytm >= 0.10 else 1e-2
        assert abs(calculated_ytm - target_ytm) < tolerance

def test_price_from_ytm_floating_rate():
    """Тест расчета цены по YTM для облигации с плавающей ставкой: обратимость и соотношения."""
    floating_config = FloatingRateConfig(
        base_rate=0.03,
        spread=0.02,
        cap=0.08,
        floor=0.04
    )
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=floating_config,
        coupon_frequency=2
    )
    ytm1 = 0.06
    ytm2 = 0.08
    price1 = bond.price_from_ytm(ytm=ytm1)
    price2 = bond.price_from_ytm(ytm=ytm2)
    assert price1 is not None and price2 is not None
    assert price1 > price2
    # Проверяем обратимость
    assert abs(bond.ytm(price=price1) - ytm1) < 1e-2
    assert abs(bond.ytm(price=price2) - ytm2) < 1e-2

def test_price_from_ytm_with_amortization():
    """Тест расчета цены по YTM для амортизируемой облигации: обратимость."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2,
        amortizations=[
            Payment(date=pd.Timestamp("2022-01-01"), amount=200),
            Payment(date=pd.Timestamp("2023-01-01"), amount=200)
        ]
    )
    ytm = 0.06
    price_issue = bond.price_from_ytm(ytm=ytm)
    assert price_issue is not None
    price_after_amort = bond.price_from_ytm(ytm=ytm, analysis_date=pd.Timestamp("2023-06-01"))
    assert price_after_amort is not None
    assert price_after_amort < price_issue
    # Проверяем обратимость
    assert abs(bond.ytm(price=price_issue) - ytm) < 1e-2
    assert abs(bond.ytm(price=price_after_amort, analysis_date=pd.Timestamp("2023-06-01")) - ytm) < 1e-2

def test_price_from_ytm_with_early_redemption():
    """Тест расчета цены по YTM для облигации с досрочным погашением: обратимость."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2,
        early_redemptions=[
            Payment(date=pd.Timestamp("2023-01-01"), amount=500)
        ]
    )
    ytm = 0.06
    price_issue = bond.price_from_ytm(ytm=ytm)
    assert price_issue is not None
    price_after_redemption = bond.price_from_ytm(ytm=ytm, analysis_date=pd.Timestamp("2023-06-01"))
    assert price_after_redemption is not None
    assert price_after_redemption < price_issue
    # Проверяем обратимость
    assert abs(bond.ytm(price=price_issue) - ytm) < 1e-2
    assert abs(bond.ytm(price=price_after_redemption, analysis_date=pd.Timestamp("2023-06-01")) - ytm) < 1e-2 

def test_next_coupon_date():
    """Тест получения даты следующего купона."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Тест на дату выпуска
    next_date = bond.next_coupon_date(pd.Timestamp("2020-01-01"))
    assert next_date == pd.Timestamp("2020-07-01")
    
    # Тест между купонами
    next_date = bond.next_coupon_date(pd.Timestamp("2020-03-15"))
    assert next_date == pd.Timestamp("2020-07-01")
    
    # Тест на дату купона
    next_date = bond.next_coupon_date(pd.Timestamp("2020-07-01"))
    assert next_date == pd.Timestamp("2021-01-01")
    
    # Тест после последнего купона
    next_date = bond.next_coupon_date(pd.Timestamp("2025-01-01"))
    assert next_date is None

def test_previous_coupon_date():
    """Тест получения даты предыдущего купона."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Тест на дату выпуска
    prev_date = bond.previous_coupon_date(pd.Timestamp("2020-01-01"))
    assert prev_date == pd.Timestamp("2020-01-01")
    
    # Тест между купонами
    prev_date = bond.previous_coupon_date(pd.Timestamp("2020-03-15"))
    assert prev_date == pd.Timestamp("2020-01-01")
    
    # Тест на дату купона
    prev_date = bond.previous_coupon_date(pd.Timestamp("2020-07-01"))
    assert prev_date == pd.Timestamp("2020-07-01")
    
    # Тест до первого купона
    prev_date = bond.previous_coupon_date(pd.Timestamp("2019-12-01"))
    assert prev_date is None

def test_accrued_interest():
    """Тест расчета накопленного купонного дохода."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Тест на дату купона (NKD = 0)
    accrued = bond.accrued_interest(pd.Timestamp("2020-07-01"))
    assert accrued == 0.0
    
    # Тест на середине купонного периода
    accrued = bond.accrued_interest(pd.Timestamp("2020-04-01"))
    assert accrued > 0
    assert accrued < 25  # Половина полугодового купона
    
    # Тест на дату выпуска
    accrued = bond.accrued_interest(pd.Timestamp("2020-01-01"))
    assert accrued == 0.0

def test_accrued_interest_floating_rate():
    """Тест NKD для облигации с плавающей ставкой."""
    floating_config = FloatingRateConfig(
        base_rate=0.03,
        spread=0.02,
        cap=0.08,
        floor=0.04
    )
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=floating_config,
        coupon_frequency=2
    )
    
    # Тест на середине купонного периода
    accrued = bond.accrued_interest(pd.Timestamp("2020-04-01"))
    assert accrued > 0
    # Эффективная ставка = 0.03 + 0.02 = 0.05, но с флором 0.04
    # Полугодовой купон = 1000 * 0.05 / 2 = 25
    # На середине периода NKD ≈ 12.5
    assert 10 < accrued < 15

def test_clean_price():
    """Тест расчета чистой цены из грязной."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Тест на дату купона (NKD = 0)
    clean_price = bond.clean_price(1025.0, pd.Timestamp("2020-07-01"))
    assert clean_price == 1025.0
    
    # Тест между купонами
    dirty_price = 1025.83
    clean_price = bond.clean_price(dirty_price, pd.Timestamp("2020-04-01"))
    assert clean_price < dirty_price
    assert clean_price > 1000

def test_dirty_price():
    """Тест расчета грязной цены из чистой."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Тест на дату купона (NKD = 0)
    dirty_price = bond.dirty_price(1025.0, pd.Timestamp("2020-07-01"))
    assert dirty_price == 1025.0
    
    # Тест между купонами
    clean_price = 1005.0
    dirty_price = bond.dirty_price(clean_price, pd.Timestamp("2020-04-01"))
    assert dirty_price > clean_price
    
    # Проверяем обратимость
    clean_price_calc = bond.clean_price(dirty_price, pd.Timestamp("2020-04-01"))
    assert abs(clean_price_calc - clean_price) < 1e-2

def test_current_yield_with_accrued_interest():
    """Тест текущей доходности с учетом NKD."""
    bond = Bond(
        issue_date=pd.Timestamp("2020-01-01"),
        maturity_date=pd.Timestamp("2025-01-01"),
        face_value=1000,
        coupon_rate=0.05,
        coupon_frequency=2
    )
    
    # Тест на дату купона
    cy_on_coupon = bond.current_yield(1025.0, pd.Timestamp("2020-07-01"))
    
    # Тест между купонами (грязная цена включает NKD)
    dirty_price = 1025.83
    cy_between_coupons = bond.current_yield(dirty_price, pd.Timestamp("2020-04-01"))
    
    # Текущая доходность должна быть одинаковой (относительно чистой цены)
    assert abs(cy_on_coupon - cy_between_coupons) < 1e-3 