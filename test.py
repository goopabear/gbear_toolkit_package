from src.gbear_toolkit.tables import DataTable
from src.gbear_toolkit import ProjectPaths


app = DataTable()
p = ProjectPaths('gbear_toolkit_package')

app.load_csv(abs_path=p.path_to('tests', 'csv', 'sales.csv'), pk='order_id', filter_headers='region')

def fill():
    col = app.get_col('order_id',)
    print(col)
    #for row in col[1:]:


print(fill())

#app.add_col('add', fill)
#print(app.table)