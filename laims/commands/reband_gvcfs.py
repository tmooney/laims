from __future__ import division

from logzero import logger
from crimson import verifybamid
import os

from laims.app import LaimsApp
from laims.build38analysisdirectory import QcDirectory
from laims.models import ComputeWorkflowSample
from laims.database import open_db
from laims.utils import force_make_dirs
from laims.lsf import LsfJob

chromosomes = (
        'chr1',
        'chr2',
        'chr3',
        'chr4',
        'chr5',
        'chr6',
        'chr7',
        'chr8',
        'chr9',
        'chr10',
        'chr11',
        'chr12',
        'chr13',
        'chr14',
        'chr15',
        'chr16',
        'chr17',
        'chr18',
        'chr19',
        'chr20',
        'chr21',
        'chr22',
        'chrX',
        'chrY'
        )

ext_chromosomes = (
        'chrM',
        'chr1_KI270706v1_random',
        'chr1_KI270707v1_random',
        'chr1_KI270708v1_random',
        'chr1_KI270709v1_random',
        'chr1_KI270710v1_random',
        'chr1_KI270711v1_random',
        'chr1_KI270712v1_random',
        'chr1_KI270713v1_random',
        'chr1_KI270714v1_random',
        'chr2_KI270715v1_random',
        'chr2_KI270716v1_random',
        'chr3_GL000221v1_random',
        'chr4_GL000008v2_random',
        'chr5_GL000208v1_random',
        'chr9_KI270717v1_random',
        'chr9_KI270718v1_random',
        'chr9_KI270719v1_random',
        'chr9_KI270720v1_random',
        'chr11_KI270721v1_random',
        'chr14_GL000009v2_random',
        'chr14_GL000225v1_random',
        'chr14_KI270722v1_random',
        'chr14_GL000194v1_random',
        'chr14_KI270723v1_random',
        'chr14_KI270724v1_random',
        'chr14_KI270725v1_random',
        'chr14_KI270726v1_random',
        'chr15_KI270727v1_random',
        'chr16_KI270728v1_random',
        'chr17_GL000205v2_random',
        'chr17_KI270729v1_random',
        'chr17_KI270730v1_random',
        'chr22_KI270731v1_random',
        'chr22_KI270732v1_random',
        'chr22_KI270733v1_random',
        'chr22_KI270734v1_random',
        'chr22_KI270735v1_random',
        'chr22_KI270736v1_random',
        'chr22_KI270737v1_random',
        'chr22_KI270738v1_random',
        'chr22_KI270739v1_random',
        'chrY_KI270740v1_random',
        'chrUn_KI270302v1',
        'chrUn_KI270304v1',
        'chrUn_KI270303v1',
        'chrUn_KI270305v1',
        'chrUn_KI270322v1',
        'chrUn_KI270320v1',
        'chrUn_KI270310v1',
        'chrUn_KI270316v1',
        'chrUn_KI270315v1',
        'chrUn_KI270312v1',
        'chrUn_KI270311v1',
        'chrUn_KI270317v1',
        'chrUn_KI270412v1',
        'chrUn_KI270411v1',
        'chrUn_KI270414v1',
        'chrUn_KI270419v1',
        'chrUn_KI270418v1',
        'chrUn_KI270420v1',
        'chrUn_KI270424v1',
        'chrUn_KI270417v1',
        'chrUn_KI270422v1',
        'chrUn_KI270423v1',
        'chrUn_KI270425v1',
        'chrUn_KI270429v1',
        'chrUn_KI270442v1',
        'chrUn_KI270466v1',
        'chrUn_KI270465v1',
        'chrUn_KI270467v1',
        'chrUn_KI270435v1',
        'chrUn_KI270438v1',
        'chrUn_KI270468v1',
        'chrUn_KI270510v1',
        'chrUn_KI270509v1',
        'chrUn_KI270518v1',
        'chrUn_KI270508v1',
        'chrUn_KI270516v1',
        'chrUn_KI270512v1',
        'chrUn_KI270519v1',
        'chrUn_KI270522v1',
        'chrUn_KI270511v1',
        'chrUn_KI270515v1',
        'chrUn_KI270507v1',
        'chrUn_KI270517v1',
        'chrUn_KI270529v1',
        'chrUn_KI270528v1',
        'chrUn_KI270530v1',
        'chrUn_KI270539v1',
        'chrUn_KI270538v1',
        'chrUn_KI270544v1',
        'chrUn_KI270548v1',
        'chrUn_KI270583v1',
        'chrUn_KI270587v1',
        'chrUn_KI270580v1',
        'chrUn_KI270581v1',
        'chrUn_KI270579v1',
        'chrUn_KI270589v1',
        'chrUn_KI270590v1',
        'chrUn_KI270584v1',
        'chrUn_KI270582v1',
        'chrUn_KI270588v1',
        'chrUn_KI270593v1',
        'chrUn_KI270591v1',
        'chrUn_KI270330v1',
        'chrUn_KI270329v1',
        'chrUn_KI270334v1',
        'chrUn_KI270333v1',
        'chrUn_KI270335v1',
        'chrUn_KI270338v1',
        'chrUn_KI270340v1',
        'chrUn_KI270336v1',
        'chrUn_KI270337v1',
        'chrUn_KI270363v1',
        'chrUn_KI270364v1',
        'chrUn_KI270362v1',
        'chrUn_KI270366v1',
        'chrUn_KI270378v1',
        'chrUn_KI270379v1',
        'chrUn_KI270389v1',
        'chrUn_KI270390v1',
        'chrUn_KI270387v1',
        'chrUn_KI270395v1',
        'chrUn_KI270396v1',
        'chrUn_KI270388v1',
        'chrUn_KI270394v1',
        'chrUn_KI270386v1',
        'chrUn_KI270391v1',
        'chrUn_KI270383v1',
        'chrUn_KI270393v1',
        'chrUn_KI270384v1',
        'chrUn_KI270392v1',
        'chrUn_KI270381v1',
        'chrUn_KI270385v1',
        'chrUn_KI270382v1',
        'chrUn_KI270376v1',
        'chrUn_KI270374v1',
        'chrUn_KI270372v1',
        'chrUn_KI270373v1',
        'chrUn_KI270375v1',
        'chrUn_KI270371v1',
        'chrUn_KI270448v1',
        'chrUn_KI270521v1',
        'chrUn_GL000195v1',
        'chrUn_GL000219v1',
        'chrUn_GL000220v1',
        'chrUn_GL000224v1',
        'chrUn_KI270741v1',
        'chrUn_GL000226v1',
        'chrUn_GL000213v1',
        'chrUn_KI270743v1',
        'chrUn_KI270744v1',
        'chrUn_KI270745v1',
        'chrUn_KI270746v1',
        'chrUn_KI270747v1',
        'chrUn_KI270748v1',
        'chrUn_KI270749v1',
        'chrUn_KI270750v1',
        'chrUn_KI270751v1',
        'chrUn_KI270752v1',
        'chrUn_KI270753v1',
        'chrUn_KI270754v1',
        'chrUn_KI270755v1',
        'chrUn_KI270756v1',
        'chrUn_KI270757v1',
        'chrUn_GL000214v1',
        'chrUn_KI270742v1',
        'chrUn_GL000216v2',
        'chrUn_GL000218v1'
    )

