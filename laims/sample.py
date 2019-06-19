import re, sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabulate import tabulate
 
from laims.app import LaimsApp
from laims.models import Base, ComputeWorkflowSample
 
def list_default_show():
    return "id,ingest_sample_name,source_directory"

def list(filter_by, show=list_default_show()):
    engine = create_engine(LaimsApp().lims_db_url)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    filter_search = re.search("(.+)([=~])(.+)", filter_by)
    if not filter_search:
        raise Exception("Unknown filter method: {}". format(filter_by))
    if not hasattr(ComputeWorkflowSample, filter_search.group(1)):
        raise Exception("Invalid attribute to filter by: {}".format(filter_search.group(1)))
    if filter_search.group(2) == "=":
        filters = ( getattr(ComputeWorkflowSample, filter_search.group(1)) == filter_search.group(3) )
    elif filter_search.group(2) == "~":
        filters = ( getattr(ComputeWorkflowSample, filter_search.group(1)).like(filter_search.group(3)) )
    results = session.query(ComputeWorkflowSample).filter(filters)
    rows = []
    show = show.split(',')
    for sample in results:
        rows.append( map(lambda a : getattr(sample, str(a)), show) )
    sys.stdout.write(tabulate(rows, headers=map(lambda a : a.upper(), show), tablefmt="simple", numalign="left"))
