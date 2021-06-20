import enum
import uuid
from datetime import datetime

from meza.io import read_csv
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

from balance_api.connection.db import database_operation
from balance_api.models.account_tags import AccountTag
from balance_api.models.transactions import Transaction, TransactionType
from balance_api.transactions.mappings import n26


class SourceFileType(enum.Enum):
    CSV = "csv"


def transform_records(records, mapping: dict, account_id: int, session: Session):

    for r in records:
        tag_value = mapping.get('tag')(r)
        account_tag = find_or_create_account_tag(session, account_id, tag_value)
        amount = float(mapping.get('amount')(r))

        yield Transaction(
            date=mapping.get('date')(r),
            transaction_type=mapping.get('type')(r),
            amount=amount,
            description=mapping.get('description')(r),
            account_id=account_id,
            account_tag=account_tag,
        )


def find_or_create_account_tag(session: Session, account_id: int, tag_value: str):
    q = (
        session.query(
            AccountTag
        ).where(
            AccountTag.account_id == account_id,
            AccountTag.value == tag_value
        )
    )
    try:
        account_tag = q.one()
    except NoResultFound:
        account_tag = AccountTag(
            value=tag_value,
            account_id=account_id
        )
        session.add(account_tag)
        session.commit()

    return account_tag


@database_operation(max_tries=3)
def load_file(file_path: str, source_type: SourceFileType, mapping: dict, account_id: int, session: Session):
    records = None
    if source_type == SourceFileType.CSV:
        records = read_csv(file_path)

    if records:
        for transaction in transform_records(records, mapping, account_id=account_id, session=session):
            transaction.id = uuid.uuid4()
            session.add(transaction)

        session.commit()


# For running locally
if __name__ == "__main__":
    load_file('/Users/julianovidal/Downloads/n26-csv-transactions.csv', SourceFileType.CSV, n26.mapping, 1)
