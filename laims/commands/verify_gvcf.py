from __future__ import print_function

import subprocess

def verify_gvcf(gvcf_path, reference_path, interval):
    cmd = [ 'gatk', '--java-options',  '-Xmx8G', 'ValidateVariants', '-V', gvcf_path, '-R', reference_path,
            '-L', interval, '--validate-GVCF' ]
    proc = subprocess.Popen(cmd)
    exit_code = proc.wait()
    gvcf_status = 'FAIL'
    if exit_code == 0 : 
        gvcf_status = 'PASS'

    gvcf_check_fname = "{}.check".format(gvcf_path)
    with open(gvcf_check_fname, 'w') as f:
        f.write(gvcf_status + "\n")

    #print(' '.join([str(exit_code), gvcf_status]))
