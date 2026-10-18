from src.gbear_toolkit.tables import DataTable
from src.gbear_toolkit import ProjectPaths


app = DataTable()
p = ProjectPaths('gbear_toolkit_package')

app.load_csv(abs_path=p.path_to('tests', 'csv', 'sales.csv'), pk='order_id', filter_headers='region')
app.append_csv(abs_path=p.path_to('tests'))
