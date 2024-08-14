from datetime import datetime, UTC

from sqlalchemy import or_
from sqlalchemy import (
    select,
)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.session import Session

from balance_api.data.models import Base, CurrencyType


class Asset(Base):
    __tablename__ = "assets"

    isin: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str]
    currency: Mapped[CurrencyType]
    price: Mapped[float]

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), nullable=False
    )


def find_asset(isin: str, session: Session) -> Asset | None:
    try:
        return session.get(Asset, isin)
    except NoResultFound:
        return None


def search_assets(keyword: str, session: Session):
    stmt = select(Asset).where(
        or_(Asset.isin.like(f"%{keyword}%"), Asset.description.like(f"%{keyword}%"))
    )

    return session.scalars(stmt).all()
