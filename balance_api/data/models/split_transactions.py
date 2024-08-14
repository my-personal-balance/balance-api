from datetime import datetime, UTC

from sqlalchemy import (
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.session import Session

from balance_api.data.models import Base


class SplitTransaction(Base):
    __tablename__ = "split_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    amount: Mapped[float]
    description: Mapped[str]
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), onupdate="CASCADE")

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), nullable=False
    )


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
    return list_split_transactions(user_id, transaction_id, session)


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
