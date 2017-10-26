import glob
import os
import sys
import json
import re


class CramFile(object):

    def __init__(self, cram, samtools_path='/gscmnt/gc2802/halllab/ccdg_resources/bin/samtools-1.3.1'):
        self.cram = cram
        self.samtools_path = samtools_path

    @staticmethod
    def is_readgroup(string):
        return string.startswith('@RG')

    @staticmethod
    def sm_tag_for_readgroup_string(rg_string):
        sm_match = re.search(r'SM:(\S+)', rg_string)
        return sm_match.group(1)

    def sm_tag(self):
        header = os.popen('{samtools} view -H {cram}'.format(samtools=self.samtools_path, cram=self.cram))
        samples = set()
        for line in header:
            if self.is_readgroup(line):
                samples.add(self.sm_tag_for_readgroup_string(line))
        assert(len(samples) == 1)
        return samples.pop()


class InputJson(object):
    def __init__(self, input_json):
        with open(input_json) as json_file:
            self.json_data = json.load(json_file)

    @staticmethod
    def id_for_readgroup_string(rg_string):
        # ID:\d+
        seqid_match = re.search(r'ID:(\d+)', rg_string)
        return seqid_match.group(1)

    def seqids(self):
        return [ self.id_for_readgroup_string(x[1]) for x in self.json_data['sequence']['analysis']['data']]

    def bams(self):
        return [ x[0] for x in self.json_data['sequence']['analysis']['data']]


class Build38RealignmentDirectory(object):
    _expectations = {
            "*.cram": 1,
            "*.crai": 1,
            "*.chr*.g.vcf.gz": 24,
            "*.chr*.g.vcf.gz.tbi": 24,
            "*.extChr.g.vcf.gz": 1,
            "*.extChr.g.vcf.gz.tbi": 1,
            "X_chrom*": 2,
            "all_chrom*": 2,
            "bamutil_stats.txt": 1,
            "flagstat.out": 1,
            "insert_size*": 2,
            "mark_dups_metrics.txt": 1,
            "verify_bam_id*": 4,
            "wgs_metric_summary.txt": 1,
            "alignment_summary.txt": 1,
            "GC_bias*": 3,
            }

    def __init__(self, directory_path):
        self.path = directory_path
        self.output_file_dict = None
        self.is_complete = None
        self._completion_time = None
        self._sm_tag = None
        assert os.path.isdir(self.path)

    def _collect_output_file_dict(self):
        self.output_file_dict = dict()
        for glob_string in Build38RealignmentDirectory._expectations:
            glob_files = glob.glob(os.path.join(self.path, glob_string))
            self.output_file_dict[glob_string] = glob_files

    def complete(self):
        # NOTE - it would be cool to have a decorator for methods like this
        # that require the calling of some other method in the class
        if self.is_complete is not None:
            return self.is_complete
        else:
            if self.output_file_dict is None:
                self._collect_output_file_dict()
            for glob_string, num_expected in Build38RealignmentDirectory._expectations.iteritems():
                if not num_expected == len(self.output_file_dict[glob_string]):
                    self.is_complete = False
                    sys.stderr.write("Missing files matching {0}\n".format(glob_string))
                    return self.is_complete
            self.is_complete = True
            return self.is_complete

    def status(self):
        if self.complete():
            return 'done'
        else:
            return 'incomplete'

    def completion_time(self):
        if self._completion_time is None:
            if self.is_complete and self.output_file_dict is not None:
                self._completion_time = max([os.path.getmtime(x) for sublist in self.output_file_dict.itervalues() for x in sublist])
        return self._completion_time

    def sm_tag(self):
        if self._sm_tag is None:
            self._sm_tag = CramFile(self.cram_file()).sm_tag()
        return self._sm_tag

    def cram_file(self):
        if self.output_file_dict is None:
            self._collect_output_file_dict()
        return self.output_file_dict['*.cram'][0]

    def cram_files(self):
        cram_file = self.cram_file()
        return (cram_file, cram_file + '.crai')

    def sample_name(self):
        cram_file = self.cram_file()
        filename = os.path.basename(cram_file)
        sample_name = filename.split('.cram')[0]
        return sample_name

    def main_gvcf_files(self):
        if self.output_file_dict is None:
            self._collect_output_file_dict()
        return self.output_file_dict['*.chr*.g.vcf.gz']

    def all_gvcf_files(self):
        return [ x for files in [self.output_file_dict['*.chr*.g.vcf.gz'], self.output_file_dict['*.extChr.g.vcf.gz']] for x in files ]

    def flagstat_file(self):
        if self.output_file_dict is None:
            self._collect_output_file_dict()
        return self.output_file_dict['flagstat.out'][0]

    def input_json(self):
        return os.path.join(self.path, 'launch.json')

    def qc_yaml_file(self):
        return os.path.join(self.path, 'qc_metrics.yaml')

    def picard_alignment_metrics_file(self):
        return os.path.join(self.path, 'alignment_summary.txt')

    def picard_mark_duplicates_metrics_file(self):
        return os.path.join(self.path, 'mark_dups_metrics.txt')

    def picard_wgs_metrics_file(self):
        return os.path.join(self.path, 'wgs_metric_summary.txt')

    def picard_gc_bias_metrics_file(self):
        return os.path.join(self.path, 'GC_bias_summary.txt')

    def picard_gc_bias_output_file(self):
        return os.path.join(self.path, 'GC_bias.txt')

    def picard_gc_bias_chart(self):
        return os.path.join(self.path, 'GC_bias_chart.pdf')

    def picard_insert_size_metrics_file(self):
        return os.path.join(self.path, 'insert_size_summary.txt')

    def picard_insert_size_chart(self):
        return os.path.join(self.path, 'insert_size.pdf')

    def verifybamid_self_sample_file(self):
        return os.path.join(self.path, 'verify_bam_id.selfSM')

    def verifybamid_self_readgroup_file(self):
        return os.path.join(self.path, 'verify_bam_id.selfRG')

    def verifybamid_depth_sample_file(self):
        return os.path.join(self.path, 'verify_bam_id.depthSM')

    def verifybamid_depth_readgroup_file(self):
        return os.path.join(self.path, 'verify_bam_id.depthRG')

    def bamutil_file(self):
        return os.path.join(self.path, 'bamutil_stats.txt')

    def qc_files(self):
        glob_strings = (
            "X_chrom*",
            "all_chrom*",
            "bamutil_stats.txt",
            "flagstat.out",
            "insert_size*",
            "mark_dups_metrics.txt",
            "verify_bam_id*",
            "wgs_metric_summary.txt",
            "alignment_summary.txt",
            "GC_bias*",
            )
        if self.output_file_dict is None:
            self._collect_output_file_dict()
        return [y for x in glob_strings for y in self.output_file_dict[x]]
