# DTL - columns - dict[str, list] - columns keyed by name
from datetime import date
from decimal import Decimal

DATA = {
    'asin': ['B08N5WRWNW', 'B07FQ4DJ7X', 'B08C1W5N87', 'B08F6BPNC3'],
    'title': ['Echo Dot', 'Kindle', 'Fire TV Stick', 'Ring Doorbell'],
    'srp': [Decimal('49.99'), Decimal('99.99'), Decimal('39.99'), Decimal('59.99')],
    'added': [date(2024, 1, 15), date(2024, 2, 3), date(2024, 3, 21), None],
}
