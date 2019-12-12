import os, subprocess, unittest
from mock import patch
from click.testing import CliRunner

from laims.app import LaimsApp
from laims.commands import verify_bulk_gvcfs
from laims.cli import launch_verify_bulk_gvcfs

class VerifyBulkGvcfsTest(unittest.TestCase):
    def setUp(self):
        self.data_d = os.path.join(os.path.dirname(__file__), "data")
        self.tsv_path = os.path.join(self.data_d, "gvcfs.tsv")
        self.ref_fn = os.path.join(self.data_d, "ref.fa")
        LaimsApp(config={"queue": "ccdg"})

    def test0_get_intervla_from_path(self):
        with self.assertRaisesRegex(Exception, "Failed to get interval from file name: sample.no-chr.gvcf.gz"):
            verify_bulk_gvcfs.get_interval_from_path("sample.no-chr.gvcf.gz")
        self.assertEqual(verify_bulk_gvcfs.get_interval_from_path("sample.chr10.gvcf.gz"), "chr10")

    @patch("subprocess.check_call")
    def test1_verify_bulk_gvcfs_cmd(self, check_call_patch):
        runner = CliRunner()

        result = runner.invoke(launch_verify_bulk_gvcfs, [])
        self.assertEqual(result.exit_code, 2)

        result = runner.invoke(launch_verify_bulk_gvcfs, ["--help"])
        self.assertEqual(result.exit_code, 0)

        check_call_patch.return_value = 0
        result = runner.invoke(launch_verify_bulk_gvcfs, ["--tsv-path", self.tsv_path, "--reference-path", self.ref_fn])
        try:
            self.assertEqual(result.exit_code, 0)
        except:
            print(result.output)
            raise

# -- VerifyBulkGvcfsTest

if __name__ == '__main__':
    unittest.main(verbosity=2)
