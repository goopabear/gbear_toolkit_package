from src.gbear_toolkit.tables import DataTable
from src.gbear_toolkit import ProjectPaths


app = DataTable()
p = ProjectPaths('gbear_toolkit_package')

app.load_csv(abs_path=p.path_to('tests', 'csv', 'sales.csv'), pk='order_id', filter_headers='region')

def v(**kwargs):
    row = kwargs.pop('row', None)
    print(row)
    return 2

app.add_col(header='priority', fill=v)
print(app.table)
