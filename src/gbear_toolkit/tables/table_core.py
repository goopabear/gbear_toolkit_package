from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import csv

from .table_export import Export

class DataTable(Export):
    def __init__(self, table_name: str = 'data_table'):
        # Table starts as empty. Loads data from CSV and/or append from in-memory data.
        self.table_name = table_name
        self._defaults()

    def _defaults(self) -> None:
        self.table: list[list] | list[dict] | dict[str, list] | dict[str, dict] | None = None
        # Table formats:
        #   LTL - rows    - list[list]      - rows as lists, e.g. [[sku, srp], ['51234', 12.99]]
        #   LTD - records - list[dict]      - rows as dicts, e.g. [{"id": 1, "name": "a"}]
        #   DTL - columns - dict[str, list] - columns keyed by name, e.g. {"id": [1, 2], "name": ["a", "b"]}
        #   DTD - index   - dict[str, dict] - rows keyed by unique PK, e.g. {"B08N5WRWNW": {"srp": 49.99, "title": "Echo Dot"}}
        self.format: str | None = None
        # Format notes:
        #   - In-memory data can only be loaded as LTL or LTD, and is validated on load.
        #   - CSVs are parsed directly into LTL or LTD, so they skip format validation.
        #   - DTL and DTD are produced only by transforming self.table.

        # Column count
        self.n_cols: int | None = None

        # Headers
        self.includes_headers: bool = False
        self.headers: list[str] = []
        self.header_index: dict[str, int] = {}

        # Primary keys - Designate a column as a PK for efficient key lookups.
        # This PK column cannot contain dupes!
        self.pk: str | None = None
        self.pk_col_index: int | None = None
        self.pk_hashmap: dict[str, int] = {}

    def _assigntype(self, value):
        # Normalizes a value for CSV output. Decimals and dates come back as strings:
        #   Decimal('1E+3') -> '1000', date(2024, 3, 5) -> '2024-03-05'
        DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%d-%b-%Y", "%B %d, %Y")

        # Non-string inputs (in-memory data)
        if value is None or isinstance(value, (bool, int, float)):
            return value
        if isinstance(value, Decimal):
            return format(value, 'f') if value.is_finite() else None
        if isinstance(value, datetime):  # check before date; datetime subclasses date
            return value.isoformat(sep=' ')
        if isinstance(value, date):
            return value.isoformat()

        s = str(value).strip()

        if not s:
            return None

        try:
            return int(s)
        except ValueError:
            pass

        try:
            d = Decimal(s)
        except InvalidOperation:
            pass
        else:
            if d.is_finite():          # reject "NaN", "Infinity", "-inf"
                return format(d, 'f')

        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(s, fmt).date().isoformat()
            except ValueError:
                pass

        return s


    # -----------------------------------------------------------------------------
    # First, loading from in-memory: LTL and LTD only.

    # Returns format of data
    def _checkformat(self, data) -> str:
        print('[INFO] Detecting input data format')
        if not data:
            raise ValueError('Input data is empty')
        
        if isinstance(data, list):
            element = data[0]
            if not element:
                raise ValueError('First row is empty; cannot determine data format')
            if isinstance(element, list): # list with rows as lists, e.g. [[1, "a"], [2, "b"]]
                return 'LTL'
            if isinstance(element, dict): # list with rows as dicts, e.g. [{"id": 1, "name": "a"}]
                return 'LTD'
            else:
                raise TypeError(f'Rows must be lists or dictionaries; got {type(element).__name__}')
            
        if isinstance(data, dict): 
            for k, v in data.items():
                if not isinstance(k, (str, int, float)):
                    raise TypeError(f'Dictionary keys must be strings, integers or floats; got {type(k).__name__}')
                if isinstance(v, list): # dict with columns keyed by name, e.g. {"id": [1, 2], "name": ["a", "b"]}
                    return 'DTL'
                if isinstance(v, dict): # dict with rows keyed by unique PK, e.g. {"B08N5WRWNW": {"srp": 49.99, "title": "Echo Dot"}}
                    return 'DTD'
                else:
                    raise TypeError(f'Dictionary values must be lists or dictionaries; got {type(v).__name__}')
        else:
            raise TypeError(f'Input data must be a list or dictionary; got {type(data).__name__}')


    # -----------------------------------------------------------------------------
    # Row ingestion - shared by every loader

    def _set_headers(self, row, pk) -> None:
        for col_index, element in enumerate(row):
            header = str(element)
            self.headers.append(header)
            self.header_index[header] = col_index
            if pk == header:
                self.pk = pk
                self.pk_col_index = col_index
        if pk and not self.pk:
            print(f'[WARNING] Primary key {pk!r} not found in headers; continuing without a primary key')
        self.n_cols = len(self.headers)
        self.includes_headers = True

    def _set_placeholder_headers(self, row) -> None:
        # No header row: name columns col_1, col_2, ... from the first row's width
        self.headers = [f'col_{n_col}' for n_col in range(1, len(row) + 1)]
        self.n_cols = len(self.headers)

    def _parse_row(self, row, n_row, convert) -> list:
        # Returns the cleaned row, or raises with the reason it was skipped
        if not isinstance(row, list):
            raise TypeError(f'Row {n_row}: expected a list, got {type(row).__name__}; skipping row')
        if len(row) > self.n_cols:
            raise IndexError(f'Row {n_row}: more values than columns (expected {self.n_cols}); skipping row')
        if len(row) < self.n_cols:
            raise IndexError(f'Row {n_row}: expected {self.n_cols} values, got {len(row)}; skipping row')

        row_data = []
        for n_col, element in enumerate(row, start=1):
            if self.pk and n_col == self.pk_col_index + 1:  # Add 1 because index starts at 0
                if element is None or str(element).strip() == '':  # 0 is a valid key
                    raise ValueError(f'Row {n_row}: primary key value is empty; skipping row')
                if str(element) in self.pk_hashmap:
                    raise ValueError(f'Row {n_row}: duplicate primary key {str(element)!r}; skipping row')
                row_data.append(str(element))
                continue

            if not isinstance(element, (str, int, float, Decimal, date, type(None))):
                raise TypeError(f'Row {n_row}, column {n_col}: unsupported type {type(element).__name__}; skipping row')
            row_data.append(self._assigntype(element) if convert else element)

        return row_data

    def _ingest_rows(self, rows_iter, pk=None, includes_headers=True, convert=True) -> None:
        # Builds self.table as LTL from any iterable of rows.
        # convert=False keeps values as-is (CSV values stay strings).
        if pk:
            print(f'[INFO] Primary key set to {pk!r}')
        if includes_headers:
            print('[INFO] Treating first row as headers')

        rows = []
        for n_row, row in enumerate(rows_iter, start=1):
            try:
                # First row decides the headers
                if not self.headers:
                    if not isinstance(row, list):
                        raise TypeError(f'Row {n_row}: expected a list, got {type(row).__name__}; skipping row')
                    if includes_headers:
                        self._set_headers(row, pk)
                        rows.append(self.headers)
                        continue  # Header row is not data
                    self._set_placeholder_headers(row)
                    rows.append(self.headers)

                row_data = self._parse_row(row, n_row, convert)
                rows.append(row_data)
                if self.pk:  # Only record PK once the row is accepted
                    self.pk_hashmap[row_data[self.pk_col_index]] = len(rows) - 1

            except Exception as e:
                print(f'[ERROR] {e}')

        print(f'[INFO] Load complete: {len(rows) - 1} rows loaded')
        self.table = rows
        self.format = 'LTL'

    # -----------------------------------------------------------------------------
    # Loading functions

    def _load(self, ingest, pk, includes_headers) -> None:
        if pk and not includes_headers:
            print('[WARNING] Primary key specified but includes_headers is False; continuing without a primary key')
            pk = None

        # Clear object memory
        self._defaults()

        try:
            ingest(pk, includes_headers)
        except Exception as e:
            print(f'[ERROR] {e}')

    def load_from(self, data, pk=None, includes_headers=True) -> None:
        def ingest(pk, includes_headers):
            method = self._checkformat(data)
            print(f'[INFO] Detected format: {method}')
            if method != 'LTL':
                raise TypeError(f'Unsupported format {method!r}; only LTL is currently supported')
            self._ingest_rows(data, pk, includes_headers)

        self._load(ingest, pk, includes_headers)

    def load_csv(self, abs_path, pk=None, includes_headers=True) -> None:
        def ingest(pk, includes_headers):
            with open(abs_path, newline='', encoding='utf-8-sig') as f:
                self._ingest_rows(csv.reader(f), pk, includes_headers, convert=False)

        self._load(ingest, pk, includes_headers)
