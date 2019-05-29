import os.path
import json
import click
import laims
from logzero import logger

class LaimsApp(object):
    def __init__(self, config_file=None, database=None, job_group=None, queue=None):
        '''
        This sets up common options for the application
        '''
        self.database = database
        self.job_group = job_group
        self.queue = queue
        self.config_file = config_file
        self.config = {}
        if config_file and not os.path.exists(config_file):
            raise Exception("Given config file {} does not exist!".fotrmat(confiog_file))
        else self.config_file is None:
            default_config
            if os.path.join(click.get_app_dir('laims'), 'config.json'):
            self.config_file = os.path.join(click.get_app_dir('laims'), 'config.json')
        self._load_config()

    def get_config(self, name):
        if name in self.config:
            return self.config[name]
        return None

    def _load_config(self):
        if not os.path.exists(self.config_file):
            logger.error('No configuration file found at {0}'.format(self.config_file))
            return
            
        with open(self.config_file) as f:
            self.config = json.load(f)
        self.database = self.get_config('database')
        self.job_group = self.get_config('job_group')

    def log_config(self):
        logger.info('Using config at {0}'.format(self.config_file))
        logger.info('Using database at {0}'.format(self.database))

#-- LaimsApp

@click.group()
@click.option('--config', envvar='LAIMS_CONFIG_PATH')
@click.option('--database', envvar='LAIMS_DB_PATH')
@click.option('--job-group', default=None)
@click.option('--queue', default='ccdg', type=click.Choice(['research-hpc', 'ccdg']))
@click.version_option(version=laims.__version__, prog_name='laims', message='%(prog)s %(version)s')
@click.pass_context
def cli(ctx, config, database, job_group, queue):
    ctx.obj = LaimsApp(config_file=config, database=database, job_group=job_group, queue=queue)

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
