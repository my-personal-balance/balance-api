import logging
import tempfile
from datetime import datetime
from operator import itemgetter

from sqlalchemy.orm.session import Session
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from balance_api.models.account_mappers import SourceFileType, find_account_mapper
from balance_api.models.tags import find_or_create_account_tag
from balance_api.models.transactions import Transaction, TransactionType
from balance_api.transactions import (
    LoadTransactionFileException,
    MissingAccountMapperException,
)
from balance_api.transactions.readers import BaseReader
from balance_api.transactions.readers.csv import CSVReader
from balance_api.transactions.readers.xlsx import ExcelReader

logger = logging.getLogger(__name__)


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

        self.account_mapper = find_account_mapper(user_id, account_id, session)

        self.mapping_schema = self.account_mapper.source_file_schema

    def __read_file(self, temp_file):
        if not self.account_mapper:
            raise MissingAccountMapperException(
                f"Missing account mapper for account id {self.account_id}."
            )

        reader = self.__get_file_reader(temp_file)
        reader.parse()
        return reader.tail

    def __get_file_reader(self, temp_file) -> BaseReader:
        source_file_type = SourceFileType(self.account_mapper.source_file_type)
        if SourceFileType.CSV == source_file_type:
            delimiter = self.mapping_schema.get("file_delimiter")
            return CSVReader(temp_file, delimiter=delimiter)
        elif source_file_type in [SourceFileType.XLS, SourceFileType.XLSX]:
            return ExcelReader(temp_file)

    def __transform_records(self, records):
        for record in records:
            tag_value = self.__get_record_value(self.mapping_schema.get("tag"), record)

            tag = None
            if tag_value:
                tag = find_or_create_account_tag(
                    user_id=self.user_id, tag_value=tag_value, session=self.session
                )

            amount = float(
                self.__get_record_value(self.mapping_schema.get("amount"), record)
            )

            transaction_date = self.__get_record_value(
                self.mapping_schema.get("date"), record
            )
            transaction_date = self.__parse_date(transaction_date)

            description = self.__get_record_value(
                self.mapping_schema.get("description"), record
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
        except KeyError as err:
            logger.error(err)
            return None

    def __parse_date(self, transaction_date):
        date_format = self.mapping_schema.get("date_format")
        if date_format:
            try:
                nd = datetime.strptime(transaction_date, "%d/%m/%Y")
                return nd.strftime("%Y-%m-%d")
            except Exception as e:
                logger.error(e)
                raise LoadTransactionFileException(
                    detail="Error while parsing transaction file date "
                )

        return transaction_date

    def process(self):
        temp_file_path = (
            f"{tempfile.gettempdir()}/{secure_filename(self.file.filename)}"
        )
        with open(temp_file_path, mode="wb+") as f:
            self.file.save(f)

        records = self.__read_file(temp_file_path)
        if records:
            for transaction in self.__transform_records(records):
                self.session.add(transaction)

            try:
                self.session.commit()
            except Exception as e:
                logger.error(e)
        else:
            raise LoadTransactionFileException(
                detail="Error while loading transaction file"
            )
