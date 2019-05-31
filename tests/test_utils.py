import datetime, re, tempfile, unittest

from .context import laims
from laims import utils

class LaimsUtilsTest(unittest.TestCase):
    expected_checksum = "36925bfbf7b3d3284706ae2582215cce"

    def test1_md5_checksum(self):
        f = tempfile.NamedTemporaryFile()
        f.write('This is just a test.\nSeriously!')
        f.flush()
        self.assertEqual(utils.md5_checksum(f.name), self.expected_checksum)

    def test2_read_first_checksum(self):
        f = tempfile.NamedTemporaryFile()
        f.write('{0}  {1}'.format(self.expected_checksum, 'test.txt'))
        f.flush()
        self.assertEqual(utils.read_first_checksum(f.name), self.expected_checksum)

    def test3_file_mtime(self):
        f = tempfile.NamedTemporaryFile()
        f.write('test')
        f.flush()
        mtime = utils.file_mtime(f.name)
        time_re = re.compile(r"\d\d\d\d\-\d\d\-\d\d \d\d:\d\d:\d\d\.\d\d\d\d\d\d")
        #2019-05-31 19:36:15.858331
        self.assertRegexpMatches(str(mtime), time_re)

# -- LaimsUtilsTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
