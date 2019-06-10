import os, unittest

from .context import laims
from laims.app import LaimsApp
from laims.preprocessor import GenericRsyncCmd, RewriteGvcfCmd

class LaimsPreprocessorTest(unittest.TestCase):

    def test1_rewrite_gvcf_cmd(self):
        laimsapp = LaimsApp(config_file=os.path.join("tests", "test_app", "laims.json"))
        cmd = RewriteGvcfCmd(
            reference='/gscmnt/gc2802/halllab/ccdg_resources/genomes/human/GRCh38DH/all_sequences.fa',
        )
        self.assertIsNotNone(cmd)
        cmdline = cmd('input.gvcf.gz', 'output.gvcf.gz')
        self.assertEqual('java -Xmx3500M -Xms3500M -jar /gatk/gatk-package-4.0.6.0-local.jar -T CombineGVCFs -R /gscmnt/gc2802/halllab/ccdg_resources/genomes/human/GRCh38DH/all_sequences.fa --breakBandsAtMultiplesOf 1000000 -V input.gvcf.gz -o output.gvcf.gz.tmp.vcf.gz && mv output.gvcf.gz.tmp.vcf.gz output.gvcf.gz && mv output.gvcf.gz.tmp.vcf.gz.tbi output.gvcf.gz.tbi', cmdline)

    def test2_generic_rsync_command(self):
        laimsapp = LaimsApp()
        cmd = GenericRsyncCmd()
        cmdline = ['rsync', '--verbose', '--archive', 'INPUT1', 'INPUT2', 'INPUT3', 'OUTDIR/']
        self.assertEqual(cmd(['INPUT1', 'INPUT2', 'INPUT3'], 'OUTDIR'), cmdline)

# -- LaimsPreprocessorTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
