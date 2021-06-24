from datetime import datetime

from sqlalchemy import (
    Column,
    INTEGER,
    TEXT,
    DateTime,
)

from balance_api.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(TEXT)
    email = Column(TEXT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
