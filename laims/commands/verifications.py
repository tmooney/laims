from __future__ import print_function

import os
import sqlite3
import textwrap

def chromosomes():
    chroms = range(1, 23)
    chroms.extend(['X', 'Y'])
    chroms = [ 'chr{}'.format(c) for c in chroms ]
    return chroms

def verify_timestamps(sample, gvcf, tbi):
    if os.path.getmtime(gvcf) > os.path.getmtime(tbi):
        msg = ("{sample}\t[warn] "
               "GVCF ({gvcf}) is newer than TBI ({tbi}) "
               "-- please investigate!")
        msg.format(sample=sample, gvcf=gvcf, tbi=tbi)
        print(msg)

def verify_gvcfs_and_tbi_existance(sample, reband_gvcf, reband_tbi, chrom):
    for f in (reband_gvcf, reband_tbi):
        result = 'EXISTS' if os.path.exists(f) else 'MISSING'
        msg = "{sample}\t{c}\t{path}\t{result}".format(
            sample=sample,
            c=chrom,
            path=f,
            result=result
        )
        print(msg)

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
    data = [ d[0] for d in c.fetchall() ]

    for sample in data:
        sample_dir = os.path.join(cohort_path, sample)
        reband_dir = os.path.join(sample_dir, 'rebanded_gvcfs')

        if not os.path.isdir(sample_dir):
            print("{}\t[warn] Did not find sample directory: {}".format(sample, sample_dir))
            continue

        if not os.path.isdir(reband_dir):
            print("{}\t[warn] Did not find reband directory: {}".format(sample, reband_dir))
            continue

        chroms = chromosomes()
        for c in chroms:
            gvcf = "{}.{}.g.vcf.gz".format(sample, c)
            tbi = "{}.tbi".format(gvcf)
            reband_gvcf = os.path.join(reband_dir, gvcf)
            reband_tbi = os.path.join(reband_dir, tbi)

            verify_gvcfs_and_tbi_existance(sample, reband_gvcf, reband_tbi, c)
            verify_timestamps(sample, reband_gvcf, reband_tbi)
