import functools

class Convert():
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
    # Validation functions:

    def _checkif(self):
        if not self.table:
            raise Exception('No table exists')
        if not self.format:
            raise Exception('No format described')
        if not self.includes_headers:
            raise Exception('Table must include headers')

    def _exists(self):
        try:
            self._checkif()
            return True
        except Exception as e:
            print(f'[ERROR] {e!r}')
            return False

    #==============================================================================================
    # Validation functions:

    def convert_dtl(self):
        DTL = {}
        for i, header in enumerate(self.table[0]):
            column = []
            for row in self.table[1:]:
                column.append(row[i])
            DTL[header] = column

        self.table = DTL
        self.format = 'DTL'



        

        
    