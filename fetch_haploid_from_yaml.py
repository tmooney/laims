#!/usr/bin/env python

import sys
import os
import yaml
from pipeinspector.build38realignmentdirectory import Build38RealignmentDirectory

for compute_directory in sys.argv[1:]:
    directory = Build38RealignmentDirectory(compute_directory)
    qc_yaml = directory.qc_yaml_file()
    if not os.path.exists(qc_yaml):
        sys.stderr.write('Missing {0}\n'.format(qc_yaml))
        continue
    with open(qc_yaml) as yaml_stream:
        data = yaml.load(yaml_stream)
        print '\t'.join([compute_directory,
            str(data['HAPLOID_COVERAGE']),
            str(data['FREEMIX']),
            str(data['interchromosomal_rate']),
            str(data['discordant_rate']),
            str(data['FIRST_OF_PAIR']['PF_MISMATCH_RATE']),
            str(data['SECOND_OF_PAIR']['PF_MISMATCH_RATE'])
            ])
