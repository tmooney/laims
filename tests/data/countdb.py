from sqlalchemy import *

#from laims.models import Base
 
db_fn = "test.db"
db_url = "sqlite:///{}".format(db_fn)
engine = create_engine(db_url)
sql = "select name, count(*) as sample_count from sample_cohorts group by name;"
with engine.connect() as con:
    result = con.execute(sql)
    print(result.keys())
    print(dir(result))
    for row in result.fetchall():
       print(row)
