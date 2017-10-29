import os.path
import json
import click
import laims


class LaimsApp(object):
    def __init__(self, config=None, database=None, job_group=None):
        '''
        This sets up common options for the application
        '''
        self.database = database
        self.job_group = job_group
        self.config_file = config
        if self.config_file is None:
            self.config_file = os.path.join(click.get_app_dir('laims'), 'config.json')
        self._load_config()

    def _load_attr_from_config(self, name, json_data):
        if getattr(self, name) is None and name in json_data:
            setattr(self, name, json_data[name])

    def _load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file) as cfg:
                json_data = json.load(cfg)
                self._load_attr_from_config('database', json_data)
                self._load_attr_from_config('job_group', json_data)


@click.group()
@click.option('--config', envvar='LAIMS_CONFIG_PATH')
@click.option('--database', envvar='LAIMS_DB_PATH')
@click.option('--job-group', default=None)
@click.version_option(version=laims.__version__, prog_name='laims', message='%(prog)s %(version)s')
@click.pass_context
def cli(ctx, config, database, job_group):
    ctx.obj = LaimsApp(config, database, job_group)

@cli.command(help='ingest LIMS build38 realignment compute_workflow_execution csv')
@click.argument('workorder_csv')
@click.option('--output-dir')
@click.pass_obj
def ingest(app, workorder_csv, output_dir):
    print app.config_file
    print app.database
    from laims.commands.ingest_work_order import ingest
    ingest(app, workorder_csv, output_dir)

@cli.command(help='check analysis directory for completeness')
@click.pass_obj
def check(app):
    print app.config_file
    print app.database
    from laims.commands.check_analysis_dir import check_analysis_dir
    check_analysis_dir(app)

@cli.command(name='call-sv', help='run SV pipeline on a workorder')
@click.argument('workorder', nargs=-1, type=int)
@click.pass_obj
def call_sv(app, workorder):
    print app.config_file
    print app.database
    import laims.commands.call_svs
    laims.commands.call_svs.call_svs(app, workorder)

@cli.command(name='generate-qc-table', help='generate a table of qc results for a workorder')
@click.argument('workorder', nargs=-1, type=int)
@click.pass_obj
def generate_table(app, workorder):
    print app.config_file
    print app.database
    import laims.commands.generate_qc_table
    laims.commands.generate_qc_table.generate(app, workorder)

