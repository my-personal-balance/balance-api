from datetime import datetime

from sqlalchemy import (
    Column,
    INTEGER,
    TEXT,
    DateTime,
)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

from balance_api.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(TEXT)
    email = Column(TEXT)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def authenticate(email: str, password: str, session: Session):
    q = session.query(User).filter(User.email == email)
    try:
        return q.one()
    except NoResultFound:
        return None
