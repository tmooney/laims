import os, subprocess, unittest
from mock import patch

from .context import laims
from laims.app import LaimsApp
from laims.lsf import BsubEmailOption, BsubMemoryOption, BsubDockerOption, LsfJob

class LaimsLsfTest(unittest.TestCase):
    laimsapp = LaimsApp(config_file=os.path.join(os.path.dirname(__file__), "data", "laims.json"))

    def test1_option_classes(self):
        config = self.laimsapp.context.config
        o = BsubDockerOption()
        self.assertTrue(isinstance(o, BsubDockerOption))
        self.assertEqual(o(config), ['-a', 'docker({})'.format(self.laimsapp.docker)])

        o = BsubEmailOption()
        self.assertTrue(isinstance(o, BsubEmailOption))
        self.assertEqual(o(config), ['-N', '-u', 'bobama@usa.gov'])

        o = BsubMemoryOption()
        self.assertTrue(isinstance(o, BsubMemoryOption))
        self.assertEqual(o({"memory_in_gb": 10}), ['-M', '10000000', '-R', '"select[mem>10000] rusage[mem=10000]"'])

    @patch('subprocess.check_call')
    def test2_lsf_job(self, subprocess_patch):
        config = self.laimsapp.context.config
        job = LsfJob(config)
        self.assertTrue(isinstance(job, LsfJob))

        available_opts = LsfJob.available_options
        self.assertEqual(len(available_opts), 9, "available options count is 9")

        expected_cmd = ['bsub', '-a', 'docker(registry.gsc.wustl.edu/mgi/laims:latest)', '-N', '-u', 'bobama@usa.gov', 'echo', 'hello', 'world']
        self.assertEqual(job.bsub_cmd(['echo', 'hello', 'world']), expected_cmd)

        expected_cmd = ['bsub', '-M', '10000000', '-R', '"select[mem>10000] rusage[mem=10000]"', '-a', 'docker(hello-world)', '-N', '-u', 'bobama@usa.gov', 'echo', 'hello', 'world']
        self.assertEqual(job.bsub_cmd(['echo', 'hello', 'world'], {"docker": "hello-world", "memory_in_gb": 10}), expected_cmd)

        subprocess_patch.return_value = 1
        self.assertFalse(job.launch(['echo', 'hello', 'world'], {"docker": "hello-world"}), expected_cmd)

# -- LaimsLsfTest

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-- __main__
