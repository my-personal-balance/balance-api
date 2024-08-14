import enum
from datetime import datetime, UTC

from sqlalchemy import (
    ForeignKey,
)
from sqlalchemy.exc import NoResultFound, DataError
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.session import Session

from balance_api.data.models import Base, CurrencyType


class AccountType(enum.Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    INVESTMENTS = "INVESTMENTS"
    OTHERS = "OTHERS"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alias: Mapped[str]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    type: Mapped[AccountType] = mapped_column(nullable=False)
    currency: Mapped[CurrencyType]

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), nullable=False
    )


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


def create_account(account_resource, session: Session) -> Account:
    new_account = Account(**account_resource)
    session.add(new_account)
    session.commit()
    return new_account


def delete_account(user_id: int, account_id: int, session: Session):
    account = find_account(user_id, account_id, session)
    if account:
        session.delete(account)
        session.commit()
