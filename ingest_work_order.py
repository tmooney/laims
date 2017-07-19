#!/usr/bin/env python

import sys
import argparse
import csv
import dataset
import datetime
import json
from preprocess_directory import B38Preprocessor
from pipeinspector.lsf import LsfJob

from sqlalchemy import Column, Text, Integer, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ComputeWorkflowSample(Base):
    
    __tablename__ = 'csp_sample'
    __table_args__ = (
            UniqueConstraint('source_work_order', 'woi', 'source_directory', name='uniq_row'),
            )
    
    id = Column(Integer, primary_key=True)
    source_work_order = Column(Integer)
    woi = Column(Integer)
#    cohort = Column(Text)
    ingest_sample_name = Column(Text, unique=True, nullable=False) #convenience. Could change in the LIMS 
#    sm_tag_name = Column(Text)
    source_directory = Column(Text, unique=True, nullable=False)
    valid_source_directory = Column(Boolean)
    passed_qc = Column(Boolean)
    analysis_cram_path = Column(Text)
    analysis_cram_verifyed = Column(Boolean)
    analysis_gvcf_path = Column(Text)
    analysis_gvcfs_verified = Column(Boolean)
    analysis_sv_path = Column(Text)
    analysis_sv_verified = Column(Boolean)
    ingest_date = Column(DateTime, default=datetime.datetime.utcnow)


db = create_engine('sqlite:///tracking.db')
Base.metadata.create_all(db)
Session = sessionmaker(bind=db)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ingest LIMS build38 realignment compute_workflow_execution csv', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('csv', metavar='<FILE>', help='LIMS csv')
    parser.add_argument('--output-dir', metavar='<DIR>', default='/gscmnt/gc2758/analysis/ccdg/data', help='output directory to place processed gvcfs within a directory for the sample.')
    parser.add_argument('--qc-map', metavar='<FILE>', help='QC sample map')
    parser.add_argument('--output-json', metavar='<FILE>', help='json file of ingest information')
    #parser.add_argument('--dry-run', dest='dry_run', action='store_true', help='dry run, no jobs submitted')
    args = parser.parse_args()

    default_job_options = {
        'memory_in_gb': 5,
        'queue': 'research-hpc',
        'docker': 'registry.gsc.wustl.edu/genome/genome_perl_environment:23',
        }
    if args.job_group is not None:
        default_job_options['group'] = args.job_group

    preprocessor = B38Preprocessor(args.output_dir, job_runner=LsfJob(default_job_options))

    # TODO validate using logic from pre-process
    columns = {'Compute Workflow Execution': 'compute_workflow_execution', 'Work Order': 'work_order', 'DNA': 'ingest_sample_name', 'WOI': 'woi', 'Working Directory': 'source_directory'}
    seen = set()
    with open(args.csv) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            output_json = dict()
            #ingest_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            #output_json['ingest_date'] = ingest_time
            for key in columns:
                output_json[columns[key]] = row[key]
            seen_key = (
                    output_json['source_directory'],
                    output_json['ingest_sample_name'],
                    output_json['work_order']
                    )
            if seen_key in seen:
                sys.stderr.write('Duplicate row with identical source directory, sample name and workorder. Skipping...\n')
                continue
            else:
                seen.add(seen_key)

            outdir = preprocessor(output_json['source_directory'])
            is_valid = False
            analysis_cram_path = None
            analysis_gvcf_path = None
            if outdir is not None:
                is_valid = True
                analysis_cram_path = outdir
                analysis_gvcf_path = outdir
            session = Session()
            session.add(
                ComputeWorkflowSample(
                    source_work_order=output_json['work_order'],
                    ingest_sample_name=output_json['ingest_sample_name'],
                    source_directory=output_json['source_directory'],
                    woi=output_json['woi'],
                    valid_source_directory=is_valid,
                    analysis_cram_path=analysis_cram_path,
                    analysis_gvcf_path=analysis_gvcf_path
                    )
                )
            session.commit()
