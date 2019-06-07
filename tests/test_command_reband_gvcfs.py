import os, unittest
from jinja2 import Template

from .context import laims
from laims.app import LaimsApp
from laims.commands.reband_gvcfs import RebandandRewriteGvcfCmd

class LaimsCommandRebandTest(unittest.TestCase):
    laimsapp = LaimsApp(config_file=os.path.join("tests", "test_app", "laims.json"))

    def test1_cmd_object(self):
        rebrand_template_fn = os.path.join('share', 'rebrand-gvcfs.sh.jinja')
        self.assertTrue(os.path.exists(rebrand_template_fn))
        with open(rebrand_template_fn, 'r') as f:
            rebrand_template = Template(f.read())
        self.assertTrue(isinstance(rebrand_template, Template))

        opts = {
            "java": self.laimsapp.java,
            "gatk_jar": self.laimsapp.gatk_jar,
            "reference": "/gscmnt/gc2802/halllab/ccdg_resources/genomes/human/GRCh38DH/all_sequences.fa",
            "max_mem": "'8G'",
            "max_stack": "'8G'",
            "break_multiple": 1000000,
            "chrom": 1,
            "freemix": 1,
            "input_file": "input.g.vcf",
            "output_file": "output.g.vcf",
        }
        opts["temp_output1"] = opts['output_file'] + '.raw_hc.tmp.vcf.gz'
        opts["temp_output2"] = opts['output_file'] + '.tmp.vcf.gz'

        rebrand_cmd = RebandandRewriteGvcfCmd(reference=opts['reference'], max_mem=opts['max_mem'], max_stack=opts['max_stack'], break_multiple=opts['break_multiple'])
        self.assertIsNotNone(rebrand_cmd)
        self.assertEqual(rebrand_cmd(input_file="input.g.vcf", output_file="output.g.vcf", freemix="1", chrom="1"), rebrand_template.render(opts=opts))

# -- LaimsCommandRebandTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
