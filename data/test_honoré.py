from db_tools import Database

db = Database("data.db")  

cost = db.get_cost_scrap("PAR", 0)
print("Cost of scrap 0 at site PAR:", cost)




