from datetime import datetime, UTC

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError

from balance_api.data.models import Base, CurrencyType


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    currency: Mapped[CurrencyType] = mapped_column(default=CurrencyType.EUR)

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now(UTC)
    )


def authenticate(email: str, password: str, session: Session):
    q = session.query(User).filter(User.email == email)
    try:
        return q.one()
    except NoResultFound:
        return None


def find_user(user_id: int, session: Session) -> User | None:
    try:
        return session.get(User, user_id)
    except NoResultFound:
        return None


def create_user(user: dict, session: Session) -> User:
    new_user = User(**user)
    session.add(new_user)
    try:
        session.commit()
        return new_user
    except IntegrityError as e:
        session.rollback()
        raise ValueError(f"User with email {user['email']} already exists")