# DTD - index - dict[str, dict] - rows keyed by unique PK (asin)
from datetime import date
from decimal import Decimal

DATA = {
    'B08N5WRWNW': {'title': 'Echo Dot', 'srp': Decimal('49.99'), 'added': date(2024, 1, 15)},
    'B07FQ4DJ7X': {'title': 'Kindle', 'srp': Decimal('99.99'), 'added': date(2024, 2, 3)},
    'B08C1W5N87': {'title': 'Fire TV Stick', 'srp': Decimal('39.99'), 'added': date(2024, 3, 21)},
    'B08F6BPNC3': {'title': 'Ring Doorbell', 'srp': Decimal('59.99'), 'added': None},
}
