import click, os, tabulate, sys

from laims.app import LaimsApp
from laims.models import ComputeWorkflowSample, SampleFile

# SAMPLE FILE
# add
# list
# update

@click.group()
def laims_files_cli():
    """
    Commands and Helpers for Samples
    """
    pass

# [add]
@click.command()
@click.argument("sample", type=str)
@click.argument("name", type=str, type=click.Choice(["cram", "gvcf"]) # FIXME add cloud
@click.argument("value", type=str)
def file_add_cmd(sample, name, value):
    """
    Add (or update) a single sample's file.
    """
    sm = LaimsApp().db_connection()
    session = sm()
    sample_file = session.query(SampleFile).get((sample.id, name))
    if sample_file is None:
        sample_file = SampleFile(sample_id=sample.id, name=name_l, value=metrics[name])
        elif metrics[name] != metric.value:
            setattr(metric, name_l, metrics[name])
        session.add(metric)
    session.commit()
    print("add")

# [list]
@click.command()
@click.option("filters", nargs=-1)
def sample_list_cmd(filters):
    sm = LaimsApp().db_connection()
    session = sm()
    if filter_by is not None:
        query = session.query(ComputeWorkflowSample).filter_by(source_work_order=filter_by)
    else:
        sample_iter = session.query(ComputeWorkflowSample)
    rows = []
    for sample in sample_iter:
        rows += [map(str, [sample.id, sample.ingest_sample_name, sample.source_work_order])]
    sys.stdout.write( tabulate.tabulate(rows, ["ID", "NAME", "WORK_ORDER"], tablefmt="simple") )
laims_sample_cli.add_command(sample_list_cmd, name="list")

# [update]
@click.command()
@click.argument("sample")
@click.argument("name")
@click.argument("value")
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
