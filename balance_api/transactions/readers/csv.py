import csv

from balance_api.transactions.readers import BaseReader


class CSVReader(BaseReader):
    def __init__(self, filename, delimiter):
        super().__init__(filename)
        self.delimiter = delimiter

    def parse(self):
        with open(self.filename, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            data = []
            for row in reader:
                record = tuple(row)
                if any(record):
                    if not self.head:
                        self.set_head(record)
                        continue

                    row = {}
                    for count, item in enumerate(record):
                        row[self.head[count]] = item
                    data.append(row)

            self.set_tail(data)
