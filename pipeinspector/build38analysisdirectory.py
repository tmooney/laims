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
