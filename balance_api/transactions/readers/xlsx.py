from openpyxl import load_workbook

from balance_api.transactions.readers import BaseReader


class ExcelReader(BaseReader):
    def parse(self):
        wb = load_workbook(
            filename=self.filename,
            read_only=True,
            data_only=True,
            keep_links=False,
        )
        ws = wb.active
        data = []
        for row in ws.rows:
            record = []
            for cell in row:
                record.append(cell.value)

            record = tuple(record)
            if any(record):
                if not self.head:
                    self.set_head(record)
                    continue

                row = {}
                for count, item in enumerate(record):
                    row[self.head[count]] = item
                data.append(row)

        self.set_tail(data)
        wb.close()
