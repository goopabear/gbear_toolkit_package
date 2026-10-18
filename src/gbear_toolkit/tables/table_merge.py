
class Merge():
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

    #==============================================================================================
    # Merging

    def _leftjoin_update(self, new_column:list):
        if len(self.table) == len(new_column):
            for n, row in enumerate(self.table):
                row.append(new_column[n])
                return new_column
        else:
            raise ValueError('Detected a non-matching row count between left table and new column.')
        
    # Join new column on existing PK
    # Source must contain at least 2 columns with headers. One column must have at least one matching identifier
    def leftjoin(self, match_col: str, lookup: list[list], lookup_key: str, lookup_value: str):
        if not match_col in self.headers:
            raise ValueError(f'Left table (self) does not include the header: {match_col!r}')

        new_column = [] # each element is a new row

        left_index = self.header_index[match_col]

        rightheaders = lookup[0]
        new_column.append(rightheaders)
        rkey_index = rightheaders.index[lookup_key]
        rval_index = rightheaders.index[lookup_value]

        if not rkey_index:
            raise ValueError(f'lookup_key {lookup_key!r} not found in right table')
        if not rval_index:
            raise ValueError(f'lookup_value {lookup_value!r} not found in right table')

        
        for n, row in enumerate(self.table[1:], start=1):
            try:
                match = row[left_index]

                rightrow = lookup[n]
                rkey = rightrow[rkey_index]
                if match == rkey:
                    value = rightrow[rval_index]
                    new_column.append(value)
                else:
                    new_column.append(None)

            except Exception as e:
                print(f'[UNEXPECTED ERROR] Skipping row {n}: {e!r}')
                new_column.append(None)
                continue

        self._leftjoin_update(self, new_column=new_column)
        return 
        