class RebandandRewriteGvcfCmd(object):
    def __init__(self, reference):
        self.reference = reference
        hc_cmd = '{java} -Xmx{max_mem} -Xms{max_stack} -jar {gatk_jar} -T HaplotypeCaller -R {{ref}} -I {{cram_file}} -o {{temp_output1}} -ERC GVCF --max_alternate_alleles 3 -variant_index_type LINEAR -variant_index_parameter 128000 -L {{chrom}} -contamination {{freemix}} --read_filter OverclippedRead'
        combine_cmd = '{java} -Xmx{max_mem} -Xms{max_stack} -jar {gatk_jar} -T CombineGVCFs -R {{ref}} --breakBandsAtMultiplesOf {break_multiple} -V {{temp_output1}} -o {{temp_output2}}'
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
        laimsapp = LaimsApp()
        reband_gvcfs_opts = laimsapp.reband_gvcfs_opts
        self.cmd = cmdline.format(
                java=str(laimsapp.java),
                max_mem=str(reband_gvcfs_opts["max_mem"]),
                max_stack=str(reband_gvcfs_opts["max_stack"]),
                gatk_jar=str(laimsapp.gatk_jar),
                break_multiple=str(reband_gvcfs_opts["break_multiple"])
                )

    def __call__(self, cram_file, freemix, output_file, chrom):
        temp_output1 = output_file + '.raw_hc.tmp.vcf.gz'
        temp_output2 = output_file + '.tmp.vcf.gz'
        return self.cmd.format(cram_file=cram_file, ref=self.reference, freemix=freemix, output=output_file, temp_output1=temp_output1, temp_output2=temp_output2, chrom=chrom)

