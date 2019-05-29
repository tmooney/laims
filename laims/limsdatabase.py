import os
import csv

import dataset
from jinja2 import Template

class ReadCountInDb(object):
    def __init__(self):
        self._sql = 'sqlrun "select seq_id, filt_clusters * 2 from index_illumina where seq_id in ({0})" --parse'

    #psql -U gscguest -h lims-db.gsc.wustl.edu lims
    def get_lims_database_connection(self):
        user = 'gscguest'
        password = app.get_lims_pwd ##TODO fix this
        server = 'lims-db.gsc.wustl.edu'
        database = 'lims'
        url = 'postgresql://{0}:{1}@{2}/{3}'.format(user, password, server, database)
        db = dataset.connect(url, schema='gsc')
        return db

    def get_read_counts(self, read_groups):
        # select seq_id, filt_clusters * 2 from index_illumina where seq_id in ({0})" --parse
        sql = """
            select ii.seq_id, ii.filt_clusters * 2 as total_clusters
            from   index_illumina ii
            where  ii.seq_id in ( {{ seq_ids | join(', ') }} )
        """

        template = Template(sql)
        rendered_sql = template.render(seq_ids=read_groups)
        db_connection = self.get_lims_database_connection()
        result = db_connection.query(rendered_sql)
        data = [ { 'seq_id' : row['seq_id'],
                   'filt_clusters' : row['total_clusters'] } for row in result ]
        return data

    def __call__(self, ids):
        total = 0
        output = self.get_read_counts(ids)
        if output:
            total = sum([ int(row['filt_clusters']) for row in output ])
        return total
