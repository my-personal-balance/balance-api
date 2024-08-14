from dataclasses import dataclass
from typing import List

from balance_api.data.models.split_transactions import (
    SplitTransaction as m_SplitTransaction,
)


@dataclass
class SplitTransaction:
    id: int
    transaction_id: int
    amount: float
    description: str
    tag_id: int

    @classmethod
    def serialize(cls, st: m_SplitTransaction):
        return (
            SplitTransaction(
                st.id, st.transaction_id, st.amount, st.description, st.tag_id
            )
            if st
            else None
        )

    @classmethod
    def serialize_many(cls, sts: List[m_SplitTransaction]):
        return [cls.serialize(t) for t in sts]
