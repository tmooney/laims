import os, unittest

from .context import laims
from laims.build38realignmentdirectory import CramFile, InputJson, Build38RealignmentDirectory

class Build38RealignmentDirectoryTest(unittest.TestCase):

    def test1_compiles(self):
        self.assertTrue(1)

# -- Build38RealignmentDirectoryTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
