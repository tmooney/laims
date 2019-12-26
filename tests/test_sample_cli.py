import os, unittest
from click.testing import CliRunner

from laims.app import LaimsApp
from laims.sample_cli import laims_sample_cli, sample_list_cmd

class LaimsSampleCliTest(unittest.TestCase):
    def setUp(self):
        self.config_fn = os.path.join(os.path.dirname(__file__), "data", "laims.json")
        self.database_fn = os.path.join(os.path.dirname(__file__), "data", "test.db")

    def test1_laims_sample_cli(self):
        runner = CliRunner()

        result = runner.invoke(laims_sample_cli, [])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(laims_sample_cli, ["--help"])
        self.assertEqual(result.exit_code, 0)

    def test2_laims_sample_list_cmd(self):
        runner = CliRunner()
        laimsapp = LaimsApp(self.config_fn)
        laimsapp.database = self.database_fn

        result = runner.invoke(sample_list_cmd, ["--help"])
        self.assertEqual(result.exit_code, 0)

        result = runner.invoke(sample_list_cmd, ["-f", "2854371"])
        expected_output = """  ID  NAME                      WORK_ORDER
----  ----------------------  ------------
   1  H_XS-356091-0186761975       2854371
   2  H_XS-345839-0186762084       2854371
   3  H_XS-245227-0186760925       2854371
   4  H_XS-362472-0186761202       2854371
   5  H_XS-44610-0186760927        2854371"""
        try:
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.output, expected_output)
        except:
            print(result.output)
            raise

# -- LaimsSampleCliTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
