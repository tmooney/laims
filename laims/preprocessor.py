import os
import os.path
from logzero import logger
from laims.build38realignmentdirectory import Build38RealignmentDirectory
from laims.directoryvalidation import B38DirectoryValidator
from laims.shortcutter import Shortcutter
import laims.utils as utils


class B38Preprocessor(object):

    def __init__(self, dest_dir, job_runner, force=False):
        self.dest_dir = dest_dir
        self.logdir = os.path.join(self.dest_dir, 'log')
        self.lsf_job_runner = job_runner
        self.force = force
        utils.force_make_dirs(self.logdir)

    def _qc_files(self, d, outdir, stdout_dir):
        stdout = os.path.join(stdout_dir, 'qc_file_copy.log')
        qc_shortcutter = Shortcutter(d, outdir, '.qc_file_md5s.json', lambda x: x.qc_files())
        files = d.qc_files()
        copy_cmd = GenericRsyncCmd()
        files_to_copy = list()
        for f in files:
            filename = os.path.basename(f)
            outfile = os.path.join(outdir, filename)
            if not (qc_shortcutter.can_shortcut(f, outfile)):
                files_to_copy.append(f)
        if files_to_copy:
            copy_cmdline = copy_cmd(files_to_copy, outdir)
            self.lsf_job_runner.launch(copy_cmdline, {'stdout': stdout})

    def __call__(self, target_dir):
        # do some STUFF
        d = Build38RealignmentDirectory(target_dir)
        validator = B38DirectoryValidator(d)
        if validator.valid_directory() or self.force:
            logger.info('Directory valid for processing')
            outdir = self.output_directory(d)
            logger.info('Output directory is {0}'.format(outdir))
            utils.force_make_dirs(outdir)

            stdout_dir = os.path.join(self.logdir, d.sample_name())
            utils.force_make_dirs(stdout_dir)

            # always submit a CRAM transfer because we use rsync
            # and it checks these things...
            copy_stdout = os.path.join(stdout_dir, 'cram_copy.log')
            cram_shortcutter = Shortcutter(d, outdir, '.cram_file_md5s.json', lambda x: x.cram_files())
            cram, crai = d.cram_files()
            new_cram = os.path.basename(cram)
            output_cram = os.path.join(outdir, new_cram)
            output_crai = output_cram + '.crai'
            if not (cram_shortcutter.can_shortcut(cram, output_cram) and cram_shortcutter.can_shortcut(crai, output_crai)):
                cram_copy_cmd = RsyncCmd()
                cram_copy_cmdline = cram_copy_cmd(d.cram_file(), outdir)
                self.lsf_job_runner.launch(cram_copy_cmdline, {'stdout': copy_stdout})

            shortcutter = Shortcutter(d, outdir, '.gvcf_file_md5s.json', lambda x: x.all_gvcf_files())
            for gvcf in d.all_gvcf_files():
                new_gzvcf = os.path.basename(gvcf)
                output_gzvcf = os.path.join(outdir, new_gzvcf)
                if not shortcutter.can_shortcut(gvcf, output_gzvcf):
                    cmd = RewriteGvcfCmd(
                            java='/gapp/x64linux/opt/java/jdk/jdk1.8.0_60/bin/java',
                            max_mem='3500M',
                            max_stack='3500M',
                            gatk_jar='/gscmnt/gc2802/halllab/ccdg_resources/lib/GenomeAnalysisTK-3.5-0-g36282e4.jar',
                            reference='/gscmnt/gc2802/halllab/ccdg_resources/genomes/human/GRCh38DH/all_sequences.fa',
                            break_multiple=1000000
                            )
                    cmdline = cmd(gvcf, output_gzvcf)
                    script_file = os.path.join(stdout_dir, new_gzvcf + '.sh')
                    with open(script_file, 'w') as f:
                        f.write(cmd_line + "\n")
                    stdout = os.path.join(stdout_dir, new_gzvcf + '.log')
                    lsf_options = {
                            'stdout': stdout,
                            }
                    self.lsf_job_runner.launch(' '.join(['/bin/bash', script_file]), lsf_options)
            # Sync QC files
            qc_outdir = os.path.join(outdir, 'qc')
            utils.force_make_dirs(qc_outdir)
            self._qc_files(d, qc_outdir, stdout_dir)
            return outdir
        else:
            logger.warn('Invalid for processing')
            return None

    def output_directory(self, d):
        return os.path.join(self.dest_dir, d.sample_name())


class RewriteGvcfCmd(object):
    def __init__(self, java, max_mem, max_stack, gatk_jar, reference, break_multiple):
        self.cmd = '{java} -Xmx{max_mem} -Xms{max_stack} -jar {gatk_jar} -T CombineGVCFs -R {ref} --breakBandsAtMultiplesOf {break_multiple} -V {{input}} -o {{temp_output}} && mv {{temp_output}} {{output}} && mv {{temp_output}}.tbi {{output}}.tbi'.format(
                java=str(java),
                max_mem=str(max_mem),
                max_stack=str(max_stack),
                gatk_jar=str(gatk_jar),
                ref=str(reference),
                break_multiple=str(break_multiple),
                )

    def __call__(self, input_file, output_file):
        temp_output = output_file + '.tmp.vcf.gz'
        return self.cmd.format(input=input_file, output=output_file, temp_output=temp_output)


class GenericRsyncCmd(object):
    def __init__(self):
        self.cmd = 'rsync --verbose --archive {input} {output_dir}/'

    def __call__(self, input_files, output_dir):
        return self.cmd.format(input=' '.join(input_files), output_dir=output_dir)


class RsyncCmd(object):
    def __init__(self):
        self.cmd = 'rsync --verbose --archive {input} {output_dir}/ && rsync --verbose --archive {input}.md5 {output_dir}/ && rsync --verbose --archive {input}.crai {output_dir}/'

    def __call__(self, input_file, output_dir):
        return self.cmd.format(input=input_file, output_dir=output_dir)
