import os, shutil, tempfile, unittest
from click.testing import CliRunner
from sqlalchemy import update

from laims.app import LaimsApp
from laims.models import ComputeWorkflowSample
from laims.metrics_cli import laims_metrics_cli, metrics_add_cmd

class LaimsCohortsCliTest(unittest.TestCase):
    def setUp(self):
        self.data_dn = os.path.join(os.path.dirname(__file__), "data")
        self.sample_dn = os.path.join(self.data_dn, "samples", "H_XS-356091-0186761975")

        self.temp_d = tempfile.TemporaryDirectory()
        self.database_fn = os.path.join(self.temp_d.name, "test.db")
        shutil.copyfile(os.path.join(self.data_dn, "test.db"), self.database_fn)

        laimsapp = LaimsApp()
        laimsapp.database = self.database_fn

    def tearDown(self):
        self.temp_d.cleanup()

    def test1_laims_metrics_cli(self):
        runner = CliRunner()

        result = runner.invoke(laims_metrics_cli, [])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(laims_metrics_cli, ["--help"])
        self.assertEqual(result.exit_code, 0)

    def test2_laims_metrics_add(self):
        runner = CliRunner()

        result = runner.invoke(metrics_add_cmd, ["--help"])
        self.assertEqual(result.exit_code, 0)

        sm = LaimsApp().db_connection()
        session = sm()
        for sample in session.query(ComputeWorkflowSample):
            sample.analysis_cram_path = self.sample_dn
            session.add(sample)
        session.flush()
        session.commit()

        result = runner.invoke(metrics_add_cmd)
        try:
            self.assertEqual(result.exit_code, 0)
            expected_output = """NAME 
"""
            self.assertEqual(result.output, expected_output)
        except:
            print(result.output)
            raise

# -- LaimsCohortsCliTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
