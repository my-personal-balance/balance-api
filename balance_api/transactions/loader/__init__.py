import enum
import uuid

from meza.io import read_csv, read_xls
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

from balance_api.models.account_tags import AccountTag
from balance_api.models.transactions import Transaction


class SourceFileType(enum.Enum):
    CSV = "csv"
    XLS = "xls"


def transform_records(records, mapping: dict, account_id: uuid, session: Session):

    for record in records:
        tag_value = mapping.get('tag')(record)

        account_tag = None
        if tag_value:
            account_tag = find_or_create_account_tag(session, account_id, tag_value)

        amount = float(mapping.get('amount')(record))

        yield Transaction(
            date=mapping.get('date')(record),
            transaction_type=mapping.get('type')(record),
            amount=abs(amount),
            description=mapping.get('description')(record),
            account_id=account_id,
            account_tag=account_tag,
        )


def find_or_create_account_tag(session: Session, account_id: uuid, tag_value: str):
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


def process_transactions_file(
    file_stream,
    source_type: SourceFileType,
    mapping: dict,
    account_id: uuid,
    session: Session
):
    records = None
    if source_type == SourceFileType.CSV:
        records = read_csv(file_stream)
    elif source_type == SourceFileType.XLS:
        records = read_xls(file_stream)

    if records:
        for transaction in transform_records(records, mapping, account_id=account_id, session=session):
            session.add(transaction)

        session.commit()
