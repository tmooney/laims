import os, shutil, tempfile, unittest

from laims.app import LaimsApp
from laims.models import ComputeWorkflowSample, SampleCohort, SampleFile, SampleMetric

class LaimsModelsTest(unittest.TestCase):
    def setUp(self):
        self.data_d = os.path.join(os.path.dirname(__file__), "data")

        self.temp_d = tempfile.TemporaryDirectory()
        self.database_fn = os.path.join(self.temp_d.name, "test.db")
        shutil.copyfile(os.path.join(self.data_d, "test.db"), self.database_fn)

        laimsapp = LaimsApp()
        laimsapp.database = self.database_fn

    def tearDown(self):
        self.temp_d.cleanup()

    def test_sample(self):
        sm = LaimsApp().db_connection()
        session = sm()
        sample = session.query(ComputeWorkflowSample).get(8)
        self.assertIsNotNone(sample)

    def test_sample_cohort(self):
        sm = LaimsApp().db_connection()
        session = sm()
        cohorts = session.query(SampleCohort).filter_by(sample_id=8).all()
        self.assertEqual(len(cohorts), 1)
        sample = cohorts[0].sample
        self.assertEqual(sample.ingest_sample_name, "H_XY-BGM1073006")
        self.assertEqual(sample.ingest_sample_name, cohorts[0].sample.ingest_sample_name)

    def test_sample_file(self):
        sm = LaimsApp().db_connection()
        session = sm()
        files = session.query(SampleFile).filter_by(sample_id=8).all()
        self.assertEqual(len(files), 2)
        sample = files[0].sample
        self.assertEqual(sample.ingest_sample_name, "H_XY-BGM1073006")
        self.assertEqual(sample.ingest_sample_name, files[0].sample.ingest_sample_name)

    def test_sample_metric(self):
        sm = LaimsApp().db_connection()
        session = sm()
        metrics = session.query(SampleMetric).filter_by(sample_id=8).all()
        self.assertEqual(len(metrics), 2)
        sample = metrics[0].sample
        self.assertEqual(sample.ingest_sample_name, "H_XY-BGM1073006")
        self.assertEqual(sample.ingest_sample_name, metrics[1].sample.ingest_sample_name)

# -- LaimsModelsTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
