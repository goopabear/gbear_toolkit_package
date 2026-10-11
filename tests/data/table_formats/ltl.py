# LTL - rows - list[list] - rows as lists, header row first
from datetime import date
from decimal import Decimal

DATA = [
    ['asin', 'title', 'srp', 'added'],
    ['B08N5WRWNW', 'Echo Dot', Decimal('49.99'), date(2024, 1, 15)],
    ['B07FQ4DJ7X', 'Kindle', Decimal('99.99'), date(2024, 2, 3)],
    ['B08C1W5N87', 'Fire TV Stick', Decimal('39.99'), date(2024, 3, 21)],
    ['B08F6BPNC3', 'Ring Doorbell', Decimal('59.99'), None],
]
