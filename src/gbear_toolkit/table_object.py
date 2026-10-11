from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import csv

class DataTable():
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
    # Loading from CSV

    def _LTL_method(self, data, **kwargs) -> None:
        # Create output container: a list of rows as lists, e.g. [[1, "a"], [2, "b"]]
        rows = []

        # ------------------------------------------------------------------------------------- ^^^^
        # Gather from kwargs:
        pk = kwargs.pop("pk", None)
        if pk:
            print(f'[INFO] Primary key set to {pk!r}')

        includes_headers = kwargs.pop("includes_headers", False)
        if includes_headers:
            print('[INFO] Treating first row as headers')

        # ------------------------------------------------------------------------------------- ^^^^
        # Start iterating through every row

        for n_row, row in enumerate(data, start=1):
            try:
                if not isinstance(row, list):
                    raise TypeError(f'Row {n_row}: expected a list, got {type(row).__name__}; skipping row') # If row not list, SKIP
                
                # For each element in this row append to the total to the list:
                row_data = []
                # ------------------------------------------------------------------------------------- XXXX
                # Header assignment

                # If data includes headers; use placeholder integers
                # NOTE: While self.headers exists, includes_headers will still be false.
                if not includes_headers and not self.headers:
                    for n_col, _ in enumerate(row, start=1):
                        placeholder = 'col_' + str(n_col)
                        self.headers.append(placeholder)
                    self.n_cols = len(self.headers)
                    rows.append(self.headers)

                # If headers
                if includes_headers and not self.headers:
                    for col_index, element in enumerate(row, start=0):
                        header = str(element)
                        self.headers.append(header)
                        self.header_index[header] = col_index
                        if pk == header:
                            self.pk = pk
                            self.pk_col_index = col_index
                            self.pk_hashmap = {}     
                    if pk and not self.pk:
                        print(f'[WARNING] Primary key {pk!r} not found in headers; continuing without a primary key')               
                    self.n_cols = len(self.headers)  # <-- Set column count
                    rows.append(self.headers)
                    self.includes_headers = True  # <-- Confirmed Headers
                    continue
                    
                # -------------------------------------------------------------------------------------
                # Append each element in row into an inner list

                for n_col, element in enumerate(row, start=1):
                    pk_element = False

                    # Check for PK dupe
                    if self.pk and n_col == self.pk_col_index + 1: # Add 1 because index starts at 0
                            if not element:
                                raise ValueError(f'Row {n_row}: primary key value is empty; skipping row')
                            if str(element) in self.pk_hashmap:
                                raise ValueError(f'Row {n_row}: duplicate primary key {str(element)!r}; skipping row')
                            pk_element = True

                    # -------------------------------------------------------------------------------------

                    if not isinstance(element, (str, int, float, Decimal, date, type(None))):
                        raise TypeError(f'Row {n_row}, column {n_col}: unsupported type {type(element).__name__}; skipping row')
                    if n_col > len(self.headers):
                        raise IndexError(f'Row {n_row}: more values than columns (expected {len(self.headers)}); skipping row')
                
                    # Finally, append the element to row data
                    if pk_element:
                        row_data.append(str(element))
                    else:
                        row_data.append(self._assigntype(element))

                # -------------------------------------------------------------------------------------
                # Check if row data is consistent with column count scanned from row 1
                if len(row_data) != self.n_cols:
                    raise IndexError(f'Row {n_row}: expected {self.n_cols} values, got {len(row_data)}; skipping row')

                # Finally, if no errors raised, append row to table.
                rows.append(row_data)
                if self.pk: # Only record PK once the row is accepted
                    self.pk_hashmap[str(row_data[self.pk_col_index])] = len(rows) - 1
                # -------------------------------------------------------------------------------------

            except Exception as e:
                print(f'[ERROR] {e}')
                continue

        # Once finished, overwrite table:
        print(f'[INFO] Load complete: {len(rows) - 1} rows loaded')
        self.table = rows
        self.format = 'LTL'
        return True



    def _CSV_method(self, abs_path, **kwargs) -> None:
        # Create output container: a list of rows as lists, e.g. [[1, "a"], [2, "b"]] 
        rows = []

        # -------------------------------------------------------------------------------------
        # Gather from kwargs:
        pk = kwargs.pop("pk", None)
        if pk:
            print(f'[INFO] Primary key set to {pk!r}')

        includes_headers = kwargs.pop("includes_headers", False)
        if includes_headers:
            print('[INFO] Treating first row as headers')

        # -------------------------------------------------------------------------------------
        # Open CSV and start iterating per row in CSV
        with open(abs_path, newline="", encoding='utf-8-sig') as f:
            r = csv.reader(f)
            for n_row, row in enumerate(r, start=1):
    
                try:
                    # For each element in this row append to the total to the list:
                    row_data = []
                    # ------------------------------------------------------------------------------------- XXXX
                    # Header assignment

                    # If data includes headers; use placeholder integers
                    # NOTE: While self.headers exists, includes_headers will still be false.
                    if not includes_headers and not self.headers:
                        for n_col, _ in enumerate(row, start=1):
                            placeholder = 'col_' + str(n_col)
                            self.headers.append(placeholder)
                        self.n_cols = len(self.headers)
                        rows.append(self.headers)

                    # If headers
                    if includes_headers and not self.headers:
                        for col_index, element in enumerate(row, start=0):
                            header = str(element)
                            self.headers.append(header)
                            self.header_index[header] = col_index
                            if pk == header:
                                self.pk = pk
                                self.pk_col_index = col_index
                                self.pk_hashmap = {}     
                        if pk and not self.pk:
                            print(f'[WARNING] Primary key {pk!r} not found in headers; continuing without a primary key')               
                        self.n_cols = len(self.headers)  # <-- Set column count
                        rows.append(self.headers)
                        self.includes_headers = True  # <-- Confirmed Headers
                        continue
                        
                    # -------------------------------------------------------------------------------------
                    # Append each element in row into an inner list

                    for n_col, element in enumerate(row, start=1):

                        # Check for PK dupe
                        if self.pk and n_col == self.pk_col_index + 1: # Add 1 because index starts at 0
                                if not element:
                                    raise ValueError(f'Row {n_row}: primary key value is empty; skipping row')
                                if str(element) in self.pk_hashmap:
                                    raise ValueError(f'Row {n_row}: duplicate primary key {str(element)!r}; skipping row')

                        # -------------------------------------------------------------------------------------

                        if n_col > len(self.headers):
                            raise IndexError(f'Row {n_row}: more values than columns (expected {len(self.headers)}); skipping row')
                    
                        # Finally, append the element to row data
                        row_data.append(element)

                    # -------------------------------------------------------------------------------------
                    # Check if row data is consistent with column count scanned from row 1
                    if len(row_data) != self.n_cols:
                        raise IndexError(f'Row {n_row}: expected {self.n_cols} values, got {len(row_data)}; skipping row')

                    # Finally, if no errors raised, append row to table.
                    rows.append(row_data)
                    if self.pk: # Only record PK once the row is accepted
                        self.pk_hashmap[str(row_data[self.pk_col_index])] = len(rows) - 1
                    # -------------------------------------------------------------------------------------

                except Exception as e:
                    print(f'[ERROR] {e}')
                    continue

        # Once finished, overwrite table:
        print(f'[INFO] Load complete: {len(rows) - 1} rows loaded')
        self.table = rows
        self.format = 'LTL'
        return True

    # -----------------------------------------------------------------------------
    # Loading functions

    def load_from(self, data, pk=None, includes_headers=True) -> None:
        if pk and not includes_headers:
            print('[WARNING] Primary key specified but includes_headers is False; continuing without a primary key')
            pk=None

        # Clear object memory
        self._defaults()

        try:
            method = self._checkformat(data)
            print(f'[INFO] Detected format: {method}')

            if method == 'LTL':
                self._LTL_method(data=data, pk=pk, includes_headers=includes_headers)
            else:
                raise TypeError(f'Unsupported format {method!r}; only LTL is currently supported')

        except Exception as e:
            print(f'[ERROR] {e}')


    def load_csv(self, abs_path, pk=None, includes_headers=True) -> None:
        if pk and not includes_headers:
            print('[WARNING] Primary key specified but includes_headers is False; continuing without a primary key')
            pk=None

        # Clear object memory
        self._defaults()

        try:
            self._CSV_method(abs_path=abs_path, pk=pk, includes_headers=includes_headers)
        except Exception as e:
            print(f'[ERROR] {e}')


if __name__ == '__main__':

    # TEST SCRIPT
    # -------------------------------------------------------------------------------------
    import os
    import importlib.util

    # Sample data for each format lives in tests/data/table_formats: ltl.py, ltd.py, dtl.py, dtd.py
    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
    formats_dir = os.path.abspath(os.path.join(repo_root, 'tests', 'data', 'table_formats'))

    # Change the filename here to test a different format
    path = os.path.join(formats_dir, 'ltl.py')

    # Loads a sample file from path and returns its DATA
    def load_sample(path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(f'[ERROR] Sample file not found at {path}')
        spec = importlib.util.spec_from_file_location('sample', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.DATA

    data = load_sample(path)  # <---- Sample Data
    print(f'[INFO] Loaded sample from {path}')

    # -------------------------------------------------------------------------------------

    d = DataTable()
    d.load_from(data, pk='asin')
    print(d.header_index)