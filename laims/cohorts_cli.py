import click, os, tabulate, sys

from laims.app import LaimsApp
from laims.models import SampleCohort

# COHORTS
# create
# list

@click.group()
def laims_chohort_cli():
    """
    Commands and Helpers for Sample Cohorts
    """
    pass

# [create]
@click.command()
def cohort_list_cmd(filter_by):
    sm = LaimsApp().db_connection()
    session = sm()
    for sample in :
        sample = session.query(

        cohort = SampleCohort(
        sesion.add(cohort)
    session.commit()
    sys.
laims_cohort_cli.add_command(cohort_list_cmd, name="create")

# [list]
@click.command()
@click.option("--filter-by", "-f", required=False, help="Filter cohorts by workorder.")
def cohort_list_cmd(filter_by):
    db_fn = "test.db"
    db_url = "sqlite:///{}".format(db_fn)
    engine = create_engine(db_url)
    statement = "select name, count(*) as sample_count from sample_cohorts group by name;"
    with engine.connect() as con:
        result = con.execute(sql)
        print(result.keys())
        print(dir(result))
        for row in result.fetchall():
            print(row)

    sm = LaimsApp().db_connection()
    session = sm()
    rows = []
    for cohort in session.query(SampleCohort)
        rows += [map(str, [cohort.id, cohort.ingest_cohort_name, cohort.source_work_order])]
    sys.stdout.write( tabulate.tabulate(rows, ["ID", "NAME", "SAMPLE_COUNT"], tablefmt="simple") )
laims_cohort_cli.add_command(cohort_list_cmd, name="list")
