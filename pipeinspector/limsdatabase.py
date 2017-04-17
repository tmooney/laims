import os
import csv

class ReadCountInDb(object):
    def __init__(self):
        self._sql = 'sqlrun "select seq_id, filt_clusters * 2 from index_illumina where seq_id in ({0})" --instance warehouse --parse'

    def __call__(self, ids):
        total = 0
        id_string = ','.join(ids)
        output = os.popen(self._sql.format(id_string))
        reader = csv.reader(output, delimiter='\t')
        for row in reader:
            total += int(row[1])
        return total
