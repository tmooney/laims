import os, shutil, tempfile, unittest
from click.testing import CliRunner

from laims.app import LaimsApp
from laims.sample_cli import laims_sample_cli, sample_list_cmd, sample_update_files_cmd

class LaimsSampleCliTest(unittest.TestCase):
    def setUp(self):
        self.data_d = os.path.join(os.path.dirname(__file__), "data")

        self.temp_d = tempfile.TemporaryDirectory()
        self.database_fn = os.path.join(self.temp_d.name, "test.db")
        shutil.copyfile(os.path.join(self.data_d, "test.db"), self.database_fn)

        laimsapp = LaimsApp()
        laimsapp.database = self.database_fn

    def tearDown(self):
        self.temp_d.cleanup()

    def test1_laims_sample_cli(self):
        runner = CliRunner()

        result = runner.invoke(laims_sample_cli, [])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(laims_sample_cli, ["--help"])
        self.assertEqual(result.exit_code, 0)

    def test2_laims_sample_list_cmd(self):
        runner = CliRunner()

        result = runner.invoke(sample_list_cmd, ["--help"])
        self.assertEqual(result.exit_code, 0)

        result = runner.invoke(sample_list_cmd, ["-f", "2854371"])
        try:
            self.assertEqual(result.exit_code, 0)
            expected_output = """  ID  NAME                      WORK_ORDER
----  ----------------------  ------------
   1  H_XS-356091-0186761975       2854371
   2  H_XS-345839-0186762084       2854371
   3  H_XS-245227-0186760925       2854371
   4  H_XS-362472-0186761202       2854371
   5  H_XS-44610-0186760927        2854371"""
            self.assertEqual(result.output, expected_output)
        except:
            print(result.output)
            raise

    def test3_laims_sample_update_files_cmd(self):
        runner = CliRunner()
        print(sample_update_files_cmd.name)

        result = runner.invoke(sample_update_files_cmd, ["--help"])
        self.assertEqual(result.exit_code, 0)

        samples = [ "H_XS-356091-0186761975", "H_XS-362472-0186761202", "H_WHEREAMI"]
        new_crams = list(map(lambda s: os.path.join("/mnt/data/crams", s + ".cram"), samples))

        with tempfile.NamedTemporaryFile(mode="w") as temp_f:
            temp_f.write("\n".join(new_crams))
            temp_f.flush()
            result = runner.invoke(sample_update_files_cmd, ["cram", temp_f.name])

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

# -- LaimsSampleCliTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
