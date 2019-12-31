import os, shutil, tempfile, unittest
from click.testing import CliRunner

from laims.app import LaimsApp
from laims.cohorts_cli import laims_cohorts_cli, cohorts_list_cmd, cohorts_link_cmd

class LaimsCohortsCliTest(unittest.TestCase):
    def setUp(self):
        self.data_d = os.path.join(os.path.dirname(__file__), "data")

        self.temp_d = tempfile.TemporaryDirectory()
        self.database_fn = os.path.join(self.temp_d.name, "test.db")
        shutil.copyfile(os.path.join(self.data_d, "test.db"), self.database_fn)

        laimsapp = LaimsApp()
        laimsapp.database = self.database_fn

    def tearDown(self):
        self.temp_d.cleanup()

    def test1_laims_cohorts_cli(self):
        runner = CliRunner()

        result = runner.invoke(laims_cohorts_cli, [])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(laims_cohorts_cli, ["--help"])
        self.assertEqual(result.exit_code, 0)

    def test2_laims_cohorts_list_cmd(self):
        runner = CliRunner()

        result = runner.invoke(cohorts_list_cmd, ["--help"])
        self.assertEqual(result.exit_code, 0)

        result = runner.invoke(cohorts_list_cmd)
        try:
            self.assertEqual(result.exit_code, 0)
            expected_output = """NAME      SAMPLE_COUNT
------  --------------
afib                10"""
            self.assertEqual(result.output, expected_output)
        except:
            print(result.output)
            raise

    def test3_laims_cohorts_link(self):
        runner = CliRunner()

        result = runner.invoke(cohorts_link_cmd, ["--help"])
        self.assertEqual(result.exit_code, 0)

        result = runner.invoke(cohorts_link_cmd, ["new", "H_MISSING"])
        self.assertEqual(result.exit_code, 1)

        samples = [ "H_XS-356091-0186761975", "H_XS-362472-0186761202"]
        with tempfile.NamedTemporaryFile(mode="w") as temp_f:
            temp_f.write("\n".join(samples))
            temp_f.flush()
            result = runner.invoke(cohorts_link_cmd, ["new", temp_f.name])

        try:
            self.assertEqual(result.exit_code, 0)
            expected_output = "Added 2 samples to cohort new, skipped 0 existing."
            self.assertEqual(result.output, expected_output)
        except:
            print(result.output)
            raise

# -- LaimsCohortsCliTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
