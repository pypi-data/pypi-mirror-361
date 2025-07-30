# cashflow/config.py

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """
    Глобальные настройки для библиотеки AssetLab.

    Пользователи могут изменять эти значения, чтобы повлиять на все расчеты
    по умолчанию.
    Пример:
        from cashflow import config
        config.settings.DAY_COUNT = 360.0
    """
    # Basis for calculating days in a year.
# Standard values: 365, 360, 365.25
    DAY_COUNT: float = Field(
        default=365.0,
        description="База для расчета количества дней в году (например, 365.0 или 360.0)."
    )


# Create a single settings instance that will be used throughout the library
settings = Settings()
