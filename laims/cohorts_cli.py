import click, os, tabulate, sys

from laims.app import LaimsApp
#from laims.models import ComputeWorkflowSample, SampleCohort

# COHORTS
# create
# update
# list

@click.group()
def laims_cohorts_cli():
    """
    Commands and Helpers for Sample Cohorts
    """
    pass

# [list]
@click.command()
def cohort_list_cmd():
    sm = LaimsApp().db_connection()
    session = sm()
    sql = "select name, count(*) as sample_count from sample_cohorts group by name"
    result = session.execute(sql)
    rows = []
    for cohort in result.fetchall():
        rows += [list(map(str, cohort))]
    sys.stdout.write( tabulate.tabulate(rows, ["NAME", "SAMPLE_COUNT"], tablefmt="simple") )
laims_cohorts_cli.add_command(cohort_list_cmd, name="list")
