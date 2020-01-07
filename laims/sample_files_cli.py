import click, os, tabulate, sys

from laims.app import LaimsApp
from laims.models import ComputeWorkflowSample, SampleFile

# SAMPLE FILE
# update

@click.group()
def files_cli():
    """
    Work with samples' files
    """
    pass

valid_keys = ["cram", "gvcf"]

# [update]
@click.command()
@click.argument("fof")
@click.option("--key", "-k", type=click.Choice(valid_keys), help="Use this as the sample file key instead of deriving it from the file's extension.")
def update_cmd(fof, key):
    """
    Update Samples Files

    Give an FOF of files to update. The sample name should be derivable from the filename. It not giving the --key option, the extension will be used as the file's key.
    """
    sm = LaimsApp().db_connection()
    session = sm()
    with open(fof, "r") as f:
        for fn in f.readlines():
            fn = fn.rstrip()
            bn = os.path.basename(fn)
            tokens =  bn.split(".")

            sample_name = tokens[0]
            sample = session.query(ComputeWorkflowSample).filter_by(ingest_sample_name=sample_name).first()

            if sample is None:
                sys.stderr.write("NO_SAMPLE {}\n".format(sample_name, fn))
                continue

            _key = key
            if _key is None:
                _key = tokens[-1]
                if not _key in valid_keys:
                    sys.stderr.write("INVALID_KEY {} {}\n".format(_key, fn))
                    continue

            sample_file = session.query(SampleFile).get((sample.id, _key))
            if sample_file is not None:
                sample_file.value = fn
            else:
                #sample_file = SampleFile(sample.id, key, fn)
                sample_file = SampleFile(sample_id=sample.id, name=_key, value=fn)
            session.add(sample_file)
            sys.stderr.write("OK {} {} {}\n".format(sample_name, _key, fn))
    session.commit()
files_cli.add_command(update_cmd, name="update")
