from __future__ import print_function
import csv, os, subprocess

from laims.app import LaimsApp
from laims.lsf import LsfJob

def verify_bulk_gvcfs(tsv_path, reference_path):
    os.environ['LSF_DOCKER_PRESERVE_ENVIRONMENT'] = 'false'

    job_opts = LaimsApp().lsf_job_options()
    job_opts["memory_in_gb"] = 10
    job_runner = LsfJob(job_opts)

    with open(tsv_path) as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            interval = get_interval_from_path(row[0])
            cmd = [ "laims", "verify-gvcf", "--gvcf-path", row[0], "--reference-path", reference_path, "--interval", interval ]
            job_runner.launch(cmd, cmd_options={"stdbn": ".".join([os.path.basename(row[0]), "out"])})

#-- verify_bulk_gvcfs

chromosomes = [ 'chr{}'.format(c) for c in range(1,23) ]
chromosomes.extend(['chrX', 'chrY'])
def get_interval_from_path(path):
    for t in os.path.basename(path).split('.'):
        if t == 'extChr': return "/gscmnt/gc2802/halllab/ccdg_resources/genomes/human/GRCh38DH/all_sequences.filtered-chromosome.list.ext"
        for c in chromosomes:
            if t == c: return c
    raise Exception('Failed to get interval from file name: {}'.format(path))

#-- get_interval_from_path
