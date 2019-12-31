import click, os, tabulate, sys
from sqlalchemy.orm.exc import NoResultFound

from laims.app import LaimsApp
from laims.models import ComputeWorkflowSample, SampleCohort

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

# [link]
@click.command()
@click.argument("name", type=str)
@click.argument("samples", required=True, nargs=-1)
def cohorts_link_cmd(name,samples):
    """
    Link samples to a cohort
    """
    sm = LaimsApp().db_connection()
    session = sm()
    if len(samples) == 1 and os.path.exists(samples[0]):
        with open(samples[0], "r") as f:
            names_to_link = set()
            for l in f.readlines():
                names_to_link.add( l.rstrip() )
    else:
        names_to_link = set(samples)
    stats = { "add": 0, "skip": 0 }
    for sample_name in names_to_link:
        try:
            sample = session.query(ComputeWorkflowSample).filter_by(ingest_sample_name=sample_name).one()
        except NoResultFound:
            raise Exception("Could not find sample named {}".format(sample_name))
        cohort = session.query(SampleCohort).get((sample.id, name))
        if cohort is None:
            cohort = SampleCohort(name=name, sample_id=sample.id)
            session.add(cohort)
            stats["add"] += 1
        else:
            stats["skip"] += 1
    session.commit()
    sys.stderr.write("Added {} samples to cohort {}, skipped {} existing.".format(stats["add"], name, stats["skip"]))
laims_cohorts_cli.add_command(cohorts_link_cmd, name="link")

# [list]
@click.command()
def cohorts_list_cmd():
    """
    List cohorts and sample counts
    """
    sm = LaimsApp().db_connection()
    session = sm()
    sql = "select name, count(*) as sample_count from sample_cohorts group by name"
    result = session.execute(sql)
    rows = []
    for cohort in result.fetchall():
        rows += [list(map(str, cohort))]
    sys.stdout.write( tabulate.tabulate(rows, ["NAME", "SAMPLE_COUNT"], tablefmt="simple") )
laims_cohorts_cli.add_command(cohorts_list_cmd, name="list")
