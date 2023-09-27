class TransactionException(Exception):
    pass


class LoadTransactionFileException(TransactionException):
    def __init__(self, detail):
        super().__init__(title="Load transaction file exception", detail=detail)


class MissingAccountMapperException(TransactionException):
    def __init__(self, detail):
        super().__init__(title="Missing account mapper exception", detail=detail)
