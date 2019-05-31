import glob
import os.path
from logzero import logger
from laims.limsdatabase import ReadCountInDb
from laims.flagstat import Flagstat
from laims.build38realignmentdirectory import CramFile, InputJson


class DirectoryValidator(object):

    def __init__(self, expectations):
        """
        Expectations is a dictionary where the key is a glob
        pattern and the value is the number of files expected to be returned
        """
        self.expectations = expectations

    def collect_output_file_dict(self, directory):
        output_file_dict = dict()
        for glob_string in self.expectations:
            glob_files = glob.glob(os.path.join(directory, glob_string))
            output_file_dict[glob_string] = glob_files
        return output_file_dict

    def complete(self, directory, output_file_dict=None):
        if output_file_dict is None:
            output_file_dict = self.collect_output_file_dict(directory)
        complete = True
        reasons = ['{0} is not complete'.format(directory)]
        for glob_string, num_expected in self.expectations.iteritems():
            if not num_expected == len(output_file_dict[glob_string]):
                complete = False
                reasons.append(
                    '\tMissing files matching {0}'.format(glob_string)
                )
            for file_ in output_file_dict[glob_string]:
                if os.path.getsize(file_) == 0:
                    complete = False
                    reasons.append('\t{0} has 0 size'.format(file_))
        if not complete:
            raise RuntimeError('\n'.join(reasons))

    def completion_time(self, directory, complete=None, output_file_dict=None):
        if complete is None:
            complete = self.complete(directory)
        if output_file_dict is None:
            output_file_dict = self.collect_output_file_dict(directory)
        return max([os.path.getmtime(x)
                    for sublist in output_file_dict.itervalues()
                    for x in sublist])


# NOTE This is another type of directory validator
# FIXME It should be harmonized with the class above
class B38DirectoryValidator(object):

    def __init__(self, directory):
        self.counter = ReadCountInDb()
        self.directory = directory

    def readcount_ok(self):
        cram = CramFile(self.directory.cram_file())
        seqids = cram.seqids()
        logger.info("Input JSON: {}".format(self.directory.input_json()))
        input_json = InputJson(self.directory.input_json())
        expected_seqids = input_json.readgroups()
        if len(expected_seqids) != len(seqids):
            logger.error("Number of BAMs in JSON {0} doesn't match readgroups in CRAM {1}".format(len(expected_seqids), len(seqids)))
            return False
        unaligned_total = self.counter(seqids)
        flagstat = Flagstat(self.directory.flagstat_file())
        logger.info("Flagstats: {}".format(self.directory.flagstat_file()))
        aligned_total = flagstat.read1 + flagstat.read2
        rv = aligned_total == unaligned_total
        if not rv:
            logger.error("Aligned total bp ({}) doesn't match unaligned total bp ({})".format(aligned_total, unaligned_total))
        return rv

    def sm_tag_ok(self):
        sm_tag = self.directory.sm_tag()
        rv = not sm_tag.startswith('H_')
        if not rv:
            logger.error("SM tag starts with H_")
        return rv

    def valid_directory(self):
        return self.directory.complete() and self.readcount_ok() and self.sm_tag_ok()
