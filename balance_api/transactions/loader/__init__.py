import enum
import tempfile

from meza.io import read_csv, read_xls
from sqlalchemy.orm.session import Session
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from balance_api.models.tags import find_or_create_account_tag
from balance_api.models.transactions import Transaction
from balance_api.transactions import LoadTransactionFileException
from balance_api.transactions.mappings import n26, openbank


class SourceFileType(enum.Enum):
    CSV = "text/csv"
    XLS = "application/vnd.ms-excel"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


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
            tag_value = mapping.get("tag")(record)

            tag = None
            if tag_value:
                tag = find_or_create_account_tag(
                    user_id=self.user_id, tag_value=tag_value, session=self.session
                )

            amount = float(mapping.get("amount")(record))

            yield Transaction(
                date=mapping.get("date")(record),
                transaction_type=mapping.get("type")(record),
                amount=abs(amount),
                description=mapping.get("description")(record),
                account_id=self.account_id,
                tag=tag,
            )

    def process(self):
        temp_file_path = (
            f"{tempfile.gettempdir()}/{secure_filename(self.file.filename)}"
        )
        with open(temp_file_path, mode="wb+") as f:
            self.file.save(f)
            records = self.__read_file(f)

        if records:
            mapping = self.__guess_mapping(records)
            for transaction in self.__transform_records(records, mapping):
                self.session.add(transaction)

            self.session.commit()
        else:
            raise LoadTransactionFileException(
                detail="Error while loading transaction file"
            )
