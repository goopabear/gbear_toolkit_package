from src.gbear_toolkit.tables import DataTable
from src.gbear_toolkit import ProjectPaths

from src.gbear_toolkit.files import xlsx_to_csv
from src.gbear_toolkit.dates import to_iso

app = DataTable()
p = ProjectPaths('gbear_toolkit_package')

app.load_csv(abs_path=p.user_select(), filter_headers= ['RELEASE', 'SKU', 'QTY', 'ETA', 'Received', 'Landed Cost'])

output = app.get_col_uniques('SKU')


print(output)


