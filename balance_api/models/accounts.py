import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    INTEGER,
    TEXT,
    ForeignKey,
    Enum,
    DateTime,
)
from sqlalchemy.exc import NoResultFound, DataError
from sqlalchemy.orm.session import Session

from balance_api.models import Base


class AccountType(enum.Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    INVESTMENTS = "INVESTMENTS"
    OTHERS = "OTHERS"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    alias = Column(TEXT)
    user_id = Column(
        INTEGER, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    type = Column(Enum(AccountType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def find_account(user_id: int, account_id: int, session: Session):
    q = session.query(Account).where(
        Account.user_id == user_id, Account.id == account_id
    )
    try:
        return q.one()
    except NoResultFound:
        return None
    except DataError:
        return None


def list_accounts(user_id: int, session: Session):
    return (
        session.query(Account)
        .where(Account.user_id == user_id)
        .order_by(Account.created_at)
    ).all()


def create_account(account_resource, session: Session):
    new_account = Account(**account_resource)
    session.add(new_account)
    session.commit()
    return new_account


def delete_account(user_id: int, account_id: int, session: Session):
    account = find_account(user_id, account_id, session)
    if account:
        session.delete(account)
        session.commit()