from balance_api.data.models.tags import (
    Tag,
    find_tag as find_tag_db,
    list_tags as list_tags_db,
    find_or_create_account_tag,
)
from sqlalchemy.orm.session import Session
from typing import List


class TagService:
    def __init__(self, session: Session):
        self.session = session

    def create_tag(self, user_id: int, tag_value: str) -> Tag:
        return find_or_create_account_tag(user_id, tag_value, self.session)
    
    def find_tag(self, user_id: int, tag_id: int) -> Tag:
        return find_tag_db(user_id, tag_id, self.session)
    
    def list_tags(self, user_id: int) -> List[Tag]:
        return list_tags_db(user_id, self.session)
    
    def init_tags_for_user(self, user_id: int) -> List[Tag]:
        tags = [
            "Miscellaneous",
            "ATM",
            "Transport & Car",
            "Food & Groceries",
            "Bars & Restaurants",
            "Insurances & Finances",
            "Media & Electronics",
            "Shopping",
            "Household & Utilities",
            "Travel & Holidays",
            "Leisure & Entertainment",
            "Healthcare & Drug Stores",
            "Subscriptions & Donations",
            "Salary",
            "Family & Friends",
            "Education",
            "Income",
            "Tax & Fines",
            "Business expenses",
            "Savings & Investments",
        ]
        return [self.create_tag(user_id, tag) for tag in tags]