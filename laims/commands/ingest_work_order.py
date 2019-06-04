import csv
from laims.preprocessor import B38Preprocessor
from laims.lsf import LsfJob
from laims.models import ComputeWorkflowSample
from laims.database import open_db
from logzero import logger


def ingest(app, csv_file, output_dir, force=False):
    Session = open_db(app.database)

    default_job_options = {
        'memory_in_gb': 5,
        'queue': app.queue,
        'docker': 'registry.gsc.wustl.edu/genome/genome_perl_environment',
        }
    if app.job_group is not None:
        default_job_options['group'] = app.job_group

    preprocessor = B38Preprocessor(output_dir, job_runner=LsfJob(default_job_options), force=force)

    columns = {'Compute Workflow Execution': 'compute_workflow_execution', 'Work Order': 'work_order', 'DNA': 'ingest_sample_name', 'WOI': 'woi', 'Working Directory': 'source_directory'}
    seen = set()
    with open(csv_file) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            output_json = dict()
            for key in columns:
                output_json[columns[key]] = row[key]
            seen_key = (
                    output_json['source_directory'],
                    output_json['ingest_sample_name'],
                    output_json['work_order']
                    )
            if seen_key in seen:
                logger.info('Duplicate row with identical source directory, sample name and workorder. Skipping...')
                continue
            else:
                seen.add(seen_key)

            outdir = preprocessor(output_json['source_directory'])
            is_valid = False
            analysis_cram_path = None
            analysis_gvcf_path = None
            if outdir is not None:
                is_valid = True
                analysis_cram_path = outdir
                analysis_gvcf_path = outdir
            session = Session()
            session.add(
                ComputeWorkflowSample(
                    source_work_order=output_json['work_order'],
                    ingest_sample_name=output_json['ingest_sample_name'],
                    source_directory=output_json['source_directory'],
                    woi=output_json['woi'],
                    valid_source_directory=is_valid,
                    analysis_cram_path=analysis_cram_path,
                    analysis_gvcf_path=analysis_gvcf_path
                    )
                )
            session.commit()
