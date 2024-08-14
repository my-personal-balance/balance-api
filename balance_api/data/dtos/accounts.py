from dataclasses import dataclass
from typing import List

from balance_api.data.models.accounts import Account as m_Account


@dataclass
class Account:
    id: int
    alias: str
    user_id: int
    type: str
    currency: str

    balance: float = 0.0
    incomes: float = 0.0
    expenses: float = 0.0

    @classmethod
    def serialize(cls, a: m_Account, **kwarg):
        balance = kwarg.get("balance", 0.0)
        incomes = kwarg.get("incomes", 0.0)
        expenses = kwarg.get("expenses", 0.0)
        return (
            Account(
                a.id,
                a.alias,
                a.user_id,
                a.type.name if a.type else None,
                a.currency.name if a.currency else None,
                balance,
                incomes,
                expenses,
            )
            if a
            else None
        )

    @classmethod
    def serialize_many(cls, accounts: List[m_Account]):
        return [cls.serialize(account) for account in accounts]
