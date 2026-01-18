import requests
import logging
from sqlalchemy.orm.session import Session
from balance_api.services.transactions import TransactionService
from balance_api import config

logger = logging.getLogger(__name__)


class AutoClassifyService:

    def __init__(self, session: Session):
        self.session = session

    def classify(self, user_id: int, transaction_ids: list[int]):
        logger.info(f"Classifying transactions for user {user_id}")
        response = requests.post(f"{config.CLASSIFY_HOST}/{user_id}/classify/pre-load")
        logger.info(response.json())

        transaction_service = TransactionService(self.session)
        transaction_descriptions = []
        for transaction_id in transaction_ids:
            t = transaction_service.get_transaction(user_id, transaction_id)
            if t:
                response = requests.post(
                    f"{config.CLASSIFY_HOST}/{user_id}/classify",
                    json={"text": t.description},
                )
                data = response.json()
                transaction_descriptions.append(
                    {
                        "id": t.id,
                        "category": data["category"],
                        "confidence_level": data["confidence_level"],
                    }
                )

        return transaction_descriptions
