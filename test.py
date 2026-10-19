from src.gbear_toolkit.tables import DataTable
from src.gbear_toolkit import ProjectPaths

from src.gbear_toolkit.dates import to_iso

app = DataTable()
p = ProjectPaths('gbear_toolkit_package')




app.load_csv(abs_path=p.user_select(), filter_headers= ['RELEASE', 'SKU', 'QTY', 'ETA', 'Received', 'Landed Cost'])

new_table = [['SKU', 'Landed Cost']]

skus = app.get_col_uniques('SKU')




for sku in skus:
    if not sku:
        continue

    sku = str(sku)
    most_recent = None
    index = {}
    landed = None

    for n, row in enumerate(app.table[1:],start=1):
        row_sku = str(row[app._col_index('SKU')])
        if sku != row_sku:
            continue

        release_date = row[app._col_index('RELEASE')]
        
        try:
            isodate = to_iso(release_date)
        except:
            continue

        if not most_recent or isodate > most_recent:
            print('hiwhaidh')
            if row[app._col_index('Landed Cost')]:
                landed = row[app._col_index('Landed Cost')]
                most_recent = isodate
                index[sku] = n


    new_row = [sku, landed]
    new_table.append(new_row)

print(new_table)