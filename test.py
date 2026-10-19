from src.gbear_toolkit.tables import DataTable
from src.gbear_toolkit import ProjectPaths

from src.gbear_toolkit.files import xlsx_to_csv

app = DataTable()
p = ProjectPaths('gbear_toolkit_package')

xlsx_to_csv(source_path=p.user_select(), output_path=p.path_to('tests'))