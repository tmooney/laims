import os, unittest

from .context import laims
from laims.build38analysisdirectory import AnalysisDirectory, AnalysisSvDirectory, QcDirectory

class Build38AnalysisDirectoryTest(unittest.TestCase):

    def test1_compiles(self):
        self.assertTrue(1)

# -- Build38AnalysisDirectoryTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
