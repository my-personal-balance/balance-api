from datetime import datetime

from sqlalchemy import (
    Column,
    FLOAT,
    TEXT,
    DateTime,
)
from sqlalchemy import or_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

from balance_api.models import Base


class Asset(Base):
    __tablename__ = "assets"

    isin = Column(TEXT, primary_key=True)
    description = Column(TEXT)
    currency = Column(TEXT)
    price = Column(FLOAT)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def find_asset(isin: str, session: Session) -> Asset:
    q = (
        session.query(Asset).where(Asset.isin == isin)
    )
    try:
        return q.one()
    except NoResultFound:
        return None


def search_assets(keyword: str, session: Session):
    q = (
        session.query(Asset).filter(
            or_(
                Asset.isin.like(f"%{keyword}%"),
                Asset.description.like(f"%{keyword}%")
            )
        )
    )
    return q.all()
