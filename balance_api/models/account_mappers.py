import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Enum,
    INTEGER,
    JSON,
)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from balance_api.models import Base
from balance_api.models.accounts import Account


class SourceFileType(enum.Enum):
    CSV = "text/csv"
    XLS = "application/vnd.ms-excel"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class AccountMapper(Base):
    __tablename__ = "account_mappers"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    account_id = Column(
        INTEGER, ForeignKey("accounts.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    source_file_type = Column(Enum(SourceFileType))
    source_file_schema = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    account = relationship(Account)


def find_account_mapper(
    user_id: int, account_id: int, session: Session
) -> AccountMapper:
    q = (
        session.query(AccountMapper)
        .join(Account)
        .filter(
            Account.user_id == user_id,
            AccountMapper.account_id == account_id,
        )
    )
    try:
        return q.one()
    except NoResultFound:
        return None
