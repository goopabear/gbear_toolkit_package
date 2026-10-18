from datetime import datetime
import csv
import os

class Export():
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


    def export_csv(self, abs_path: str, filename: str ='export', timestamp=True):
        stamp = ""
        if timestamp:
            stamp = datetime.now().strftime("_%Y_%m_%d_%H%M%S")

        file = f"{filename}{stamp}.csv"
        output_path = abs_path + os.sep + file

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(self.table)
        return output_path


    def append_csv(self, abs_path: str, filename: str ='log', bypass_check=False):
        file = f"{filename}.csv"
        output_path = abs_path + os.sep + file
        write_headers = False # Won't write headers unless 'filenotfound' or if no headers found in the destination.

        try:
            with open(output_path, "r", newline="", encoding="utf-8") as r:
                print(f'[INFO] Existing file found at: {output_path!r}')
                reader = csv.reader(r)
                destination_headers = next(reader, [])

            if not bypass_check:
                if not destination_headers:
                    write_headers=True
                    pass
                elif not destination_headers == self.headers:
                    raise ValueError('Source and destination do not have matching headers')

        except FileNotFoundError:
            print(f'[INFO] {file!r} does not exist in specified directory.')
            print(f'[INFO] Creating new {file!r} file...')
            write_headers=True

        except Exception as e:
            raise Exception(e)

        with open(output_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_headers:
                writer.writerow(self.table[0])
                print('[INFO] Destination was new or empty; wrote header row.')
            writer.writerows(self.table[1:])
            print(f'[INFO] Appended new rows to {output_path!r}')
