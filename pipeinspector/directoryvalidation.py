import glob
import os.path

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
        reasons = [ '{0} is not complete'.format(directory) ]
        for glob_string, num_expected in self.expectations.iteritems():
            if not num_expected == len(output_file_dict[glob_string]):
                complete = False
                reasons.append('\tMissing files matching {0}'.format(glob_string))
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
        return max([os.path.getmtime(x) for sublist in output_file_dict.itervalues() for x in sublist])
