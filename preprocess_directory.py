#!/usr/bin/env python

import sys
import json
import os
import os.path
import errno
import argparse

from pipeinspector.build38realignmentdirectory import Build38RealignmentDirectory, InputJson, CramFile
from pipeinspector.flagstat import Flagstat
from pipeinspector.limsdatabase import ReadCountInDb
import pipeinspector.utils as utils
from pipeinspector.lsf import LsfJob


class B38DirectoryValidator(object):

    def __init__(self, directory):
        self.counter = ReadCountInDb()
        self.directory = directory

    def readcount_ok(self):
        input_json = InputJson(self.directory.input_json())
        seqids = input_json.seqids()
        unaligned_total = self.counter(seqids)
        flagstat = Flagstat(self.directory.flagstat_file())
        aligned_total = flagstat.read1 + flagstat.read2
        rv = aligned_total == unaligned_total
        if not rv:
            sys.stderr.write("Aligned total bp doesn't match unaligned total bp\n")
        return rv

    def sm_tag_ok(self):
        sm_tag = self.directory.sm_tag()
        rv = not sm_tag.startswith('H_')
        if not rv:
            sys.stderr.write("SM tag starts with H_\n")
        return rv

    def valid_directory(self):
        return self.directory.complete() and self.readcount_ok() and self.sm_tag_ok()


