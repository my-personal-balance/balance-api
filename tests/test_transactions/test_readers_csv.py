from balance_api.transactions.readers.csv import CSVReader


def test_transactions_readers_xlsx():
    filename = "tests/fixtures_data/sample_transactions.csv"
    delimiter = ","
    reader = CSVReader(filename, delimiter)
    reader.parse()
    records = reader.tail
    assert len(records) == 9
