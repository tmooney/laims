import os.path
import json
import click
from logzero import logger

import laims
from laims.app import LaimsApp

@click.group()
@click.option('--config', envvar='LAIMS_CONFIG_PATH')
@click.option('--database', envvar='LAIMS_DB_PATH')
@click.option('--job-group', default=None)
@click.option('--queue', default='ccdg', type=click.Choice(['research-hpc', 'ccdg']))
@click.version_option(version=laims.__version__, prog_name='laims', message='%(prog)s %(version)s')
@click.pass_context
def cli(ctx, config, database, job_group, queue):
    conf = {
            "database": database,
            "job_group": job_group,
            "queue": queue,
            }
    ctx.obj = LaimsApp(config_file=config, config=conf)

@cli.command(help='TEST')
@click.pass_obj
def test(app):
    print("TESTING\n")
    app.log_config()

@cli.command(help='ingest LIMS build38 realignment compute_workflow_execution csv')
@click.argument('workorder_csv')
@click.option('--output-dir')
@click.option('--force/--no-force', default=False)
@click.pass_obj
def ingest(app, workorder_csv, output_dir, force):
    from laims.commands.ingest_work_order import ingest
    app.log_config()
    ingest(app, workorder_csv, output_dir, force)

@cli.command(help='check analysis directory for completeness')
@click.pass_obj
def check(app):
    from laims.commands.check_analysis_dir import check_analysis_dir
    app.log_config()
    check_analysis_dir(app)

@cli.command(name='call-sv', help='run SV pipeline on a workorder')
@click.argument('workorder', nargs=-1, type=int)
@click.pass_obj
def call_sv(app, workorder):
    import laims.commands.call_svs
    app.log_config()
    laims.commands.call_svs.call_svs(app, workorder)

@cli.command(name='generate-qc-table', help='generate a table of qc results for a workorder')
@click.argument('workorder', nargs=-1, type=int)
@click.pass_obj
def generate_table(app, workorder):
    import laims.commands.generate_qc_table
    app.log_config()
    laims.commands.generate_qc_table.generate(app, workorder)

@cli.command(name='reband', help='rerun haplotype caller with new default banding parameters')
@click.argument('workorders', nargs=-1, type=int)
@click.option('--output-dir')
@click.pass_obj
def launch_reband(app, output_dir, workorders):
    from laims.commands.reband_gvcfs import reband
    app.log_config()
    reband(app, output_dir, workorders)

@cli.command(name='oldband', help='rerun haplotype caller with old default banding parameters')
@click.argument('workorders', nargs=-1, type=int)
@click.option('--output-dir')
@click.pass_obj
def launch_oldband(app, output_dir, workorders):
    from laims.commands.oldband_gvcfs import oldband
    app.log_config()
    oldband(app, output_dir, workorders)

@cli.command(name='verify-reband-gvcfs', help='verify that all the rebanded gvcfs exist on the filesystem')
@click.option('--work-order', type=int, required=True)
@click.option('--cohort-path', type=click.Path(exists=True), required=True)
@click.pass_obj
def verify_reband_gvcfs(app, work_order, cohort_path):
    from laims.commands.verifications import verify_gvcfs
    verify_gvcfs(app.database, work_order, cohort_path)
