from dataclasses import dataclass
from typing import List

from balance_api.data.dtos.accounts import Account
from balance_api.data.dtos.split_transactions import SplitTransaction
from balance_api.data.dtos.tags import Tag
from balance_api.data.models.transactions import (
    Transaction as m_Transaction,
)


@dataclass
class Transaction:
    id: int
    date: str
    transaction_type: str
    amount: float
    account_id: int
    description: str
    tag_id: int

    account: Account
    tag: Tag

    split_transactions: List[SplitTransaction]

    balance: float

    @classmethod
    def serialize(cls, t: m_Transaction):
        return (
            Transaction(
                t.id,
                t.date.strftime("%Y-%m-%d") if t.date else None,
                t.transaction_type.name if t.transaction_type else None,
                t.amount,
                t.account_id,
                t.description,
                t.tag_id,
                Account.serialize(t.account),
                Tag.serialize(t.tag),
                SplitTransaction.serialize_many(t.split_transactions),
                t.balance,
            )
            if t
            else None
        )

    @classmethod
    def serialize_many(cls, transactions: List[m_Transaction]):
        return [cls.serialize(t) for t in transactions]
