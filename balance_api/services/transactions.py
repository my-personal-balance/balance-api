from sqlalchemy.orm.session import Session
from balance_api.data.models.transactions import find_transaction
from balance_api.data.models.transactions import Transaction


class TransactionService:
    def __init__(self, session: Session):
        self.session = session

    def get_transaction(self, user_id: int, transaction_id: int) -> Transaction | None:
        return find_transaction(user_id, transaction_id, self.session)
