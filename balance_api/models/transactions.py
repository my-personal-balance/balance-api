import calendar
import enum
import uuid
from datetime import datetime, date, timedelta

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
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"
    TRANSFER = "TRANSFER"
    REFUND = "REFUND"
    INVESTMENT = "INVESTMENT"
    IOU = "IOU"


class PeriodType(enum.Enum):
    CUSTOM = "custom"
    CURRENT_MONTH = "current_month"
    LAST_MONTH = "last_month"
    LAST_YEAR = "last_year"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    prev_transaction_id = Column(UUID(as_uuid=True))
    balance = Column(FLOAT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    account = relationship(Account)
    account_tag = relationship(AccountTag)


def create_transaction(transaction_resource, session: Session):
    new_transaction = Transaction(**transaction_resource)
    new_transaction.amount = abs(new_transaction.amount)
    session.add(new_transaction)
    session.commit()
    return new_transaction


def find_transaction(user_id: int, account_id: uuid, transaction_id: int, session: Session):
    q = (
        session.query(Transaction).join(Account).filter(
            Account.user_id == user_id,
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
        start_date: str = None,
        end_date: str = None,
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

    q = q.order_by(Transaction.date.desc(), Transaction.balance.asc(),)

    if not account_id:
        return [transaction for transaction in q.all()]
    else:
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
        end_date = first - timedelta(days=1)
        start_date = end_date.replace(day=1)

    return start_date, end_date


def get_balance(
    user_id: int,
    account_id: uuid = None,
    period_type: int = None,
    period_offset: int = None,
    start_date: str = None,
    end_date: str = None,
    session: Session = None
) -> (float, float, float):
    income = case((Transaction.transaction_type == TransactionType.INCOME, Transaction.amount), else_=0.0)
    expenses = case((Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount), else_=0.0)
    q = (
        session.query(
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

    incomes = result[0] if result[0] else 0.0
    expenses = result[1] if result[1] else 0.0
    balance = incomes - expenses

    return (
        round(balance, 2), round(incomes, 2), round(expenses, 2),
    )


def delete_transaction(user_id: int, transaction_id: int, session: Session):
    q = (
        session.query(Transaction).join(Account).where(
            Transaction.id == transaction_id, Account.user_id == user_id
        )
    )
    transaction = q.one()
    if transaction:
        prev_transaction_id = transaction.prev_transaction_id
        session.delete(transaction)

        update_session_ops(user_id, transaction_id, prev_transaction_id, session)

        session.commit()


def update_transaction_list(user_id: int, account_id: int, session: Session):
    q = (
        session.query(Transaction).join(Account).filter(
            Account.id == account_id,
            Account.user_id == user_id
        ).order_by(Transaction.date.asc())
    )

    prev_transaction: Transaction = None
    for transaction in q.all():
        if prev_transaction:
            transaction.prev_transaction_id = prev_transaction.id
            transaction.updated_at = datetime.now()

            if transaction.transaction_type == TransactionType.INCOME:
                transaction.balance = prev_transaction.balance + transaction.amount
            elif transaction.transaction_type == TransactionType.EXPENSE:
                transaction.balance = prev_transaction.balance - transaction.amount

            transaction = session.merge(transaction)

            prev_transaction = transaction
        else:
            prev_transaction = transaction
            prev_transaction.balance = prev_transaction.amount

    session.commit()


def update_session_ops(user_id: int, transaction_id: uuid, prev_transaction_id: uuid, session: Session):
    q = (
        session.query(Transaction).join(Account).where(
            Transaction.prev_transaction_id == transaction_id, Account.user_id == user_id
        )
    )

    next_transaction = q.one()
    next_transaction.prev_transaction_id = prev_transaction_id
    session.merge(next_transaction)


def get_init_balance(user_id: int, last_transaction_date: datetime, session: Session):
    q = (
        session.query(
            Transaction.account_id,
            func.max(Transaction.date),
        ).join(Account).join(User).filter(
            User.id == user_id,
            Transaction.date <= last_transaction_date,
        ).group_by(Transaction.account_id)
    )

    init_balance = 0.0
    for result in q.all():
        account_id = result[0]
        transaction_date = result[1]

        q = (
            session.query(Transaction.balance).join(Account).join(User).filter(
                User.id == user_id,
                Account.id == account_id,
                Transaction.date == transaction_date,
            ).order_by(Transaction.balance.desc()).limit(1)
        )

        init_balance += q.scalar()

    return init_balance
