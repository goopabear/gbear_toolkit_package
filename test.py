from src.gbear_toolkit.tables import DataTable
from src.gbear_toolkit import ProjectPaths


app = DataTable()
path = ProjectPaths('gbear_toolkit_package')

app.load_csv(abs_path=path.user_select())
app.export_csv(abs_path=path.user_select(), data=app.table)