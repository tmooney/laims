import os.path
import json
import click
import laims
from logzero import logger


class LaimsApp(object):
    def __init__(self, config=None, database=None, job_group=None, queue=None):
        '''
        This sets up common options for the application
        '''
        self.database = database
        self.job_group = job_group
        self.queue = queue
        self.config_file = config
        if self.config_file is None:
            self.config_file = os.path.join(click.get_app_dir('laims'), 'config.json')
        self._load_config()

    def log_config(self):
        logger.info('Using config at {0}'.format(self.config_file))
        logger.info('Using database at {0}'.format(self.database))

    def _load_attr_from_config(self, name, json_data):
        if getattr(self, name) is None and name in json_data:
            setattr(self, name, json_data[name])

    def _load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file) as cfg:
                json_data = json.load(cfg)
                self._load_attr_from_config('database', json_data)
                self._load_attr_from_config('job_group', json_data)
        else:
            logger.error('No configuration file found at {0}'.format(self.config_file))


@click.group()
@click.option('--config', envvar='LAIMS_CONFIG_PATH')
@click.option('--database', envvar='LAIMS_DB_PATH')
@click.option('--job-group', default=None)
@click.option('--queue', default='ccdg', type=click.Choice(['research-hpc', 'ccdg']))
@click.version_option(version=laims.__version__, prog_name='laims', message='%(prog)s %(version)s')
@click.pass_context
def cli(ctx, config, database, job_group, queue):
    ctx.obj = LaimsApp(config, database, job_group, queue)

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

@cli.command(name='verify-gvcf', help='verify a GVCF with GATK ValidateVariants')
@click.option('--gvcf-path', help='Path to the GVCF', type=click.Path(exists=True), required=True)
@click.option('--reference-path', help='Path to the reference sequence', default="/gscmnt/gc2802/halllab/ccdg_resources/genomes/human/GRCh38DH/all_sequences.fa", type=click.Path(exists=True), required=True)
@click.option('--interval', help='The interval that was used to create the GVCF', type=str, required=True)
@click.pass_obj
def launch_verify_gvcf(app, gvcf_path, reference_path, interval):
    from laims.commands.verify_gvcf import verify_gvcf
    verify_gvcf(gvcf_path, reference_path, interval)

@cli.command(name='verify-bulk-gvcfs', help="verify a batch of GVCFs with GATK ValidateVariants using LSF")
@click.option('--tsv-path', help='Path to the TSV with GVCFs', type=click.Path(exists=True), required=True)
@click.option('--reference-path', help='Path to the reference sequence', default="/gscmnt/gc2802/halllab/ccdg_resources/genomes/human/GRCh38DH/all_sequences.fa", type=click.Path(exists=True), required=True)
@click.pass_obj
def launch_verify_bulk_gvcfs(app, tsv_path, reference_path):
    from laims.commands.verify_bulk_gvcfs import verify_bulk_gvcfs
    verify_bulk_gvcfs(app, tsv_path, reference_path)
