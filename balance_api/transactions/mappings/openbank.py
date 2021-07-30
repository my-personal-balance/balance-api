from datetime import datetime
from operator import itemgetter

from balance_api.models.transactions import TransactionType

"""
{
    'Fecha Operación': '2021-06-19',
    'Fecha Valor': '2021-06-19',
    'Concepto': 'COMPRA EN 8016 GV LES CORTS 719 BAR, CON LA TARJETA : 5489133148236506 EL 2021-06-22',
    'Importe': '-7.13',
    'Saldo': '3.579,08'
}
"""


def find_type(transaction):
    amount = float(transaction.get("Importe"))
    return TransactionType.EXPENSE if amount < 0 else TransactionType.INCOME


def get_date(transaction):
    return datetime.strptime(transaction.get("Fecha Valor"), "%Y-%m-%d")


def get_tag(transaction):
    return None


mapping = {
    "has_header": True,
    "is_split": False,
    "bank": "Openbank",
    "currency": "EUR",
    "delimiter": ",",
    "account": "Openbank checking",
    "type": find_type,
    "date": get_date,
    "amount": itemgetter("Importe"),
    "description": itemgetter("Concepto"),
    "notes": None,
    "tag": get_tag,
}
