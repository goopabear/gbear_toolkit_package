from datetime import datetime
import csv
import os

class Export():
    def export_csv(self, abs_path: str, data: list[list], filename='export', timestamp=True):
        if timestamp:
            stamp = datetime.now().strftime("_%Y_%m_%d_%H%M%S")

        file = f"{filename}{stamp}.csv"
        output_path = abs_path + os.sep + file

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)

    def append_csv(self, path, rows, header=None):
        write_header = header and (not os.path.exists(path) or os.path.getsize(path) == 0)

        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(header)
            writer.writerows(rows)