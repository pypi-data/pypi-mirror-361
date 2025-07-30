# AssetLab

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Coverage](https://img.shields.io/badge/coverage-95%25-green.svg)](https://htmlcov.io/)

**AssetLab** is a powerful Python library for financial calculations, including cash flow analysis, asset valuation, and portfolio metrics.

> **🌍 Multilingual Support**: This project supports both English and Russian languages. See [README_ru.md](README_ru.md) for Russian documentation.

## 🚀 Features

### 💰 Cash Flow Analysis (CashFlow)
- **XNPV** - Net Present Value for irregular cash flows
- **XIRR** - Internal Rate of Return
- **MIRR** - Modified Internal Rate of Return
- **DPP** - Discounted Payback Period
- **Duration** - Macaulay and Modified
- **Profitability Index** and Payback Period
- **Visualization** of cash flows
- **Export** to pandas DataFrame

### 🏦 Deposit Modeling (Deposit)
- Interest capitalization and payment
- Deposits and partial withdrawals
- Various interest compounding frequencies
- Conversion to CashFlow for analysis

### 📈 Bond Modeling (Bond)
- Fixed and floating coupons
- Amortization and early redemption
- Support for caps and floors on floating rates
- Functional base rates
- YTM, current yield, duration calculations

## 📦 Installation

### From Source
```bash
git clone https://github.com/your-username/AssetLab.git
cd AssetLab
pip install -e .
```

### Dependencies
- Python 3.9+
- pandas >= 1.5.0
- numpy >= 1.23.0
- pydantic >= 2.0.0
- scipy >= 1.9.0
- matplotlib >= 3.7.0

## 🎯 Quick Start

### Bond Investment Analysis

```python
import pandas as pd
from assetlab import CashFlow, Payment

# Create a bond cash flow
bond_cf = CashFlow(payments=[
    Payment(date=pd.Timestamp('2024-01-15'), amount=-980),  # Purchase
    Payment(date=pd.Timestamp('2025-01-15'), amount=60),    # 1st coupon
    Payment(date=pd.Timestamp('2026-01-15'), amount=60),    # 2nd coupon
    Payment(date=pd.Timestamp('2027-01-15'), amount=1060),  # 3rd coupon + redemption
])

# Calculate key metrics
discount_rate = 0.05
npv = bond_cf.xnpv(discount_rate)
irr = bond_cf.xirr()
duration = bond_cf.modified_duration(yield_rate=irr)

print(f"NPV: {npv:.2f}")
print(f"IRR: {irr:.2%}")
print(f"Duration: {duration:.2f} years")
```

### Bank Deposit Modeling

```python
from assetlab import Deposit, Payment

# Create a deposit with compounding
deposit = Deposit(
    principal=100000,
    annual_rate=0.08,
    start_date=pd.Timestamp('2024-01-01'),
    end_date=pd.Timestamp('2026-01-01'),
    interest_frequency=4,  # Quarterly compounding
    replenishments=[
        Payment(date=pd.Timestamp('2024-06-15'), amount=20000)
    ]
)

# Get results
final_value = deposit.final_value()
total_interest = deposit.total_interest()
cashflow = deposit.to_cashflow()

print(f"Final amount: {final_value:.2f}")
print(f"Total interest: {total_interest:.2f}")
```

## 📊 Usage Examples

### Portfolio Analysis

```python
# Create several assets
bond_cf = CashFlow(payments=[
    Payment(date=pd.Timestamp('2024-01-01'), amount=-1000),
    Payment(date=pd.Timestamp('2025-01-01'), amount=1100),
])

stock_cf = CashFlow(payments=[
    Payment(date=pd.Timestamp('2024-01-01'), amount=-1500),
    Payment(date=pd.Timestamp('2024-06-01'), amount=50),   # Dividend
    Payment(date=pd.Timestamp('2025-01-01'), amount=1600), # Sale
])

# Combine into portfolio
portfolio = bond_cf + stock_cf

# Analyze portfolio
portfolio_npv = portfolio.xnpv(0.05)
portfolio_irr = portfolio.xirr()

print(f"Portfolio NPV: {portfolio_npv:.2f}")
print(f"Portfolio IRR: {portfolio_irr:.2%}")
```

### Cash Flow Visualization

```python
import matplotlib.pyplot as plt

# Create chart
fig, ax = plt.subplots(figsize=(10, 6))
bond_cf.plot(ax=ax, width=20)
ax.set_title("Bond Cash Flow")
plt.show()
```

## 📘 Example: Bond Analysis (Bond)

```python
import pandas as pd
from assetlab import Bond, Payment, FloatingRateConfig

# Simple bond with amortization example
bond = Bond(
    issue_date=pd.Timestamp('2024-01-01'),
    maturity_date=pd.Timestamp('2027-01-01'),
    face_value=1000,
    coupon_rate=0.07,  # 7% annual
    coupon_frequency=2,  # Semi-annual coupon
    amortizations=[
        Payment(date=pd.Timestamp('2025-01-01'), amount=200),
        Payment(date=pd.Timestamp('2026-01-01'), amount=200)
    ]
)

# Generate cash flow
cf = bond.to_cashflow()
print(cf.to_dataframe())

# Analyze yield to maturity (YTM) when purchased at 980
ytm = bond.ytm(price=980)
print(f"YTM: {ytm:.2%}")

# Current yield
current_yield = bond.current_yield(price=980)
print(f"Current yield: {current_yield:.2%}")

# Duration
macaulay = bond.macaulay_duration(price=980)
print(f"Macaulay duration: {macaulay:.2f} years")
```

### Floating Rate Bond

```python
# Floating rate configuration
floating_config = FloatingRateConfig(
    base_rate=0.03,  # Base rate 3%
    spread=0.02,     # Spread 2%
    cap=0.08,        # Maximum rate 8%
    floor=0.01       # Minimum rate 1%
)

# Floating rate bond
floating_bond = Bond(
    issue_date=pd.Timestamp('2024-01-01'),
    maturity_date=pd.Timestamp('2029-01-01'),
    face_value=1000,
    coupon_rate=floating_config,
    coupon_frequency=2
)

# Analyze coupon schedule
schedule = floating_bond.get_coupon_schedule()
print("Floating rate bond coupon schedule:")
for item in schedule:
    print(f"Period {item['period']}: Effective rate: {item['effective_rate']:.3%}, "
          f"Coupon: {item['coupon_amount']:.2f}")
```

### Working with Accrued Interest (AI)

```python
# Analysis on arbitrary date
analysis_date = pd.Timestamp('2024-03-15')

# Coupon dates
next_coupon = bond.next_coupon_date(analysis_date)
prev_coupon = bond.previous_coupon_date(analysis_date)
print(f"Next coupon: {next_coupon}")
print(f"Previous coupon: {prev_coupon}")

# Accrued interest
accrued = bond.accrued_interest(analysis_date)
print(f"Accrued interest on {analysis_date.date()}: {accrued:.2f}")

# Working with clean and dirty prices
dirty_price = 1025.83  # Price with AI
clean_price = bond.clean_price(dirty_price, analysis_date)
print(f"Clean price: {clean_price:.2f}")

# Reverse operation
dirty_price_calc = bond.dirty_price(clean_price, analysis_date)
print(f"Dirty price: {dirty_price_calc:.2f}")

# Current yield with AI
current_yield = bond.current_yield(dirty_price, analysis_date)
print(f"Current yield: {current_yield:.2%}")
```

### Analysis on Arbitrary Date

```python
# Bond analysis on current date (not issue date)
current_date = pd.Timestamp('2024-06-15')

# YTM on current date
ytm_current = bond.ytm(price=950, analysis_date=current_date)
print(f"YTM on {current_date.date()}: {ytm_current:.2%}")

# Duration on current date
duration_current = bond.macaulay_duration(price=950, analysis_date=current_date)
print(f"Duration on {current_date.date()}: {duration_current:.2f} years")

# Price from YTM on current date
price_from_ytm = bond.price_from_ytm(ytm=0.06, analysis_date=current_date)
print(f"Price at 6% YTM on {current_date.date()}: {price_from_ytm:.2f}")
```

## ⚙️ Settings

The library supports global settings:

```python
from assetlab import settings

# Change day count basis for calculations
settings.settings.DAY_COUNT = 360.0  # Default is 365.0
```

## 🧪 Testing

Running tests:
```bash
# All tests
pytest

# With code coverage
tox

# Individual module
pytest tests/test_cashflow.py
```

## 📈 Code Coverage

Current test coverage: **96%**

- `assetlab/__init__.py`: 100%
- `assetlab/cashflow.py`: 96%
- `assetlab/deposit.py`: 94%
- `assetlab/bond.py`: 97%
- `assetlab/settings.py`: 100%

## 📚 Documentation

### Jupyter Notebooks
Detailed usage examples are available in the `examples/` folder:

- `01_investment_analysis.ipynb` - investment and portfolio analysis
- `02_deposit_analysis.ipynb` - deposit analysis with replenishments
- `03_bond_analysis.ipynb` - bond analysis (fixed, floating, amortization, callable)

Russian versions are available in the `examples/ru/` folder:
- `01_investment_analysis.ipynb` - investment and portfolio analysis
- `02_deposit_analysis.ipynb` - deposit analysis with replenishments
- `03_bond_analysis.ipynb` - bond analysis (fixed, floating, amortization, callable)

### Sphinx Documentation
Complete API documentation is available in the `docs/` folder:

```bash
cd docs
make html
open _build/html/index.html
```

Documentation includes:
- Auto-generated API documentation
- Usage examples
- Detailed description of all classes and methods

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Maxim** - [MaximVUstinov@gmail.com](mailto:MaximVUstinov@gmail.com)

## 🔗 Links

- [Repository](https://github.com/your-username/AssetLab)
- [Issues](https://github.com/your-username/AssetLab/issues)
- [Releases](https://github.com/your-username/AssetLab/releases) 