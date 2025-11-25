from db import Database

db = Database()
res = db.fetch_all("TagOfClient")
print(res)
