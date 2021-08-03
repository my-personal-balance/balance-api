import calendar
import enum
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
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from balance_api.models import Base
from balance_api.models.tags import Tag
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

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    date = Column(DATE)
    transaction_type = Column("type", Enum(TransactionType))
    amount = Column(FLOAT)
    account_id = Column(
        INTEGER, ForeignKey("accounts.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    description = Column(TEXT)
    tag_id = Column(INTEGER, ForeignKey("tags.id", onupdate="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    account = relationship(Account)
    tag = relationship(Tag)


def create_transaction(user_id: int, transaction_resource, session: Session):
    transaction = Transaction(**transaction_resource)
    transaction.amount = abs(transaction.amount)
    session.add(transaction)
    session.commit()
    return transaction


def update_transaction(user_id: int, transaction_resource, session: Session):
    transaction = Transaction(**transaction_resource)
    transaction.amount = abs(transaction.amount)
    transaction.updated_at = datetime.utcnow()
    transaction = session.merge(transaction)
    session.commit()
    return transaction


def patch_transaction(
    user_id: int, transaction_resource, session: Session
) -> Transaction:
    transaction_data = Transaction(**transaction_resource)
    if transaction_data.id:
        q = (
            session.query(Transaction).filter(Transaction.id == transaction_data.id,)
        )
        try:
            transaction = q.one()
            if not transaction and transaction.account.user_id == user_id:
                raise NoResultFound

            if transaction_data.date:
                transaction.date = transaction_data.date
            if transaction_data.amount:
                transaction.amount = transaction_data.amount
            if transaction_data.description:
                transaction.description = transaction_data.description
            if transaction_data.tag_id:
                transaction.tag_id = transaction_data.tag_id

            transaction.updated_at = datetime.utcnow()
            transaction = session.merge(transaction)
            session.commit()

            return transaction

        except NoResultFound:
            return None


def find_transaction(
    user_id: int, account_id: int, transaction_id: int, session: Session
) -> Transaction:
    q = (
        session.query(Transaction)
        .join(Account)
        .filter(
            Account.user_id == user_id,
            Transaction.account_id == account_id,
            Transaction.id == transaction_id,
        )
    )
    try:
        return q.one()
    except NoResultFound:
        return None


def list_transactions(
    user_id: int,
    account_id: int = None,
    period_type: int = None,
    period_offset: int = None,
    start_date: str = None,
    end_date: str = None,
    session: Session = None,
) -> []:
    q = session.query(Transaction).join(Account).join(User).filter(User.id == user_id)

    if account_id:
        q = q.filter(Account.id == account_id)
    if period_type:
        start_date, end_date = get_date_rage(
            PeriodType(period_type), start_date, end_date
        )
        q = q.filter(between(Transaction.date, start_date, end_date))

    q = q.order_by(Transaction.date.desc())

    return [transaction for transaction in q.all()]


def get_date_rage(
    period_type: PeriodType, start_date: str, end_date: str
) -> (date, date):
    if PeriodType(period_type) == PeriodType.CURRENT_MONTH:
        today = date.today()
        month_range = calendar.monthrange(today.year, today.month)
        start_date = date.today().replace(day=1)
        end_date = start_date.replace(day=month_range[1])
    elif PeriodType(period_type) == PeriodType.LAST_MONTH:
        first = date.today().replace(day=1)
        end_date = first - timedelta(days=1)
        start_date = end_date.replace(day=1)
    elif PeriodType(period_type) == PeriodType.CUSTOM:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    return start_date, end_date


def get_balance(
    user_id: int,
    account_id: int = None,
    period_type: int = None,
    period_offset: int = None,
    start_date: str = None,
    end_date: str = None,
    session: Session = None,
) -> (float, float, float):
    income = case(
        (Transaction.transaction_type == TransactionType.INCOME, Transaction.amount),
        else_=0.0,
    )
    expenses = case(
        (Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount),
        else_=0.0,
    )
    q = (
        session.query(
            func.sum(income),
            func.sum(expenses),
        )
        .join(Account)
        .join(User)
        .filter(User.id == user_id)
    )

    if account_id:
        q = q.filter(Account.id == account_id)
    if period_type:
        start_date, end_date = get_date_rage(
            PeriodType(period_type), start_date, end_date
        )
        q = q.filter(between(Transaction.date, start_date, end_date))

    result = q.one()

    incomes = result[0] if result[0] else 0.0
    expenses = result[1] if result[1] else 0.0
    balance = incomes - expenses

    return (
        round(balance, 2),
        round(incomes, 2),
        round(expenses, 2),
    )


def delete_transaction(user_id: int, transaction_id: int, session: Session):
    q = (
        session.query(Transaction)
        .join(Account)
        .where(Transaction.id == transaction_id, Account.user_id == user_id)
    )
    transaction = q.one()
    if transaction:
        session.delete(transaction)
        session.commit()


def get_daily_balance(
    user_id: int,
    account_id: int,
    period_type: int,
    period_offset: int,
    start_date: str,
    end_date: str,
    session: Session,
):
    incomes = case(
        (Transaction.transaction_type == TransactionType.INCOME, Transaction.amount),
        else_=0.0,
    )
    expenses = case(
        (Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount),
        else_=0.0,
    )

    q = (
        session.query(
            Transaction.date,
            func.sum(incomes) - func.sum(expenses),
        )
        .join(Account)
        .where(Account.user_id == user_id)
    )

    if account_id:
        q = q.filter(Account.id == account_id)

    q = q.group_by(
        Transaction.date,
    ).order_by(Transaction.date)

    daily_balance = []
    prev_day_balance = 0.0
    for balance in q.all():
        prev_day_balance += balance[1]
        daily_balance.append((balance[0], prev_day_balance))

    if period_type:
        start_date, end_date = get_date_rage(
            PeriodType(period_type), start_date, end_date
        )

        balances_dict = dict(daily_balance)

        last_value = None

        balances = []
        for days in range(0, (end_date - start_date).days):
            current_day = start_date + timedelta(days=days)

            current_value = balances_dict.get(current_day, None)
            if not last_value:
                last_value = current_value

            if not current_value and last_value:
                current_value = last_value

            balances.append((current_day, current_value))

        return balances

    return daily_balance
