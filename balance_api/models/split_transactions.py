from datetime import datetime

from sqlalchemy import (
    Column,
    INTEGER,
    TEXT,
    ForeignKey,
    FLOAT,
    DateTime,
)
from sqlalchemy.orm.session import Session

from balance_api.models import Base


class SplitTransaction(Base):
    __tablename__ = "split_transactions"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    transaction_id = Column(
        INTEGER, ForeignKey("transactions.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    amount = Column(FLOAT)
    description = Column(TEXT)
    tag_id = Column(INTEGER, ForeignKey("tags.id", onupdate="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def create_split_transactions(
    user_id: int,
    transaction_id: int,
    split_transactions: [],
    session: Session,
):
    delete_split_transactions(transaction_id, session)
    for transaction_resource in split_transactions:
        split_transaction = SplitTransaction(**transaction_resource)
        split_transaction.transaction_id = transaction_id
        session.add(split_transaction)

    session.commit()
    return split_transactions


def delete_split_transactions(transaction_id: int, session: Session):
    q = session.query(SplitTransaction).where(
        SplitTransaction.transaction_id == transaction_id
    )
    split_transactions = q.all()
    if split_transactions:
        for split_transaction in split_transactions:
            session.delete(split_transaction)
        session.commit()


def list_split_transactions(user_id: int, transaction_id: int, session: Session):
    return (
        session.query(SplitTransaction).filter(
            SplitTransaction.transaction_id == transaction_id,
        )
    ).all()
