import enum

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CurrencyType(enum.Enum):
    EUR = "EUR"
    BRL = "BRL"
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value
