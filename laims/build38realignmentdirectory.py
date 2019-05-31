import glob
import os
import json
import utils
from logzero import logger


class CramFile(object):

    def __init__(self, cram, samtools_path='/gscmnt/gc2802/halllab/ccdg_resources/bin/samtools-1.3.1'):
        self.cram = cram
        self.samtools_path = samtools_path
        self._header = None

    @property
    def header(self):
        if self._header is None:
            self._header = [x for x in os.popen('{samtools} view -H {cram}'.format(samtools=self.samtools_path, cram=self.cram))]
        return self._header

    def sm_tag(self):
        samples = set()
        for line in self.header:
            if utils.is_readgroup(line):
                samples.add(utils.sm_tag_for_readgroup_string(line))
        assert(len(samples) == 1)
        return samples.pop()

    def seqids(self):
        seqids = list()
        for line in self.header:
            if utils.is_readgroup(line):
                seqids.append(utils.id_for_readgroup_string(line))
        return seqids


class InputJson(object):
    def __init__(self, input_json):
        with open(input_json) as json_file:
            self.json_data = json.load(json_file)

    def seqids(self):
        return [ utils.id_for_readgroup_string(x[1]) for x in self.json_data['sequence']['analysis']['data']]

    def readgroups(self):
        # Note that as of 4/25 we are seeing json with two fastqs instead of a uBAM
        # In addition, we occasionally see json with no readgroup information at all
        data_list = self.json_data['sequence']['analysis']['data']
        if len(data_list[0]) in [2, 3] and data_list[0][-1].startswith('@RG'):
            return [x[0] for x in data_list]
        else:
            return data_list[0]


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
            "*verify_bam_id*": [4, 5],  # 4 files for old-style CCDG project case; 4 files for TopMed project case
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

    def _is_file_count_correct(glob_string, num_expected, input_files):
        if glob_string == '*verify_bam_id*':
            file_basenames = [os.path.basename(i) for i in input_files].sort()
            # TopMed verify_bam_id outputs have a 'GT' prefix on the '*.depthRG' files
            # CCDG verify_bam_id outputs do not have a 'GT' prefix on the '*.depthRG' files
            num_expected_files = num_expected[0] if file_basenames[0].startswith('GT') else num_expected[1]
        else:
            num_expected_files = num_expected

        num_actual_files = len(input_files)
        rv = num_expected_files == num_actual_files
        if rv == False:
            msg = "File count check mismatch: file type: '{}' -- expected : {} found : {}"
            msg = msg.format(glob_string, num_expected_files, num_actual_files)
            logger.error(msg)
        return rv

    def complete(self):
        # NOTE - it would be cool to have a decorator for methods like this
        # that require the calling of some other method in the class
        if self.is_complete is not None:
            return self.is_complete
        else:
            if self.output_file_dict is None:
                self._collect_output_file_dict()
            for glob_string, num_expected in Build38RealignmentDirectory._expectations.iteritems():
                file_count_check = self._is_file_count_correct(
                    glob_string,
                    num_expected,
                    self.output_file_dict[glob_string]
                )
                if file_count_check == False:
                    self.is_complete = False
                    logger.error("Missing files matching {0}\n".format(glob_string))
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

    def qc_files(self):
        glob_strings = (
            "X_chrom*",
            "all_chrom*",
            "bamutil_stats.txt",
            "flagstat.out",
            "insert_size*",
            "mark_dups_metrics.txt",
            "*verify_bam_id*",
            "wgs_metric_summary.txt",
            "alignment_summary.txt",
            "GC_bias*",
            )
        if self.output_file_dict is None:
            self._collect_output_file_dict()
        return [y for x in glob_strings for y in self.output_file_dict[x]]
