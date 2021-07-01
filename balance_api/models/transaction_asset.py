from datetime import datetime

from sqlalchemy import (
    Column,
    FLOAT,
    TEXT,
    ForeignKey,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from balance_api.models import Base
from balance_api.models.transactions import Transaction
from balance_api.models.assets import Asset


class TransactionAsset(Base):
    __tablename__ = "transaction_assets"

    transaction_id = Column(
        UUID(as_uuid=True), ForeignKey("transaction.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True,
    )
    asset_isin = Column(
        TEXT, ForeignKey("assets.isin", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True
    )
    amount = Column(FLOAT, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    transaction = relationship(Transaction)
    asset = relationship(Asset)
