from src.gbear_toolkit.tables import DataTable
from src.gbear_toolkit import ProjectPaths


app = DataTable()
p = ProjectPaths('gbear_toolkit_package')

app.load_csv(abs_path=p.path_to('tests', 'csv', 'sales.csv'), pk='order_id', filter_headers='region')

def fill():
    col = app.get_col('order_id', incl_header=False)
    for row, element in enumerate(col):
        col[row] = element*2

    return col

app.add_col('add', fill())
print(app.table)