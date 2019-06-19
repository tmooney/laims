import os, StringIO, sys, unittest

from .context import laims
from laims.app import LaimsApp
from laims.models import ComputeWorkflowSample
from laims import sample

class LaimsSampleTest(unittest.TestCase):

    def test1_list(self):
        LaimsApp(config_file=os.path.join("tests", "test_app", "laims.json"))
        with self.assertRaisesRegexp(Exception, "Unknown filter method: Barack"):
           sample.list(filter_by="Barack")
        with self.assertRaisesRegexp(Exception, "Invalid attribute to filter by: name"):
           sample.list(filter_by="name=Barack")
        out = StringIO.StringIO()
        sys.stdout = out
        sample.list(filter_by="id=1")
        expected_out = "ID    INGEST_SAMPLE_NAME      SOURCE_DIRECTORY\n----  ----------------------  ----------------------------------------------------\n1     H_XS-356091-0186761975  /gscmnt/gc13035/production/2853358/compute_159065627"
        self.assertEqual(out.getvalue(), expected_out)
        sys.stdout = sys.__stdout__

# -- LaimsSampleTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
