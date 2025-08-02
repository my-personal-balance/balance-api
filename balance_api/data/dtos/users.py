from dataclasses import dataclass
from typing import List

from balance_api.data.models.users import User as m_User


@dataclass
class User:
    id: int
    name: str
    email: str
    currency: str

    @classmethod
    def serialize(cls, user: m_User):
        return User(user.id, user.name, user.email, user.currency.value)

    @classmethod
    def serializer_many(cls, users: List[m_User]):
        return [cls.serialize(user) for user in users]
