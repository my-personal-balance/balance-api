from datetime import datetime

from sqlalchemy import (
    Column,
    FLOAT,
    TEXT,
    DateTime,
)

from balance_api.models import Base


class Asset(Base):
    __tablename__ = "assets"

    isin = Column(TEXT, primary_key=True)
    price = Column(FLOAT)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
