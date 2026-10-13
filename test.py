from src.gbear_toolkit.tables import DataTable
from src.gbear_toolkit import ProjectPaths


app = DataTable()
path = ProjectPaths('gbear_toolkit_package')

app.load_csv(abs_path=path.user_select(), pk='sku')
print(app.headers)
print(app.header_index)
print(app.get_pkvalue(pkid='51211', header='bullet1'))