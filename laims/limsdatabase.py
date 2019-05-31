import csv, os
from jinja2 import Template

from laims.app import LaimsApp

class ReadCountInDb(object):
    def __init__(self):
        self._sql = 'sqlrun "select seq_id, filt_clusters * 2 from index_illumina where seq_id in ({0})" --parse'

    def get_read_counts(self, read_groups):
        #psql -U gscguest -h lims-db.gsc.wustl.edu lims
        # select seq_id, filt_clusters * 2 from index_illumina where seq_id in ({0})" --parse
        sql = """
            select ii.seq_id, ii.filt_clusters * 2 as total_clusters
            from   index_illumina ii
            where  ii.seq_id in ( {{ seq_ids | join(', ') }} )
        """

        template = Template(sql)
        rendered_sql = template.render(seq_ids=read_groups)
        db = LaimsApp().lims_db_connection()
        result = db.query(rendered_sql)
        data = [ { 'seq_id' : row['seq_id'],
                   'filt_clusters' : row['total_clusters'] } for row in result ]
        return data

    def __call__(self, ids):
        total = 0
        output = self.get_read_counts(ids)
        if output:
            total = sum([ int(row['filt_clusters']) for row in output ])
        return total
