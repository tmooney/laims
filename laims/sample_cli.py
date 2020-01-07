import click, os, tabulate, sys

from laims.app import LaimsApp
from laims.models import ComputeWorkflowSample

# SAMPLE
# cohorts
# list
# update-files

@click.group()
def laims_sample_cli():
    """
    Work with samples
    """
    pass

# [cohort]
from laims.cohorts_cli import laims_cohorts_cli
laims_sample_cli.add_command(laims_cohorts_cli, name="cohorts")

# [list]
# FIXME
# filter need to be cohort or workorder
# need a show
@click.command()
@click.option("--filter-by", "-f", required=False, help="Filter samples by workorder.")
def sample_list_cmd(filter_by):
    """
    List samples and show their attributes
    """
    sm = LaimsApp().db_connection()
    session = sm()
    if filter_by is not None:
        sample_iter = session.query(ComputeWorkflowSample).filter_by(source_work_order=filter_by)
    else:
        sample_iter = session.query(ComputeWorkflowSample)
    rows = []
    for sample in sample_iter:
        rows += [map(str, [sample.id, sample.ingest_sample_name, sample.source_work_order])]
    sys.stdout.write( tabulate.tabulate(rows, ["ID", "NAME", "WORK_ORDER"], tablefmt="simple") )
laims_sample_cli.add_command(sample_list_cmd, name="list")

# [metrics]
from laims.metrics_cli import laims_metrics_cli
laims_sample_cli.add_command(laims_metrics_cli, name="metrics")

# [files]
from laims.sample_files_cli import files_cli
laims_sample_cli.add_command(files_cli, name="files")
