import enum
import tempfile
import uuid
from werkzeug.datastructures import FileStorage
from meza.io import read_csv, read_xls
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

from balance_api.models.account_tags import AccountTag
from balance_api.models.transactions import Transaction, update_transaction_list
from balance_api.transactions.mappings import (
    n26,
    openbank
)
from balance_api.transactions import LoadTransactionFileException


class SourceFileType(enum.Enum):
    CSV = 'text/csv'
    XLS = 'application/vnd.ms-excel'
    XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


class TransactionFileLoader:

    def __init__(self, file: FileStorage, user_id: int, account_id: uuid, session: Session):
        self.file = file
        self.user_id = user_id
        self.account_id = account_id
        self.session = session
        self.source_file_type = SourceFileType(file.content_type)

    def __read_file(self, temp_file):
        if SourceFileType.CSV == self.source_file_type:
            return read_csv(temp_file.name)
        elif self.source_file_type in [SourceFileType.XLS, SourceFileType.XLSX]:
            return read_xls(temp_file.name)

    def __guess_mapping(self, records) -> dict:
        if SourceFileType.CSV == self.source_file_type:
            return n26.mapping
        elif self.source_file_type in [SourceFileType.XLS, SourceFileType.XLSX]:
            return openbank.mapping

    def __transform_records(self, records, mapping: dict):
        for record in records:
            tag_value = mapping.get('tag')(record)

            account_tag = None
            if tag_value:
                account_tag = self.__find_or_create_account_tag(tag_value)

            amount = float(mapping.get('amount')(record))

            yield Transaction(
                date=mapping.get('date')(record),
                transaction_type=mapping.get('type')(record),
                amount=abs(amount),
                description=mapping.get('description')(record),
                account_id=self.account_id,
                account_tag=account_tag,
                balance=0.0,
            )

    def __find_or_create_account_tag(self, tag_value: str):
        q = (
            self.session.query(
                AccountTag
            ).where(
                AccountTag.account_id == self.account_id,
                AccountTag.value == tag_value
            )
        )
        try:
            account_tag = q.one()
        except NoResultFound:
            account_tag = AccountTag(
                value=tag_value,
                account_id=self.account_id
            )
            self.session.add(account_tag)
            self.session.commit()

        return account_tag

    def process(self):
        with tempfile.NamedTemporaryFile() as f:
            self.file.save(f)

            records = self.__read_file(f)
            if records:
                mapping = self.__guess_mapping(records)
                for transaction in self.__transform_records(records, mapping):
                    self.session.add(transaction)

                self.session.commit()

                update_transaction_list(self.user_id, self.account_id, self.session)
            else:
                raise LoadTransactionFileException(
                    detail="Error while loading transaction file"
                )


