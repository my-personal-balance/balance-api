import tempfile
from operator import itemgetter

from meza.io import read_csv, read_xls
from sqlalchemy.orm.session import Session
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from balance_api.models.account_mappers import SourceFileType, find_account_mapper
from balance_api.models.tags import find_or_create_account_tag
from balance_api.models.transactions import Transaction, TransactionType
from balance_api.transactions import LoadTransactionFileException


class TransactionFileLoader:
    def __init__(
        self,
        file: FileStorage,
        user_id: int,
        account_id: int,
        session: Session,
    ):
        self.file = file
        self.user_id = user_id
        self.account_id = account_id
        self.session = session
        self.source_file_type = SourceFileType(file.content_type)
        self.account_mapper = None

    def __read_file(self, temp_file):
        if SourceFileType.CSV == self.source_file_type:
            return read_csv(temp_file.name)
        elif self.source_file_type in [SourceFileType.XLS, SourceFileType.XLSX]:
            return read_xls(temp_file.name)

    def __transform_records(self, records, mapping_schema: dict):
        for record in records:
            tag_value = self.__get_record_value(mapping_schema.get("tag"), record)

            tag = None
            if tag_value:
                tag = find_or_create_account_tag(
                    user_id=self.user_id, tag_value=tag_value, session=self.session
                )

            amount = float(
                self.__get_record_value(mapping_schema.get("amount"), record)
            )
            transaction_date = self.__get_record_value(
                mapping_schema.get("date"), record
            )
            description = self.__get_record_value(
                mapping_schema.get("description"), record
            )

            transaction_type = (
                TransactionType.EXPENSE if amount < 0 else TransactionType.INCOME
            )

            yield Transaction(
                date=transaction_date,
                transaction_type=transaction_type,
                amount=abs(amount) if amount else 0.0,
                description=description,
                account_id=self.account_id,
                tag=tag,
            )

    @classmethod
    def __get_record_value(cls, key, record):
        try:
            return itemgetter(key)(record)
        except KeyError:
            return None

    def process(self):
        temp_file_path = (
            f"{tempfile.gettempdir()}/{secure_filename(self.file.filename)}"
        )
        with open(temp_file_path, mode="wb+") as f:
            self.file.save(f)
            records = self.__read_file(f)

        if records:
            account_mapper = find_account_mapper(
                self.user_id, self.account_id, self.session
            )
            for transaction in self.__transform_records(
                records, account_mapper.source_file_schema
            ):
                self.session.add(transaction)

            self.session.commit()
        else:
            raise LoadTransactionFileException(
                detail="Error while loading transaction file"
            )
