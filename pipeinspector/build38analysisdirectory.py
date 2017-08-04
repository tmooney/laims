from directoryvalidation import DirectoryValidator

import sys

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
            sys.stderr.write(str(e))
            sys.stderr.write('\n')
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
                "*.cram.json": 1,
                "*[!t].vcf": 1, # this may fail for samples that end in a lowercase t
            }
            )
    _svtyper_validator = DirectoryValidator(
            {
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
            sys.stderr.write(str(e))
            sys.stderr.write('\n')
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
