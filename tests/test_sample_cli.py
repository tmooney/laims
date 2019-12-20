import unittest
from click.testing import CliRunner

from laims.sample_cli import laims_sample_cli

class LaimsSampleCliTest(unittest.TestCase):

    def test1_laims_sample_cli(self):
        runner = CliRunner()

        result = runner.invoke(laims_sample_cli, [])
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(laims_sample_cli, ["--help"])
        self.assertEqual(result.exit_code, 0)

# -- LaimsSampleCliTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