class B38Preprocessor(object):

    def __init__(self, dest_dir, job_runner):
        self.dest_dir = dest_dir
        self.logdir = os.path.join(self.dest_dir, 'log')
        self.lsf_job_runner = job_runner
        try:
            os.makedirs(self.logdir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def __call__(self, target_dir):
        # do some STUFF
        d = Build38RealignmentDirectory(target_dir)
        validator = B38DirectoryValidator(d)
        if validator.valid_directory():
            print 'Directory valid for processing'
            outdir = self.output_directory(d)
            print 'Output directory is {0}'.format(outdir)
            try:
                os.makedirs(outdir)
            except OSError as e:
                if e.errno != errno.EEXIST: #don't freak out if the directory exists
                    raise

            stdout_dir = os.path.join(self.logdir, d.sample_name())
            try:
                os.makedirs(stdout_dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

            # always submit a CRAM transfer because we use rsync and it checks these things...
            copy_stdout = os.path.join(stdout_dir, 'cram_copy.log')
            cram_shortcutter = Shortcutter(d, outdir, '.cram_file_md5s.json', lambda x: x.cram_files())
            cram, crai = d.cram_files()
            new_cram = os.path.basename(cram)
            output_cram = os.path.join(outdir, new_cram)
            output_crai = output_cram + '.crai'
            if not (cram_shortcutter.can_shortcut(cram, output_cram) and cram_shortcutter.can_shortcut(crai, output_crai)):
                cram_copy_cmd = RsyncCmd()
                cram_copy_cmdline = cram_copy_cmd(d.cram_file(), outdir)
                self.lsf_job_runner.launch(cram_copy_cmdline, { 'stdout': copy_stdout })

            shortcutter = GVCFShortcutter(d, outdir)
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
                    stdout = os.path.join(stdout_dir, new_gzvcf + '.log')
                    lsf_options = {
                            'stdout': stdout,
                            }
                    self.lsf_job_runner.launch(cmdline, lsf_options)
            return outdir
        else:
            print 'Invalid for processing'
            return None

    def output_directory(self, d):
        return os.path.join(self.dest_dir, d.sample_name())


class GVCFShortcutter(object):
    def __init__(self, input_directory, output_directory):
        self.output_directory = output_directory
        self.input_directory = input_directory
        self.input_md5s = self.input_md5_gvcfs()
        self.output_md5s = self.md5_gvcfs()

    # NOTE Md5 keys should be basename, not full path
    def md5_json(self):
        return os.path.join(self.output_directory, '.gvcf_file_md5s.json')

    def input_md5_gvcfs(self):
        md5s = dict()
        for filepath in self.input_directory.all_gvcf_files():
            filename = os.path.basename(filepath)
            md5s[filename] = utils.md5_checksum(filepath)
        return md5s

    def md5_gvcfs(self):
        json_file = self.md5_json()
        if os.path.isfile(json_file):
            with open(json_file) as jsonfile:
                return json.load(jsonfile)
        else:
            md5s = self.input_md5_gvcfs()
            with open(json_file, 'w') as output:
                json.dump(md5s, output)
            return md5s

    def can_shortcut(self, input_file, output_file):
        filename = os.path.basename(input_file)
        input_md5 = self.input_md5s[filename]
        try:
            output_md5 = self.output_md5s[filename]
        except KeyError:
            raise RuntimeError('{0} not previously recorded in {1} md5 json. This is likely due to a code change in lims or here.'.format(input_file, self.output_directory))
        if os.path.isfile(output_file) and input_md5 == output_md5:
            return True
        else:
            return False


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


class Shortcutter(object):
    def __init__(self, input_directory, output_directory, json_name, file_path_func):
        self.output_directory = output_directory
        self.input_directory = input_directory
        self.json_name = json_name
        self.file_path_func = file_path_func
        self._input_md5s = self._calc_input_md5s()
        self._output_md5s = self._calc_output_md5s()

    # NOTE Md5 keys should be basename, not full path
    def _md5_json(self):
        return os.path.join(self.output_directory, self.json_name)

    def _calc_input_md5s(self):
        md5s = dict()
        for filepath in self.file_path_func(self.input_directory):
            filename = os.path.basename(filepath)
            if os.path.isfile(filepath + '.md5'):
                # trust the md5 file to save compute
                md5s[filename] = utils.read_first_checksum(filepath + '.md5')
            else:
                md5s[filename] = utils.md5_checksum(filepath)
        return md5s

    def _calc_output_md5s(self):
        json_file = self._md5_json()
        if os.path.isfile(json_file):
            with open(json_file) as jsonfile:
                return json.load(jsonfile)
        else:
            md5s = self._calc_input_md5s()
            with open(json_file, 'w') as output:
                json.dump(md5s, output)
            return md5s

    def can_shortcut(self, input_file, output_file):
        filename = os.path.basename(input_file)
        input_md5 = self._input_md5s[filename]
        try:
            output_md5 = self._output_md5s[filename]
        except KeyError:
            raise RuntimeError('{0} not previously recorded in {1} md5 json. This is likely due to a code change in lims or here.'.format(input_file, self.output_directory))
        if os.path.isfile(output_file) and input_md5 == output_md5:
            return True
        else:
            return False


class RsyncCmd(object):
    def __init__(self):
        self.cmd = 'rsync --verbose --archive {input} {output_dir}/ && rsync --verbose --archive {input}.md5 {output_dir}/ && rsync --verbose --archive {input}.crai {output_dir}/'
    def __call__(self, input_file, output_dir):
        return self.cmd.format(input=input_file, output_dir=output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pre-process LIMS build38 realignment directory gvcfs', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('directories', metavar='<DIR>', nargs='+', help='LIMS output directories to process')
    parser.add_argument('--output-dir', metavar='<DIR>', default='/gscmnt/gc2758/analysis/ccdg/data', help='output directory to place processed gvcfs within a directory for the sample.')
    parser.add_argument('--job-group', metavar='<STR>', help='LSF job group for submitted jobs')
    #parser.add_argument('--dry-run', dest='dry_run', action='store_true', help='dry run, no jobs submitted')
    args = parser.parse_args()
    default_job_options = {
        'memory_in_gb': 5,
        'queue': 'research-hpc',
        'docker': 'registry.gsc.wustl.edu/genome/genome_perl_environment:23',
        }
    if args.job_group is not None:
        default_job_options['group'] = args.job_group

    preprocessor = B38Preprocessor(args.output_dir, job_runner=LsfJob(default_job_options))
    for d in args.directories:
        preprocessor(d)
