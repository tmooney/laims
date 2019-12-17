import os, unittest

from .context import laims
from laims.app import LaimsApp

class LaimsAppTest(unittest.TestCase):
    def setUp(self):
        self.config_fn = os.path.join(os.path.dirname(__file__), "data", "laims.json")

    def tearDown(self):
        LaimsApp.context = None

    def test1_init_fails(self):
        # FIXME This tests does not raise an exception in the test suite, dunno why
        with self.assertRaisesRegex(Exception, "Given config file /laims.json does not exist!"):
            laimsapp = LaimsApp(config_file="/laims.json")

    def test2_init(self):
        # init w/o config
        laimsapp = LaimsApp()
        self.assertIsNotNone(LaimsApp.context)

        # init w/ config
        LaimsApp.context = None # reset
        laimsapp = LaimsApp(config_file=self.config_fn, config={"database": "NOTDB"})
        self.assertIsNotNone(laimsapp)
        self.assertIsNotNone(laimsapp.context)
        self.assertEqual(laimsapp.config_file, self.config_fn)
        self.assertEqual(laimsapp.environment, 'test')
        self.assertEqual(laimsapp.database, 'NOTDB')
        self.assertEqual(laimsapp.lims_db_url, 'sqlite:///:memory:')

        # __setattr__
        self.assertIsNone(laimsapp.foo)
        laimsapp.foo = "bar"
        self.assertEqual(laimsapp.foo, "bar")
        self.assertEqual(LaimsApp().foo, "bar")

    def test3_lims_db(self):
        laimsapp = LaimsApp(config_file=self.config_fn, config={"database": "NOTDB"})
        self.assertIsNotNone(laimsapp)
        lims_db_url = laimsapp.lims_db_url
        self.assertIsNotNone(lims_db_url);
        LaimsApp.lims_db_url = None
        self.assertIsNone(laimsapp.lims_db_url)
        with self.assertRaisesRegex(Exception, "No lims_db_url"):
            laimsapp.lims_db_connection()

    def test4_job_options(self):
        laimsapp = LaimsApp(config_file=self.config_fn)
        laimsapp.queue = "ccdg"
        laimsapp.stdout = "/var/log/out"
        self.assertTrue(laimsapp)
        opts = laimsapp.lsf_job_options()
        expected_opts = {
            "queue": "ccdg",
            "docker": "registry.gsc.wustl.edu/mgi/laims:latest",
            "stdout": "/var/log/out",
        }
        self.assertDictEqual(opts, expected_opts, "LSF job options fetched from config")

# -- LaimsAppTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
