import os, unittest

from .context import laims
from laims.app import LaimsApp

class LaimsAppTest(unittest.TestCase):

    def test1_init_fails(self):
        with self.assertRaisesRegexp(Exception, "Given config file /laims.json does not exist!") as cm:
            LaimsApp(config_file="/laims.json")

    def test2_init(self):
        # init w/o config
        laimsapp = LaimsApp()
        self.assertIsNotNone(LaimsApp.context)

        # init w/ config
        LaimsApp.context = None # reset
        laimsapp = LaimsApp(config_file=os.path.join("tests", "test_app", "laims.json"), config={"database": "NOTDB"})
        self.assertIsNotNone(laimsapp)
        self.assertIsNotNone(laimsapp.context)
        self.assertEqual(laimsapp.config_file, os.path.join("tests", "test_app", "laims.json"))
        self.assertEqual(laimsapp.environment, 'test')
        self.assertEqual(laimsapp.database, 'NOTDB')
        self.assertEqual(laimsapp.lims_db_url, 'sqlite:///:memory:')

        # __setattr__
        self.assertIsNone(laimsapp.foo)
        laimsapp.foo = "bar"
        self.assertEqual(laimsapp.foo, "bar")
        self.assertEqual(LaimsApp().foo, "bar")

    def test3_lims_db(self):
        laimsapp = LaimsApp()
        lims_db_url = laimsapp.lims_db_url
        self.assertIsNotNone(lims_db_url);
        LaimsApp.lims_db_url = None
        self.assertIsNone(laimsapp.lims_db_url)
        with self.assertRaisesRegexp(Exception, "No lims_db_url"):
            laimsapp.lims_db_connection()

# -- LaimsAppTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__