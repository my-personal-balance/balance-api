import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    INTEGER,
    TEXT,
    ForeignKey,
    Enum,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

from balance_api.models import Base


class AccountType(enum.Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    INVESTMENTS = "INVESTMENTS"
    OTHERS = "OTHERS"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alias = Column(TEXT)
    user_id = Column(
      INTEGER, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    type = Column(Enum(AccountType))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


def find_account(user_id: int, account_id: uuid, session: Session):
    q = (
        session.query(Account).where(Account.user_id == user_id, Account.id == account_id)
    )
    try:
        return q.one()
    except NoResultFound:
        return None


def list_accounts(user_id: int, session: Session):
    q = (
        session.query(Account).where(Account.user_id == user_id).order_by(Account.created_at)
    )
    return [account for account in q.all()]


def create_account(account_resource, session: Session):
    new_account = Account(**account_resource)
    session.add(new_account)
    session.commit()
    return new_account

