import os.path
import json
from pipeinspector import utils


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