def reband(app, output_dir, workorders):
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
    logger.info("The output directory is: {}".format(logdir))

    Session = open_db(app.database)
    cmd = RebandandRewriteGvcfCmd(
            reference='/gscmnt/gc2802/halllab/ccdg_resources/genomes/human/GRCh38DH/all_sequences.fa',
            )

    logger.info("Processing {} work orders: {}".format(len(workorders), ' '.join([str(i) for i in workorders])))
    for wo in workorders:
        logger.info("Processing work order: {}".format(wo))
        session = Session()
        for sample in session.query(ComputeWorkflowSample).filter(
                ComputeWorkflowSample.source_work_order == wo
                ):
            logger.info("Processing sample: {}".format(sample.ingest_sample_name))
            logger.info("Analysis CRAM Path: {}".format(sample.analysis_cram_path))
            logger.info("Is analysis CRAM verified: {}".format(sample.analysis_cram_verifyed))
            if (sample.analysis_cram_verifyed):
                logger.info("Entering into the rebanding logic for {}".format(sample.ingest_sample_name))
                qc_dir = QcDirectory(os.path.join(sample.analysis_gvcf_path, 'qc'))
                logger.info("Ascertaining of the QC directory is complete ({})".format(qc_dir.path))
                if qc_dir.is_complete:
                    logger.info("Fetching verifybamid metrics")
                    verifybamid_metrics = verifybamid.parse(qc_dir.verifybamid_self_sample_file())
                    freemix_value = verifybamid_metrics['FREEMIX']
                    cram_path = sample.analysis_cram_path

                    sample_name = os.path.basename(cram_path)
                    cram_file = os.path.join(sample.analysis_cram_path, '{}.cram'.format(sample_name))

                    reband_path = os.path.join(sample.analysis_gvcf_path, 'rebanded_gvcfs')
                    force_make_dirs(reband_path)

                    stdout_dir = os.path.join(logdir, sample_name)

                    for chrom in chromosomes:
                        new_gzvcf = '{0}.{1}.g.vcf.gz'.format(sample_name, chrom)
                        output_gzvcf = os.path.join(reband_path, new_gzvcf)
                        if not os.path.exists(output_gzvcf) or not os.path.exists(output_gzvcf + '.tbi'):
                            stdout = os.path.join(stdout_dir, new_gzvcf + '.rebanded.log')
                            cmdline = cmd(cram_file, freemix_value, output_gzvcf, chrom)
                            script_file = os.path.join(stdout_dir, new_gzvcf + '.rebanded.sh')
                            with open(script_file, 'w') as f:
                                f.write(cmdline + "\n")
                            lsf_options = {
                                    'stdout': stdout,
                                    }
                            job_runner.launch(' '.join(['/bin/bash', script_file]), lsf_options)

                    # do ext
                    chrom_string = ' -L '.join(ext_chromosomes)
                    new_gzvcf = '{0}.extChr.g.vcf.gz'.format(sample_name)
                    output_gzvcf = os.path.join(reband_path, new_gzvcf)
                    if not os.path.exists(output_gzvcf) or not os.path.exists(output_gzvcf + '.tbi'):
                        script = os.path.join(reband_path, 'reband_extChr.sh')
                        cmdline = cmd(cram_file, freemix_value, output_gzvcf, chrom_string)
                        cmdline += ' && rm -f {0}'.format(script)
                        with open(script, 'w') as f:
                            f.write('#!/bin/bash\n')
                            f.write(cmdline)
                            f.write('\n')
                        stdout = os.path.join(stdout_dir, new_gzvcf + '.rebanded.log')
                        lsf_options = {
                                'stdout': stdout,
                                }
                        job_runner.launch('/bin/bash {0}'.format(script), lsf_options)

