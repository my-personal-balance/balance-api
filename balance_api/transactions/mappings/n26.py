from datetime import datetime
from operator import itemgetter

from balance_api.models.transactions import TransactionType

"""
{
    'Date': '2021-06-19',
    'Payee': 'PAYPAL',
    'Account number': '',
    'Transaction type': 'MasterCard Payment',
    'Payment reference': '',
    'Category': 'Shopping',
    'Amount (EUR)': '-7.13',
    'Amount (Foreign Currency)': '-7.13',
    'Type Foreign Currency': 'EUR',
    'Exchange Rate': '1.0'
}
"""


def find_type(transaction):
    amount = float(transaction.get("Amount (EUR)"))
    return TransactionType.EXPENSE if amount < 0 else TransactionType.INCOME


def get_date(transaction):
    return datetime.strptime(transaction.get("Date"), "%Y-%m-%d")


mapping = {
    "has_header": True,
    "is_split": False,
    "bank": "N26",
    "currency": "EUR",
    "delimiter": ",",
    "account": "N26 checking",
    "type": find_type,
    "date": get_date,
    "amount": itemgetter("Amount (EUR)"),
    "description": itemgetter("Payee"),
    "notes": itemgetter("Payment reference"),
    "tag": itemgetter("Category"),
}
