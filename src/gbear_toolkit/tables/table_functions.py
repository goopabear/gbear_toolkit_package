
class TableFunctions():
    def __init__(self):
        # Table starts as empty. Loads data from CSV and/or append from in-memory data.
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

    #==============================================================================================
    # Index helper functions:

    def _col_index(self, header: str) -> int:
        if header in self.headers:
            return self.header_index[header]
        else:
            raise ValueError(f'{header!r} not found in the header row')


    def _row_index(self, pk_value: str) -> int:
        if not self.pk:
            raise ValueError('Row indexing only works with PK enabled')
        if pk_value in self.pk_hashmap:
            return self.pk_hashmap[pk_value]
        else:
            raise ValueError(f'{pk_value!r} not found in the {self.pk!r} column')

    #==============================================================================================
    # Editting table:

    def add_col(self, header: str, fill: function = None):
        if isinstance(header, str):
            self.table[0].append(header)

            for n, row in enumerate(self.table[1:], start=1):
                try:
                    if fill:
                        row.append(fill())
                    else:
                        row.append(None)
                except Exception as e:
                    print(f'[ERROR] Unexcepted error in row {n}: {e!r}')
                    row.append(None)
        else:
            raise ValueError('Header must be a string')


    def remove_col(self, *headers: str):
        # Validate that arg headers are valid
        if not headers:
            print('No headers specified')
            return

        if not self.headers:
            print('Table does not contain any columns')
            return
        
        for h in headers:
            if h == self.pk:
                raise ValueError(f'[ERROR] Cannot remove the PK column {h!r}')
            if not h in self.headers:
                print(f'[WARNING] {h!r} not found in table headers')

        #-------------------------------------------------------
        # Get indexes of headers NOT included in the arguments
        remaining: list[int] = []

        for existing, column_index in self.header_index.items():
            if existing not in headers:
                remaining.append(column_index)
        if len(existing) < 1:
            raise ValueError(f'[ERROR] At least one column, PK, must remain')

        #-------------------------------------------------------
        # Filter table with using remaining indexes
        new_table = []
        for row in self.table:
            row_data =[]
            for col in remaining:
                row_data.append(row[col])
            new_table.append(row_data)

        #-------------------------------------------------------
        # Update class attributes
        self.table = new_table
        self.n_cols = len(new_table[0])
        self.headers = new_table[0]
        self.header_index = {}
        for index, header in enumerate(new_table[0]):
            self.header_index[header] = index

    #==============================================================================================
    # Returning table values:

    def get_cell(self, pk_value: str, header: str):
        try:
            col_n = self._col_index(header)
            row_n = self._row_index(pk_value)
            return self.table[row_n][col_n]
        except Exception as e:
            print(f'[ERROR] {e}')
            return None

    def get_row(self, pk_value: str) -> list:
        try:
            row_n = self._row_index(pk_value)
            return self.table[row_n]
        except Exception as e:
            print(f'[ERROR] {e}')
            return None


    def get_col(self, header: str, col_header=True) -> list:
        try:
            if col_header:
                index=0
            else:
                index=1

            column = []
            col_index = self._col_index(header)

            for row in self.table[index:]:
                column.append(row[col_index])

            return column
        
        except Exception as e:
            print(f'[UNEXPECTED_ERROR] {e}')
            return None
