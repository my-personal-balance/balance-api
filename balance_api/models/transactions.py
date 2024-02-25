import calendar
import enum
from datetime import datetime, date, timedelta
from typing import List

from sqlalchemy import (
    Column,
    INTEGER,
    TEXT,
    ForeignKey,
    Enum,
    DATE,
    FLOAT,
    DateTime,
    extract,
)
from sqlalchemy import func, case, between
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.orm.session import Session

from balance_api.models import Base
from balance_api.models.accounts import Account
from balance_api.models.tags import Tag
from balance_api.models.users import User
from balance_api.models.split_transactions import SplitTransaction


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
    CURRENT_YEAR = "current_year"
    LAST_YEAR = "last_year"
    LAST_3_MONTHS = "last_3_months"
    LAST_6_MONTHS = "last_6_months"
    LAST_12_MONTHS = "last_12_months"


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

    split_transactions: Mapped[List["SplitTransaction"]] = relationship()

    balance = 0.0


def create_transaction(user_id: int, transaction_resource, session: Session):
    transaction = Transaction(**transaction_resource)
    transaction.amount = abs(transaction.amount) if transaction.amount else 0.0
    session.add(transaction)
    session.commit()
    return transaction


def update_transaction(user_id: int, transaction_resource, session: Session):
    transaction = Transaction(**transaction_resource)
    transaction.amount = abs(transaction.amount) if transaction.amount else 0.0
    transaction.updated_at = datetime.utcnow()
    transaction = session.merge(transaction)
    session.commit()
    return transaction


def patch_transaction(user_id: int, transaction_resource, session: Session):
    transaction_data = Transaction(**transaction_resource)
    if transaction_data.id:
        q = session.query(Transaction).filter(
            Transaction.id == transaction_data.id,
        )
        try:
            transaction = q.one()
            if not transaction and transaction.account.user_id == user_id:
                raise NoResultFound

            if transaction_data.date:
                transaction.date = transaction_data.date
            if transaction_data.transaction_type:
                transaction.transaction_type = transaction_data.transaction_type
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


