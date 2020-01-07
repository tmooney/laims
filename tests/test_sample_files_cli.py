import os, shutil, tempfile, unittest
from click.testing import CliRunner
from sqlalchemy import update

from laims.app import LaimsApp
from laims.models import ComputeWorkflowSample, SampleFile
from laims.sample_files_cli import files_cli, update_cmd

class LaimsCohortsCliTest(unittest.TestCase):
    def setUp(self):
        self.data_dn = os.path.join(os.path.dirname(__file__), "data")

        self.temp_d = tempfile.TemporaryDirectory()
        self.database_fn = os.path.join(self.temp_d.name, "test.db")
        shutil.copyfile(os.path.join(self.data_dn, "test.db"), self.database_fn)

        laimsapp = LaimsApp()
        laimsapp.database = self.database_fn

    def tearDown(self):
        self.temp_d.cleanup()

    def test1_laims_sample_files_cli(self):
        runner = CliRunner()

        result = runner.invoke(files_cli, [])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(files_cli, ["--help"])
        self.assertEqual(result.exit_code, 0)

    def test2_laims_sample_files_update_cmd(self):
        runner = CliRunner()

        result = runner.invoke(update_cmd, ["--help"])
        self.assertEqual(result.exit_code, 0)

        #sm = LaimsApp().db_connection()
        #session = sm()

        samples = [ "H_XS-356091-0186761975", "H_XS-362472-0186761202", "H_WHEREAMI"]
        new_crams = list(map(lambda s: os.path.join("/mnt/data/crams", s + ".cram"), samples))

        with tempfile.NamedTemporaryFile(mode="w") as temp_f:
            temp_f.write("\n".join(new_crams))
            temp_f.flush()
            result = runner.invoke(update_cmd, [temp_f.name])

        try:
            self.assertEqual(result.exit_code, 0)
            new_crams = list(new_crams)
            expected_output = [ " ".join([samples[0], new_crams[0]]) ]
            expected_output += [ " ".join([samples[1], new_crams[1]]) ]
            expected_output += [ " ".join([samples[2], "NOT_FOUND"]) ]
            expected_output += [""]
            self.assertEqual(result.output, "\n".join(expected_output))
        except:
            print(result.output)
            raise

# -- LaimsCohortsCliTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
