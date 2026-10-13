
class TableFunctions():

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


    def _get_header_col_index(self, header: str) -> int | Exception:
        print(self.header_index)
        if header == self.pk:
            raise ValueError(f'Must use a different header than the {self.pk!r} primary key')
        if header in self.headers:
            return self.header_index[header]
        else:
            raise ValueError(f'{header!r} not found in the header row')


    def _get_pk_row_index(self, pkid: str) -> int | Exception:
        if pkid in self.pk_hashmap:
            return self.pk_hashmap[pkid]
        else:
            raise ValueError(f'{pkid!r} not found in the {self.pk!r} column')


    def get_pkvalue(self, pkid: str, header: str):
        try:
            col_n = self._get_header_col_index(header)
            row_n = self._get_pk_row_index(pkid)
            return self.table[row_n][col_n]
        except Exception as e:
            print(f'[ERROR] {e}')
            return None



