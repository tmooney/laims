import csv, os, subprocess, yaml

from jinja2 import Environment, FileSystemLoader
from laims.lsf import LsfJob
from laims.app import LaimsApp

def downsample_and_recall(app, inputs, output_dir):
    log_dir = os.path.join(output_dir, 'logs')
    os.mkdir(log_dir)
    os.mkdir(os.path.join(output_dir, 'results'))

    cromwell_job_opts = {
        'memory_in_gb' : 16,
        'queue': app.queue,
        'docker': app.docker,
        'stdout': os.path.join(log_dir, 'cromwell.log'),
    }
    if app.job_group is not None: cromwell_job_opts['group'] = app.job_group
    job_runner=LsfJob(cromwell_job_opts)

    chrs = [ (["chr{}".format(c)]) for c in range(1,23) ]
    chrs.extend([
        ["chrX"],
        ["chrY"],
        ["/gscmnt/gc2802/halllab/ccdg_resources/genomes/human/GRCh38DH/all_sequences.filtered-chromosome.ext.list"]
    ])


    workflow_inputs = {
        'reference': '/gscmnt/gc2802/halllab/ccdg_resources/genomes/human/GRCh38DH/all_sequences.fa',
        'downsample_strategy': 'ConstantMemory',
        'downsample_seed': 1,
        'emit_reference_confidence': 'GVCF',
        'max_alternate_alleles': 3,
        'variant_index_type': 'LINEAR',
        'variant_index_parameter': 128000,
        'read_filter': 'OverclippedRead',
        'intervals': chrs,
        'qc_minimum_mapping_quality': 0,
        'qc_minimum_base_quality': 0,
        'crams_to_downsample': [], #filled in from "inputs" file below
    }

    with open(inputs) as fh:
        reader = csv.reader(fh, delimiter='\t')
        for row in reader:
            sam = row[0]
            ratio = row[1]
            freemix = row[2]
            workflow_inputs['crams_to_downsample'].append(
                { 'cram': {'class': 'File', 'path': sam}, 'downsample_ratio': ratio, 'contamination': freemix }
            )

    input_yaml_path = os.path.join(output_dir, 'inputs.yaml')
    with open(input_yaml_path, 'w') as yaml_fh:
        yaml.dump(workflow_inputs, yaml_fh)

    config_template = os.path.join(LaimsApp().share_dir, 'cromwell.config.jinja')
    fs_loader = FileSystemLoader(searchpath = os.path.join(LaimsApp().share_dir))
    env = Environment(loader=fs_loader, autoescape=True)
    template = env.get_template('cromwell.config.jinja')

    cromwell_config_path = os.path.join(output_dir, 'cromwell.config')
    template.stream(
        log_dir=log_dir,
        output_dir=output_dir,
        lsf_queue=app.queue,
        lsf_job_group=app.job_group,
    ).dump(cromwell_config_path)

    cmd = [
        '/usr/bin/java', '-Dconfig.file=' + cromwell_config_path, '-Xmx14g', '-jar', '/opt/cromwell.jar', 'run',
        '-t', 'cwl', '-i', input_yaml_path, 'https://raw.githubusercontent.com/tmooney/cancer-genomics-workflow/downsample_and_recall/definitions/pipelines/gathered_downsample_and_recall.cwl' #TODO get a more canonical URL once things are merged
    ]
    job_runner.launch(cmd)
