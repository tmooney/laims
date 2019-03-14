from __future__ import print_function

import csv
import os
import subprocess

from laims.lsf import LsfJob

def verify_bulk_gvcfs(tsv_path, reference_path):

    os.environ['LSF_DOCKER_PRESERVE_ENVIRONMENT'] = 'false'
    job_opts = {
        'memory_in_gb': 10,
        'queue': 'ccdg',
        'docker': 'broadinstitute/gatk:4.0.6.0',
        'group': '/apipe-builder/verify-gvcf',
        'email': 'ebelter@wustl.edu',
    }
    job_runner=LsfJob(job_opts)

    with open(tsv_path) as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            interval = get_interval_from_path(row[0])
            cmd = [ "laims", "verify-gvcf", "--gvcf-path", row[0], "--reference", reference_path, "--interval", interval ]
            #print(job_runner.dry_run(cmd, {}))
            job_runner.launch(cmd, {})


chromosomes = [ 'chr{}'.format(c) for c in range(1,23) ]
chromosomes.extend(['chrX', 'chrY'])
def get_interval_from_path(path):
    for t in os.path.basename(path).split('.'):
        for c in chromosomes:
            if t == c: return c
    raise 'Failed to get interval from file name: {}'.foramt(path)

