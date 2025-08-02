from datetime import datetime, UTC

from sqlalchemy import (
    ForeignKey,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.orm.session import Session

from balance_api.data.models import Base
from balance_api.data.models.assets import Asset, find_asset
from balance_api.data.models.transactions import Transaction


class TransactionAsset(Base):
    __tablename__ = "transaction_assets"
    __table_args__ = (PrimaryKeyConstraint("transaction_id", "asset_isin"),)

    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    asset_isin: Mapped[str] = mapped_column(
        ForeignKey("assets.isin", onupdate="CASCADE", ondelete="CASCADE")
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), nullable=False
    )

    transaction: Mapped["Transaction"] = relationship(Transaction)
    asset: Mapped["Asset"] = relationship(Asset)


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
        raise ValueError(f"Asset {isin} not found.")

    return create_transaction_asset(
        transaction=transaction, asset=asset, session=session
    )
