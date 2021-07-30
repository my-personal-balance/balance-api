from datetime import datetime

from sqlalchemy import (
    Column,
    INTEGER,
    TEXT,
    ForeignKey,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from balance_api.models import Base
from balance_api.models.users import User


class Tag(Base):
    __tablename__ = "tags"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    value = Column(TEXT)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship(User)


def list_tags(user_id: int, session: Session) -> []:
    return session.query(Tag).where(Tag.user_id == user_id).order_by(Tag.id).all()


def find_or_create_account_tag(user_id: int, tag_value: str, session: Session) -> Tag:
    q = session.query(Tag).where(Tag.user_id == user_id, Tag.value == tag_value)
    try:
        return q.one()
    except NoResultFound:
        tag = Tag(value=tag_value, user_id=user_id)
        session.add(tag)
        session.commit()
        return tag
