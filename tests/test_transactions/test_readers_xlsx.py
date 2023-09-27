from balance_api.transactions.readers.xlsx import ExcelReader


def test_transactions_readers_xlsx():
    filename = "tests/fixtures_data/sample_transactions.xlsx"
    reader = ExcelReader(filename)
    reader.parse()
    records = reader.tail
    assert len(records) == 9
