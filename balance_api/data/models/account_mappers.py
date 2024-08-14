import enum
from datetime import datetime, UTC

from sqlalchemy import (
    ForeignKey,
    JSON,
)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.orm.session import Session

from balance_api.data.models import Base
from balance_api.data.models.accounts import Account


class SourceFileType(enum.Enum):
    CSV = "text/csv"
    XLS = "application/vnd.ms-excel"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class AccountMapper(Base):
    __tablename__ = "account_mappers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    source_file_type: Mapped[SourceFileType]
    source_file_schema: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), nullable=False
    )

    account: Mapped["Account"] = relationship(Account)


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
