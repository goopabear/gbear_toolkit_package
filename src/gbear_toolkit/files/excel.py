import csv, os
from openpyxl import load_workbook

def xlsx_to_csv(source_path, output_path, filename: str = 'output.csv', sheet_name=None):
    # Open the workbook
    workbook = load_workbook(source_path, read_only=True, data_only=True)

    # Choose the sheet
    if sheet_name is None:
        sheet = workbook.active
    else:
        sheet = workbook[sheet_name]

    # Open the output file
    output_path = output_path + os.sep + filename
    output_file = open(output_path, "w", newline="", encoding="utf-8")
    writer = csv.writer(output_file)

    # Go through each row and write it out
    for row in sheet.iter_rows(values_only=True):
        cleaned_row = []
        for value in row:
            if value is None:
                cleaned_row.append("")
            else:
                cleaned_row.append(value)
        writer.writerow(cleaned_row)

    # Close everything
    output_file.close()
    workbook.close()

#xlsx_to_csv("input.xlsx", "output.csv")             # first/active sheet
#xlsx_to_csv("input.xlsx", "sales.csv", "Sales")     # a sheet by name