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
    type = Column(Enum(AccountType))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
