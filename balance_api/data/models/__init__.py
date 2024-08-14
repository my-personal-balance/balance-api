import enum

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CurrencyType(enum.Enum):
    EUR = "EUR"
    BRL = "BRL"
