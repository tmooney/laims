import click, tabulate, sys

from laims.app import LaimsApp
from laims.models import ComputeWorkflowSample

# SAMPLE
# list

@click.group()
def laims_sample_cli():
    """
    Commands and Helpers for Samples
    """
    pass

@click.command()
@click.option("--filter-by", "-f", required=False, help="Filter samples by workorder.")
def sample_list_cmd(filter_by):
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