def find_transaction(user_id: int, transaction_id: int, session: Session):
    q = (
        session.query(Transaction)
        .join(Account)
        .filter(
            Account.user_id == user_id,
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
    tag_id: int = None,
    period_type: int = None,
    period_offset: int = None,
    start_date: str = None,
    end_date: str = None,
    max_results: int = None,
    session: Session = None,
) -> []:
    q = session.query(Transaction).join(Account).join(User).filter(User.id == user_id)

    if account_id:
        q = q.filter(Account.id == account_id)

    if tag_id:
        q = q.filter(Transaction.tag_id == tag_id)
    elif tag_id == 0:
        q = q.filter(Transaction.tag_id == None)

    q = q.order_by(Transaction.date.asc(), Transaction.id)

    if period_type:
        start_date, end_date = get_date_rage(
            PeriodType(period_type), start_date, end_date
        )

    transactions = []
    t_balance = 0.0
    for transaction in q.all():
        if TransactionType.INCOME == transaction.transaction_type:
            t_balance += transaction.amount
        elif (
            TransactionType.TRANSFER == transaction.transaction_type
            or TransactionType.EXPENSE == transaction.transaction_type
        ):
            t_balance -= transaction.amount
        transaction.balance = t_balance

        if period_type:
            if end_date >= transaction.date >= start_date:
                transactions.append(transaction)
        else:
            transactions.append(transaction)

    transactions = transactions[::-1]

    return transactions[:max_results] if max_results else transactions


def get_date_rage(
    period_type: PeriodType, start_date: str | None, end_date: str | None
) -> (date, date):
    if PeriodType(period_type) == PeriodType.CURRENT_MONTH:
        today = date.today()
        month_range = calendar.monthrange(today.year, today.month)
        start_date = date.today().replace(day=1)
        end_date = start_date.replace(day=month_range[1])
    if PeriodType(period_type) == PeriodType.LAST_MONTH:
        first = date.today().replace(day=1)
        end_date = first - timedelta(days=1)
        start_date = go_back_in_time(date.today(), 1)
    elif PeriodType(period_type) == PeriodType.CURRENT_YEAR:
        current_year = date.today().year
        start_date = date.today().replace(day=1, month=1, year=current_year)
        end_date = date.today()
    elif PeriodType(period_type) == PeriodType.LAST_YEAR:
        last_year = date.today().year - 1
        start_date = date.today().replace(day=1, month=1, year=last_year)
        end_date = date.today().replace(day=31, month=12, year=last_year)
    elif PeriodType(period_type) == PeriodType.LAST_3_MONTHS:
        first = date.today().replace(day=1)
        end_date = first - timedelta(days=1)
        start_date = go_back_in_time(date.today(), 3)
    elif PeriodType(period_type) == PeriodType.LAST_6_MONTHS:
        first = date.today().replace(day=1)
        end_date = first - timedelta(days=1)
        start_date = go_back_in_time(date.today(), 6)
    elif PeriodType(period_type) == PeriodType.LAST_12_MONTHS:
        first = date.today().replace(day=1)
        end_date = first - timedelta(days=1)
        start_date = go_back_in_time(date.today(), 12)
    elif PeriodType(period_type) == PeriodType.CUSTOM:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    return start_date, end_date


def go_back_in_time(current_date, months=0):
    my_date = date(current_date.year, current_date.month, 1)
    for m in range(months):
        my_date -= timedelta(days=1)
        my_date = my_date.replace(day=1)
    return my_date


def get_balance(
    user_id: int,
    account_id: int = None,
    tag_id: int = None,
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
    transfers = case(
        (Transaction.transaction_type == TransactionType.TRANSFER, Transaction.amount),
        else_=0.0,
    )
    q = (
        session.query(
            func.sum(income),
            func.sum(expenses),
            func.sum(transfers),
        )
        .join(Account)
        .join(User)
        .filter(User.id == user_id)
    )

    if account_id:
        q = q.filter(Account.id == account_id)

    if tag_id:
        q = q.filter(Transaction.tag_id == tag_id)
    elif tag_id == 0:
        q = q.filter(Transaction.tag_id == None)

    if period_type:
        start_date, end_date = get_date_rage(
            PeriodType(period_type), start_date, end_date
        )
        q = q.filter(between(Transaction.date, start_date, end_date))

    result = q.one()

    incomes = result[0] if result[0] else 0.0
    expenses = result[1] if result[1] else 0.0
    transfers = result[2] if result[2] else 0.0
    incomes -= transfers
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


def list_group_by_tag(
    user_id: int,
    account_id: int,
    tag_id: int,
    period_type: int,
    period_offset: int,
    start_date: str,
    end_date: str,
    session: Session,
):
    income = case(
        (Transaction.transaction_type == TransactionType.INCOME, Transaction.amount),
        else_=0.0,
    )
    expenses = case(
        (Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount),
        else_=0.0,
    )
    transfers = case(
        (Transaction.transaction_type == TransactionType.TRANSFER, Transaction.amount),
        else_=0.0,
    )

    q = (
        session.query(
            func.sum(income),
            func.sum(expenses),
            func.sum(transfers),
            Tag,
        )
        .join(Account)
        .join(Tag, isouter=True)
        .filter(Account.user_id == user_id)
    )

    if account_id:
        q = q.filter(Account.id == account_id)

    if tag_id:
        q = q.filter(Tag.id == tag_id)
    elif tag_id == 0:
        q = q.filter(Tag.id == None)

    if period_type:
        start_date, end_date = get_date_rage(
            PeriodType(period_type), start_date, end_date
        )
        q = q.filter(between(Transaction.date, start_date, end_date))

    q = q.group_by(
        Tag,
    ).order_by(Tag.value)

    items = []
    for result in q.all():
        incomes = result[0] if result[0] else 0.0
        expenses = result[1] if result[1] else 0.0
        transfers = result[2] if result[2] else 0.0
        tag = result[3]

        items.append(
            {
                "tag": tag,
                TransactionType.INCOME.name: round(incomes, 2),
                TransactionType.EXPENSE.name: round(expenses, 2),
                TransactionType.TRANSFER.name: round(transfers, 2),
            }
        )

    return items


def get_montly_balance(
    user_id: int,
    account_id: int = None,
    tag_id: int = None,
    session: Session = None,
) -> []:
    income = case(
        (Transaction.transaction_type == TransactionType.INCOME, Transaction.amount),
        else_=0.0,
    )
    expenses = case(
        (Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount),
        else_=0.0,
    )
    transfers = case(
        (Transaction.transaction_type == TransactionType.TRANSFER, Transaction.amount),
        else_=0.0,
    )

    year_stmt = extract("year", Transaction.date)
    month_stmt = extract("month", Transaction.date)

    q = (
        session.query(
            year_stmt,
            month_stmt,
            func.sum(income),
            func.sum(expenses),
            func.sum(transfers),
        )
        .join(Account)
        .join(User)
        .filter(User.id == user_id)
    )

    if account_id:
        q = q.filter(Account.id == account_id)

    if tag_id:
        q = q.filter(Transaction.tag_id == tag_id)
    elif tag_id == 0:
        q = q.filter(Transaction.tag_id == None)

    q = q.group_by(year_stmt, month_stmt).order_by(year_stmt, month_stmt)

    items = []
    for result in q.all():
        month = datetime.strptime(f"{int(result[0])}-{int(result[1])}", "%Y-%m")
        month = datetime.strftime(month, "%b %Y")
        incomes = result[2] if result[2] else 0.0
        expenses = result[3] if result[3] else 0.0
        transfers = result[4] if result[4] else 0.0

        items.append(
            {
                "month": month,
                TransactionType.INCOME.name: round(incomes, 2),
                TransactionType.EXPENSE.name: round(expenses, 2),
                TransactionType.TRANSFER.name: round(transfers, 2),
            }
        )

    return items[-12:]
