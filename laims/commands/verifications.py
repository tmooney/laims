from __future__ import print_function

import os
import sqlite3
import textwrap

def chromosomes():
    chroms = range(1, 23)
    chroms.append('X', 'Y')
    chroms = [ 'chr{}'.format(c) for c in chroms ]
    return chroms

def verify_gvcfs(database, work_order, cohort_path):
    sql = textwrap.dedent("""
        select ingest_sample_name
        from   csp_sample cs
        where  cs.source_work_order = ?
    """)

    #print("database is: {}".format(database))
    #print("work-order: {}".format(work_order))
    #print("cohort-path: {}".format(cohort_path))
    #print("sql: {}".format(sql))

    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute(sql, (work_order,))
    data = c.fetchall()

    for sample in data:
        sample_dir = os.path.join(cohort_path, sample)
        reband_dir = os.path.join(sample_dir, 'rebanded_gvcfs')

        if not os.path.isdir(sample_dir):
            print("{}\t[warn] Did not find sample directory: {}".format(sample, sample_dir))
            continue

        if not os.path.isdir(reband_dir):
            print("{}\t[warn] Did not find reband directory: {}".format(reband_dir))
            continue

        chroms = chromosomes()
        for c in chroms:
            gvcf = "{}.{}.g.vcf.gz".format(sample, c)
            tbi = "{}.tbi".format(gvcf)
            reband_gvcf = os.path.join(reband_dir, gvcf)
            reband_tbi = os.path.join(reband_dir, tbi)

            for f in (reband_gvcf, reband_tbi):
                result = 'EXISTS' if os.path.exists(f) else 'MISSING'
                msg = "{sample}\t{c}\t{path}\t{result}".format(
                    sample=sample,
                    c=c,
                    path=f,
                    result=result
                )
                print(msg)
