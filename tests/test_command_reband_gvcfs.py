import os, unittest
from jinja2 import Template

from .context import laims
from laims.app import LaimsApp
from laims.commands.reband_gvcfs import RebandandRewriteGvcfCmd

class LaimsCommandRebandTest(unittest.TestCase):
    def setUp(self):
        self.dir_n = os.path.dirname(__file__)
        self.config_fn = os.path.join(self.dir_n, "data", "laims.json")
        self.laimsapp = LaimsApp(config_file=self.config_fn)

        self.laimsapp.share_dir = os.path.join(os.path.dirname(self.dir_n), "share")

    def test1_cmd_object(self):
        reband_template_fn = os.path.join(self.laimsapp.share_dir, 'reband-gvcfs.sh.jinja')
        self.assertTrue(os.path.exists(reband_template_fn))
        with open(reband_template_fn, 'r') as f:
            reband_template = Template(f.read())
        self.assertTrue(isinstance(reband_template, Template))

        laimsapp = self.laimsapp
        laimsapp.share_dir = os.path.join(os.getcwd(), 'share')
        reband_gvcfs_opts = laimsapp.reband_gvcfs_opts
        opts = {
            "java": laimsapp.java,
            "gatk_jar": laimsapp.gatk_jar,
            "reference": "/gscmnt/gc2802/halllab/ccdg_resources/genomes/human/GRCh38DH/all_sequences.fa",
            "max_mem": reband_gvcfs_opts["max_mem"],
            "max_stack": reband_gvcfs_opts["max_stack"],
            "break_multiple": reband_gvcfs_opts["break_multiple"],
            "chrom": 1,
            "freemix": 1,
            "cram_file": "sample.cram",
            "output_file": "output.g.vcf",
        }
        opts["temp_output1"] = opts['output_file'] + '.raw_hc.tmp.vcf.gz'
        opts["temp_output2"] = opts['output_file'] + '.tmp.vcf.gz'

        self.maxDiff = None
        reband_cmd = RebandandRewriteGvcfCmd(reference=opts['reference'])
        self.assertIsNotNone(reband_cmd)
        self.assertEqual(reband_cmd(cram_file="sample.cram", output_file="output.g.vcf", freemix="1", chrom="1"), reband_template.render(opts=opts))

# -- LaimsCommandRebandTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
