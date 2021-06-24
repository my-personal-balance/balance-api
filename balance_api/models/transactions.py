import calendar
import enum
import uuid
from datetime import datetime, date

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
from sqlalchemy import func, case, between
from sqlalchemy.dialects.postgresql import UUID
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


class PeriodType(enum.Enum):
    CUSTOM = "custom"
    CURRENT_MONTH = "current_month"
    LAST_MONTH = "last_month"
    LAST_YEAR = "last_year"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(TEXT, primary_key=True)
    previous_transaction_id = Column(TEXT)
    date = Column(DATE)
    transaction_type = Column("type", Enum(TransactionType))
    amount = Column(FLOAT)
    account_id = Column(
      UUID(as_uuid=True), ForeignKey("accounts.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    description = Column(TEXT)
    account_tag_id = Column(
        INTEGER, ForeignKey("account_tags.id", onupdate="CASCADE")
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    account = relationship(Account)
    account_tag = relationship(AccountTag)


def find_transaction(user_id: int, account_id: uuid, transaction_id: int, session: Session):
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


def list_transactions(
        user_id: int,
        account_id: uuid = None,
        period_type: int = None,
        period_offset: int = None,
        start_date: int = None,
        end_date: int = None,
        session: Session = None
) -> []:
    q = (
        session.query(Transaction).join(Account).join(User).filter(User.id == user_id)
    )

    if account_id:
        q = q.filter(Account.id == account_id)
    if period_type:
        start_date, end_date = get_date_rage(PeriodType(period_type), start_date, end_date)
        q = q.filter(between(Transaction.date, start_date, end_date))

    q = q.order_by(Transaction.date.desc())
    return [transaction for transaction in q.all()]


def get_date_rage(period_type: PeriodType, start_date: str, end_date: str):
    # if PeriodType(period_type) == PeriodType.CUSTOM:
    if PeriodType(period_type) == PeriodType.CURRENT_MONTH:
        today = date.today()
        month_range = calendar.monthrange(today.year, today.month)
        start_date = date.today().replace(day=1)
        end_date = start_date.replace(day=month_range[1])
    elif PeriodType(period_type) == PeriodType.LAST_MONTH:
        first = date.today().replace(day=1)
        end_date = first - datetime.timedelta(days=1)
        start_date = end_date.replace(day=1)

    return start_date, end_date


def get_balance(
    user_id: int,
    account_id: uuid = None,
    period_type: int = None,
    period_offset: int = None,
    start_date: int = None,
    end_date: int = None,
    session: Session = None
) -> (float, float, float):
    income = case((Transaction.amount >= 0.0, Transaction.amount), else_=0.0)
    expenses = case((Transaction.amount < 0.0, Transaction.amount), else_=0.0)
    q = (
        session.query(
            func.sum(Transaction.amount),
            func.sum(income),
            func.sum(expenses),
        ).join(Account).join(User).filter(User.id == user_id)
    )

    if account_id:
        q = q.filter(Account.id == account_id)
    if period_type:
        start_date, end_date = get_date_rage(PeriodType(period_type), start_date, end_date)
        q = q.filter(between(Transaction.date, start_date, end_date))

    result = q.one()
    return (
        round(result[0], 2) if result[0] else 0.0,
        round(result[1], 2) if result[1] else 0.0,
        round(result[2], 2) if result[2] else 0.0
    )
