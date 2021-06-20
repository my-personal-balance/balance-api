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
from sqlalchemy.orm import relationship

from balance_api.models import Base
from balance_api.models.account_tags import AccountTag
from balance_api.models.accounts import Account


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
