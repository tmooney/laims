import os, unittest

from .context import laims
from laims.cli import LaimsApp

class LaimsAppTest(unittest.TestCase):

    def test11_init_fails(self):
        with self.assertRaises(IOError) as cm:
            TenxApp("/laims.json")
        self.assertTrue("No such file or directory" in cm.exception)

    def test12_init(self):
        # init w/o config
        laimsapp = LaimsApp()
        self.assertIsNotNone(laimsapp.config)

        # init w/ config
        laimsapp = LaimsApp(config_file=os.path.join("tests", "test_cli", "laims.json"))
        self.assertIsNotNone(laimsapp)
        self.assertIsNotNone(laimsapp.config)
        self.assertEqual(laimsapp.get_config('environment'), 'test')
        self.assertIsNone(laimsapp.get_config('blah'))

# -- LaimsAppTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
