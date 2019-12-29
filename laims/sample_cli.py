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
    Commands and Helpers for Samples
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

# [update-files]
@click.command()
@click.argument("file_type", type=click.Choice(["cram", "gvcf"]))
@click.argument("fof")
def sample_update_files_cmd(file_type, fof):
    """
    Update Samples Files

    Give a file type, and an FOF of files to update. The sample name should be derivable from the filename.
    """
    attr = "_".join(["analysis", file_type, "path"])
    sm = LaimsApp().db_connection()
    session = sm()
    with open(fof, "r") as f:
        for fn in f.readlines():
            sample_n = os.path.basename(fn).split(".")[0]
            sample = session.query(ComputeWorkflowSample).filter_by(ingest_sample_name=sample_n).first()
            if sample is None:
                status = "NOT_FOUND"
            else:
                setattr(sample, attr, fn.rstrip())
                status = getattr(sample, attr)
            sys.stderr.write("{} {}\n".format(sample_n, status))
    session.commit()
laims_sample_cli.add_command(sample_update_files_cmd, name="update-files")
