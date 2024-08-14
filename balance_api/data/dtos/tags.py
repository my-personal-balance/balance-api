from dataclasses import dataclass
from typing import List

from balance_api.data.models.tags import Tag as m_Tag


@dataclass
class Tag:
    id: int
    value: str
    user_id: int

    @classmethod
    def serialize(cls, tag: m_Tag):
        return Tag(tag.id, tag.value, tag.user_id) if tag else None

    @classmethod
    def serialize_many(cls, tags: List[m_Tag]):
        return [cls.serialize(tag) for tag in tags]
