from __future__ import division

import os

from laims.models import ComputeWorkflowSample
from laims.database import open_db
from laims.utils import force_make_dirs
from laims.lsf import LsfJob
from laims.commands.reband_gvcfs import chromosomes, ext_chromosomes

class OldbandandRewriteGvcfCmd(object):
    def __init__(self, java, max_mem, max_stack, gatk_jar, reference, break_multiple):
        hc_cmd = '{java} -Xmx{max_mem} -Xms{max_stack} -jar {gatk_jar} -T HaplotypeCaller -R {ref} -I {{input}} -o {{temp_output1}} -ERC GVCF -GQB 5 -GQB 20 -GQB 60 -variant_index_type LINEAR -variant_index_parameter 128000 -L {{chrom}}'
        combine_cmd = '{java} -Xmx{max_mem} -Xms{max_stack} -jar {gatk_jar} -T CombineGVCFs -R {ref} --breakBandsAtMultiplesOf {break_multiple} -V {{temp_output1}} -o {{temp_output2}}'
        stage_tmp = 'mv {{temp_output2}} {{output}}'
        stage_index = 'mv {{temp_output2}}.tbi {{output}}.tbi'
        remove_tmp = 'rm -f {{temp_output1}} {{temp_output1}}.tbi'
        cmdline = ' && '.join((
            hc_cmd,
            combine_cmd,
            stage_tmp,
            stage_index,
            remove_tmp
            ))
        self.cmd = cmdline.format(
                java=str(java),
                max_mem=str(max_mem),
                max_stack=str(max_stack),
                gatk_jar=str(gatk_jar),
                ref=str(reference),
                break_multiple=str(break_multiple)
                )

    def __call__(self, input_file, output_file, chrom):
        temp_output1 = output_file + '.raw_hc.tmp.vcf.gz'
        temp_output2 = output_file + '.tmp.vcf.gz'
        return self.cmd.format(input=input_file, output=output_file, temp_output1=temp_output1, temp_output2=temp_output2, chrom=chrom)

def oldband(app, output_dir, workorders):
    os.environ['LSF_NO_INHERIT_ENVIRONMENT'] = 'true'
    default_job_options = {
            'memory_in_gb': 10,
            'queue': app.queue,
            'docker': 'registry.gsc.wustl.edu/genome/gatk-3.5-0-g36282e4:1',
            }
    if app.job_group is not None:
        default_job_options['group'] = app.job_group
    job_runner=LsfJob(default_job_options)


    logdir = os.path.join(output_dir, 'log')

    Session = open_db(app.database)
    cmd = OldbandandRewriteGvcfCmd(
            java='/usr/bin/java',
            max_mem='8G',
            max_stack='8G',
            gatk_jar='/opt/GenomeAnalysisTK.jar',
            reference='/gscmnt/gc2802/halllab/ccdg_resources/genomes/human/GRCh38DH/all_sequences.fa',
            break_multiple=1000000
            )
    for wo in workorders:
        session = Session()
        for sample in session.query(ComputeWorkflowSample).filter(
                ComputeWorkflowSample.source_work_order == wo
                ):
            if (sample.analysis_cram_verifyed):
                cram_path = sample.analysis_cram_path

                sample_name = os.path.basename(cram_path)
                cram_file = os.path.join(sample.analysis_cram_path, '{}.cram'.format(sample_name))

                oldband_path = os.path.join(sample.analysis_gvcf_path, 'oldbanded_gvcfs')
                force_make_dirs(oldband_path)

                stdout_dir = os.path.join(logdir, sample_name)

                for chrom in chromosomes:
                    new_gzvcf = '{0}.{1}.g.vcf.gz'.format(sample_name, chrom)
                    output_gzvcf = os.path.join(oldband_path, new_gzvcf)
                    if not os.path.exists(output_gzvcf) or not os.path.exists(output_gzvcf + '.tbi'):
                        stdout = os.path.join(stdout_dir, new_gzvcf + '.oldbanded.log')
                        cmdline = cmd(cram_file, output_gzvcf, chrom)
                        lsf_options = {
                                'stdout': stdout,
                                }
                        job_runner.launch(cmdline, lsf_options)

                # do ext
                chrom_string = ' -L '.join(ext_chromosomes)
                new_gzvcf = '{0}.extChr.g.vcf.gz'.format(sample_name)
                output_gzvcf = os.path.join(oldband_path, new_gzvcf)
                if not os.path.exists(output_gzvcf) or not os.path.exists(output_gzvcf + '.tbi'):
                    script = os.path.join(oldband_path, 'oldband_extChr.sh')
                    cmdline = cmd(cram_file, output_gzvcf, chrom_string)
                    cmdline += ' && rm -f {0}'.format(script)
                    with open(script, 'w') as f:
                        f.write('#!/bin/bash\n')
                        f.write(cmdline)
                        f.write('\n')
                    stdout = os.path.join(stdout_dir, new_gzvcf + '.oldbanded.log')
                    lsf_options = {
                            'stdout': stdout,
                            }
                    job_runner.launch('/bin/bash {0}'.format(script), lsf_options)

