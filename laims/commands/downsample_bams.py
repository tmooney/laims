import os
import subprocess

from laims.lsf import LsfJob

def downsample_bams(app, bam_list, output_dir, probability):
    job_opts = {
        'memory_in_gb': 10,
        'queue': app.queue,
        'docker': 'broadinstitute/picard:2.21.4',
        'stdout': '/dev/null',
    }
    if app.job_group is not None: job_opts['group'] = app.job_group
    job_runner=LsfJob(job_opts)

    with open(bam_list) as fh:
        for line in fh:
            original_bam = line.strip()
            new_bam = os.path.join(output_dir, os.path.basename(original_bam))
            cmd = [
                '/usr/bin/java', '-Xmx8g', '-jar', '/usr/picard/picard.jar', 'DownsampleBam',
                'I='+original_bam, 'O='+new_bam, 'P='+str(probability)
            ]
            job_runner.launch(cmd)
