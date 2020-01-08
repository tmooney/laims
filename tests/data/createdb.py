import os
from sqlalchemy import *

from laims.models import Base
 
db_fn = "test.db"
os.remove(db_fn)
db_url = "sqlite:///{}".format(db_fn)
engine = create_engine(db_url)
meta = Base.metadata
Base.metadata.create_all(engine)

sql_fn = "test-data.sql"
with engine.connect() as con, open(sql_fn, "r") as sql_f:
    for statement in sql_f:
        con.execute(statement)
