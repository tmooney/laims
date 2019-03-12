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
    }
    job_runner=LsfJob(job_opts)

    with open(tsv_path) as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            # TWAM-App282Req70_04112.chr22.parsed.g.vcf.gz 
            tokens = os.path.basename(row[0]).split('.')
            interval = tokens[-5]
            cmd = [ "laims", "verify-gvcf", "--gvcf-path", row[0], "--reference", reference_path, "--interval", interval ]
            print(job_runner.dry_run(cmd, {}))
            #job_runner.launch(cmd)
