from data.db_tools import Database
from os import path

db = Database(path.join(path.dirname(path.realpath(__file__)), "data", "data.db"))

test = db.get_cost_scrap('PAR', 'S0')
print(test)