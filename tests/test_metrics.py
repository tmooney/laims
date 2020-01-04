import os, shutil, tempfile, unittest

from laims.metrics import QcMetrics

class LaimsModelsTest(unittest.TestCase):
    def setUp(self):
        self.data_dn = os.path.join(os.path.dirname(__file__), "data", "samples", "H_XS-356091-0186761975", "qc")

    def test_verifyBamID(self):
        self.assertEqual(QcMetrics.verifyBamID_bn(), "verify_bam_id.selfSM")
        self.assertEqual(QcMetrics.verifyBamID_GT_bn(), "GT_verify_bam_id.selfSM")

        qc = QcMetrics(qc_dn = self.data_dn)
        self.assertEqual(qc.verifyBamID_fn(), os.path.join(self.data_dn, "verify_bam_id.selfSM"))

        expected_metrics = {
                "#SEQ_ID": "356091",
                "RG": "ALL",
                "CHIP_ID": "NA",
                "#SNPS": "276280",
                "#READS": "6791443",
                "AVG_DP": "24.58",
                "FREEMIX": "0.00509",
                "FREELK1": "2133454.31",
                "FREELK0": "2138630.24",
                "FREE_RH": "NA",
                "FREE_RA": "NA",
                "CHIPMIX": "NA",
                "CHIPLK1": "NA",
                "CHIPLK0": "NA",
                "CHIP_RH": "NA",
                "CHIP_RA": "NA",
                "DPREF": "NA",
                "RDPHET": "NA",
                "RDPALT": "NA",
                }
        metrics = qc.verifyBamID_metrics()
        self.assertDictEqual(metrics, expected_metrics)

    def test_picard_wgs(self):
        self.assertEqual(QcMetrics.picard_wgs_bn(), "wgs_metric_summary.txt")

        qc = QcMetrics(qc_dn = self.data_dn)
        self.assertEqual(qc.picard_wgs_fn(), os.path.join(self.data_dn, "wgs_metric_summary.txt"))

        expected_metrics = {
                "GENOME_TERRITORY": "2745186691",
                "MEAN_COVERAGE": "27.351283",
                "SD_COVERAGE": "10.042201",
                "MEDIAN_COVERAGE": "27",
                "MAD_COVERAGE": "4",
                "PCT_EXC_MAPQ": "0",
                "PCT_EXC_DUPE": "0.092479",
                "PCT_EXC_UNPAIRED": "0.002148",
                "PCT_EXC_BASEQ": "0",
                "PCT_EXC_OVERLAP": "0.024087",
                "PCT_EXC_CAPPED": "0.018111",
                "PCT_EXC_TOTAL": "0.136825",
                "PCT_1X": "0.998797",
                "PCT_5X": "0.99579",
                "PCT_10X": "0.991611",
                "PCT_15X": "0.977958",
                "PCT_20X": "0.901086",
                "PCT_25X": "0.659889",
                "PCT_30X": "0.324883",
                "PCT_40X": "0.027605",
                "PCT_50X": "0.007881",
                "PCT_60X": "0.00541",
                "PCT_70X": "0.004067",
                "PCT_80X": "0.003221",
                "PCT_90X": "0.002613",
                "PCT_100X": "0.002177",
                "HET_SNP_SENSITIVITY": "0.99463",
                "HET_SNP_Q": "23",
                }
        metrics = qc.picard_wgs_metrics()
        self.assertDictEqual(metrics, expected_metrics)

# -- LaimsModelsTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
