from datetime import datetime

from sqlalchemy import (
    Column,
    TEXT,
    ForeignKey,
    DateTime,
    PrimaryKeyConstraint,
    INTEGER,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from balance_api.exceptions import AssetNotFoundException
from balance_api.models import Base
from balance_api.models.assets import Asset, find_asset
from balance_api.models.transactions import Transaction


class TransactionAsset(Base):
    __tablename__ = "transaction_assets"
    __table_args__ = (
        PrimaryKeyConstraint('transaction_id', 'asset_isin'),
    )

    transaction_id = Column(
        INTEGER, ForeignKey("transactions.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    asset_isin = Column(
        TEXT, ForeignKey("assets.isin", onupdate="CASCADE", ondelete="CASCADE")
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    transaction = relationship(Transaction)
    asset = relationship(Asset)


def create_transaction_asset(
        transaction: Transaction, asset: Asset, session: Session
) -> TransactionAsset:
    transaction_asset = TransactionAsset()
    transaction_asset.transaction = transaction
    transaction_asset.asset = asset

    session.add(transaction_asset)
    session.commit()

    return transaction_asset


def create_transaction_asset_with_isin(
        transaction: Transaction, isin: str, session: Session
) -> TransactionAsset:
    asset = find_asset(isin, session)
    if not asset:
        raise AssetNotFoundException(detail=f"Asset {isin} not found.")

    return create_transaction_asset(
        transaction=transaction,
        asset=asset,
        session=session
    )
