import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    INTEGER,
    TEXT,
    ForeignKey,
    Enum,
    DATE,
    FLOAT,
    DateTime,
)
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from balance_api.models import Base
from balance_api.models.account_tags import AccountTag
from balance_api.models.accounts import Account
from balance_api.models.users import User


class TransactionType(enum.Enum):
    EXPENSE = "expense"
    INCOME = "income"
    TRANSFER = "transafer"
    REFUND = "refund"
    INVESTMENT = "investment"
    IOU = "iou"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(TEXT, primary_key=True)
    previous_transaction_id = Column(TEXT)
    date = Column(DATE)
    transaction_type = Column("type", Enum(TransactionType))
    amount = Column(FLOAT)
    account_id = Column(
      INTEGER, ForeignKey("accounts.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    description = Column(TEXT)
    account_tag_id = Column(
        INTEGER, ForeignKey("account_tags.id", onupdate="CASCADE")
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    account = relationship(Account)
    account_tag = relationship(AccountTag)


def find_transaction(user_id: int, account_id: int, transaction_id: int, session: Session):
    q = (
        session.query(Transaction).join(Account).join(User).filter(
            User.id == user_id,
            Transaction.account_id == account_id,
            Transaction.id == transaction_id
        )
    )
    try:
        return q.one()
    except NoResultFound:
        return None


def list_transactions(user_id: int, account_id: int, session: Session) -> []:
    q = (
        session.query(Transaction).join(Account).join(User).filter(User.id == user_id)
    )

    if account_id:
        q = q.filter(Account.id == account_id)

    q.order_by(Transaction.date.desc())
    return [transaction for transaction in q.all()]


def get_balance(user_id: int, account_id: int, session: Session) -> float:
    q = (
        session.query(func.sum(Transaction.amount)).join(Account).join(User).filter(User.id == user_id)
    )

    if account_id:
        q = q.filter(Account.id == account_id)

    return round(q.scalar(), 2)
