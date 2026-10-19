from src.gbear_toolkit.tables import DataTable
from src.gbear_toolkit import ProjectPaths

from src.gbear_toolkit.dates import to_iso

app = DataTable()
p = ProjectPaths('gbear_toolkit_package')




app.load_csv(abs_path=p.user_select(), filter_headers= ['RELEASE', 'SKU', 'QTY', 'ETA', 'Received', 'Landed Cost'])

n = 1
while True:
    output = app.table[n][app._col_index('Landed Cost')]
    if not output:
        n+=1
    else:
        break

print(output)