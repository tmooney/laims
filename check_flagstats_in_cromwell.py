#!/usr/bin/env python

import json
import sys
import os
import re
import csv

def total_from_db(ids):
    total = 0

    id_string = ','.join(ids)
    sql = 'sqlrun "select seq_id, filt_clusters * 2 from index_illumina where seq_id in ({0})" --instance warehouse --parse'.format(id_string)
    output = os.popen(sql)
    reader = csv.reader(output, delimiter='\t')
    for row in reader:
        total += int(row[1])
    return total

class Flagstat(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self._parse()

    def _parse(self):
        with open(self.file_path) as flagstat:
            self._values = [int(x.split(' ')[0]) for x in flagstat]

    @property
    def read1(self):
        """Number of read1 reads. Primary only."""
        return self._values[6]

    @property
    def read2(self):
        """Number of read2 reads. Primary only."""
        return self._values[7]

def id_for_readgroup_string(rg_string):
    # ID:\d+
    seqid_match = re.search(r'ID:(\d+)', rg_string)
    return seqid_match.group(1)

def unaligned_read_count(input_json):
    with open(input_json) as json_file:
        json_data = json.load(json_file)
        seqids = [ id_for_readgroup_string(x[1]) for x in json_data['sequence']['analysis']['data']]
    return total_from_db(seqids)

for compute_directory in sys.argv[1:]:
    input_json = os.path.join(compute_directory, "launch.json")
    sample_flagstat = Flagstat(os.path.join(compute_directory, "flagstat.out"))
    aligned_total = sample_flagstat.read1 + sample_flagstat.read2
    unaligned_total = unaligned_read_count(input_json)
    if aligned_total != unaligned_total:
        print "{0} different {1} vs {2}".format(compute_directory, unaligned_total, aligned_total)
    else:
        print "{0} same".format(compute_directory)
