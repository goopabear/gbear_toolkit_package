from src.gbear_toolkit.tables import DataTable
from src.gbear_toolkit import ProjectPaths

from src.gbear_toolkit.files import xlsx_to_csv

app = DataTable()
p = ProjectPaths('gbear_toolkit_package')

app.load_csv(abs_path=p.user_select(), filter_headers= ['SKU', 'ORDER NO.', 'QTY', 'ETA', 'Received'])

x = app.get_col_uniques('Received')
print(x)
