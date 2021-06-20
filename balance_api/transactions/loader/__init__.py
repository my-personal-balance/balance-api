import enum
import uuid
from datetime import datetime

from meza.io import read_csv
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import NoResultFound

from balance_api.connection.db import database_operation
from balance_api.models.account_tags import AccountTag
from balance_api.models.transactions import Transaction, TransactionType


class SourceFileType(enum.Enum):
    CSV = "csv"


def transform_records(records, account_id: int, session: Session):
    """
    {
        'Date': '2021-06-19',
        'Payee': 'PAYPAL *COMIXOLOGY',
        'Account number': '',
        'Transaction type': 'MasterCard Payment',
        'Payment reference': '',
        'Category': 'Shopping',
        'Amount (EUR)': '-7.13',
        'Amount (Foreign Currency)': '-7.13',
        'Type Foreign Currency': 'EUR',
        'Exchange Rate': '1.0'
    }
    """
    for r in records:
        account_tag = find_or_create_account_tag(session, account_id, r.get("Category"))
        amount = float(r.get("Amount (EUR)"))
        transaction_type = TransactionType.EXPENSE if amount < 0.0 else TransactionType.INCOME
        yield Transaction(
            date=datetime.strptime(r.get('Date'), "%Y-%M-%d"),
            transaction_type=transaction_type,
            amount=amount,
            description=r.get("Payee"),
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
def load_file(file_path: str, source_type: SourceFileType, account_id: int, session: Session):
    records = read_csv(file_path)
    for transaction in transform_records(records, account_id=account_id, session=session):
        transaction.id = uuid.uuid4()
        session.add(transaction)

    session.commit()
