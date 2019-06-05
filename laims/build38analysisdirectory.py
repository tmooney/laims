from laims.directoryvalidation import DirectoryValidator
from logzero import logger

import os.path

class AnalysisDirectory(object):

    _validator = DirectoryValidator(
            {
                "*.chr*.g.vcf.gz": 24,
                "*.chr*.g.vcf.gz.tbi": 24,
                "*.cram": 1,
                "*.crai": 1,
            }
            )

    def __init__(self, directory_path):
        self.path = directory_path
        self.output_file_dict = AnalysisDirectory._validator.collect_output_file_dict(self.path)
        try:
            AnalysisDirectory._validator.complete(self.path, self.output_file_dict)
            self.is_complete = True
        except RuntimeError as e:
            logger.warn(str(e))
            self.is_complete = False

        if self.is_complete:
            self._completion_time = AnalysisDirectory._validator.completion_time(self.path, self.is_complete, self.output_file_dict)


class AnalysisSvDirectory(object):
    _staging_validator = DirectoryValidator(
            {
                "*.cram": 1,
                "*.cram.crai": 1,
            }
            )

    _extract_validator = DirectoryValidator(
            {
                "*.discordants.bam": 1,
                "*.discordants.bam.bai": 1,
                "*.splitters.bam": 1,
                "*.splitters.bam.bai": 1,
            }
            )
    _cnvnator_validator = DirectoryValidator(
            {
                "*.cn.bed": 1,
                "*.cn.txt": 1,
                "*.cnvnator.out/*.root": 2,
            }
            )
    _lumpy_validator = DirectoryValidator(
            {
                "*[!t].vcf": 1,  # this may fail for samples that end in a lowercase t
            }
            )
    _svtyper_validator = DirectoryValidator(
            {
                "*.cram.json": 1,
                "*.gt.vcf": 1,
            }
            )

    def __init__(self, directory_path):
        self.path = directory_path
        self.staging_file_dict = dict()
        self.extract_file_dict = dict()
        self.cnvnator_file_dict = dict()
        self.lumpy_file_dict = dict()
        self.svtyper_file_dict = dict()
        # may want to consider constructing validators using sample name here instead of on class

    def validate_stage(self, validator, variable):
        variable = validator.collect_output_file_dict(self.path)
        try:
            validator.complete(self.path, variable)
            return True
        except RuntimeError as e:
            logger.warn(str(e))
            return False

    def staging_complete(self):
        return self.validate_stage(AnalysisSvDirectory._staging_validator, self.staging_file_dict)

    def extract_complete(self):
        return self.validate_stage(AnalysisSvDirectory._extract_validator, self.extract_file_dict)

    def cnvnator_complete(self):
        return self.validate_stage(AnalysisSvDirectory._cnvnator_validator, self.cnvnator_file_dict)

    def lumpy_complete(self):
        return self.validate_stage(AnalysisSvDirectory._lumpy_validator, self.lumpy_file_dict)

    def svtyper_complete(self):
        return self.validate_stage(AnalysisSvDirectory._svtyper_validator, self.svtyper_file_dict)


class QcDirectory(object):
    _validator = DirectoryValidator(
        {
            "X_chrom*": 2,
            "all_chrom*": 2,
            "bamutil_stats.txt": 1,
            "flagstat.out": 1,
            "insert_size*": 2,
            "mark_dups_metrics.txt": 1,
            "*verify_bam_id*": [4, 5],
            "wgs_metric_summary.txt": 1,
            "alignment_summary.txt": 1,
            "GC_bias*": 3,
        }
    )

    def __init__(self, directory_path):
        self.path = directory_path
        self.output_file_dict = QcDirectory._validator.collect_output_file_dict(self.path)
        try:
            QcDirectory._validator.complete(self.path, self.output_file_dict)
            self.is_complete = True
        except RuntimeError as e:
            logger.warn(str(e))
            self.is_complete = False

    def sample_name(self):
        '''
        Grabs internal sample name from the variant calling metrics file
        '''
        metrics_file = self.X_chrom_vc_detail_metrics()
        with open(metrics_file) as f:
            last_was_commented = False
            for line in f:
                if line.startswith('#'):
                    last_was_commented = True
                else:
                    if last_was_commented:
                        last_was_commented = False
                    else:
                        return line.rstrip().split('\t')[0]

    def flagstat_file(self):
        if self.output_file_dict is None:
            self._collect_output_file_dict()
        return self.output_file_dict['flagstat.out'][0]

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

    def _find_verify_bam_id_file(self, old_style, new_style):
        filepath = old_style if os.path.isfile(old_style) else new_style
        return filepath

    def verifybamid_self_sample_file(self):
        old_style_path = os.path.join(self.path, 'verify_bam_id.selfSM')
        new_style_path = os.path.join(self.path, 'GT_verify_bam_id.selfSM')
        valid_path = self._find_verify_bam_id_file(old_style_path, new_style_path)
        return valid_path

    def verifybamid_self_readgroup_file(self):
        old_style_path = os.path.join(self.path, 'verify_bam_id.selfRG')
        new_style_path = os.path.join(self.path, 'GT_verify_bam_id.selfRG')
        valid_path = self._find_verify_bam_id_file(old_style_path, new_style_path)
        return valid_path

    def verifybamid_depth_sample_file(self):
        old_style_path = os.path.join(self.path, 'verify_bam_id.selfSM')
        new_style_path = os.path.join(self.path, 'GT_verify_bam_id.selfSM')
        valid_path = self._find_verify_bam_id_file(old_style_path, new_style_path)
        return valid_path

    def verifybamid_depth_readgroup_file(self):
        old_style_path = os.path.join(self.path, 'verify_bam_id.selfRG')
        new_style_path = os.path.join(self.path, 'GT_verify_bam_id.selfRG')
        valid_path = self._find_verify_bam_id_file(old_style_path, new_style_path)
        return valid_path

    def bamutil_file(self):
        return os.path.join(self.path, 'bamutil_stats.txt')

    def X_chrom_vc_detail_metrics(self):
        return os.path.join(self.path, 'X_chrom.variant_calling_detail_metrics')

    def X_chrom_vc_summary_metrics(self):
        return os.path.join(self.path, 'X_chrom.variant_calling_summary_metrics')

    def all_chrom_vc_detail_metrics(self):
        return os.path.join(self.path, 'all_chrom.variant_calling_detail_metrics')

    def all_chrom_vc_summary_metrics(self):
        return os.path.join(self.path, 'all_chrom.variant_calling_summary_metrics')
