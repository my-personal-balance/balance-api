from datetime import datetime

from sqlalchemy import (
    Column,
    INTEGER,
    TEXT,
    ForeignKey,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from balance_api.models import Base
from balance_api.models.accounts import Account


class AccountTag(Base):
    __tablename__ = "account_tags"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    value = Column(TEXT)
    account_id = Column(
      UUID(as_uuid=True), ForeignKey("accounts.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    account = relationship(Account)
