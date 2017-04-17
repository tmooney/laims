#!/usr/bin/env python

import json
import sys
import os

for input_json in sys.argv[1:]:
    with open(input_json) as json_file:
        json_data = json.load(json_file)
        bams = [ x[0] for x in json_data['sequence']['analysis']['data']]
        for bam in bams:
            if not os.path.isfile(bam):
                directory, filename = os.path.split(bam)
                print directory
