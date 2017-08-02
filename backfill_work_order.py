#!/usr/bin/env python

import sys
import os
import argparse
import csv
import datetime
from preprocess_directory import B38DirectoryValidator, B38Preprocessor
from pipeinspector.build38realignmentdirectory import Build38RealignmentDirectory
import pipeinspector.utils as putils
from pipeinspector.models import Base, ComputeWorkflowSample

from sqlalchemy import Column, Text, Integer, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db = create_engine('sqlite:///tracking.db')
#db = create_engine('sqlite:///test.db')
Base.metadata.create_all(db)
Session = sessionmaker(bind=db)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ingest LIMS build38 realignment compute_workflow_execution csv', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('csv', metavar='<FILE>', help='LIMS csv')
    parser.add_argument('--output-dir', metavar='<DIR>', default='/gscmnt/gc2758/analysis/ccdg/data', help='output directory to place processed gvcfs within a directory for the sample.')
    parser.add_argument('--job-group', metavar='<STR>', help='LSF job group for submitted jobs')
    parser.add_argument('--qc-map', metavar='<FILE>', help='QC sample map')
    parser.add_argument('--output-json', metavar='<FILE>', help='json file of ingest information')
    parser.add_argument('--force', dest='force', action='store_true', help='load regardless of whether the directory is regarded as valid')
    #parser.add_argument('--dry-run', dest='dry_run', action='store_true', help='dry run, no jobs submitted')
    args = parser.parse_args()

    default_job_options = {
        'memory_in_gb': 5,
        'queue': 'research-hpc',
        'docker': 'registry.gsc.wustl.edu/genome/genome_perl_environment:23',
        }
    if args.job_group is not None:
        default_job_options['group'] = args.job_group

    preprocessor = B38Preprocessor(args.output_dir, None)

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

            target_dir = Build38RealignmentDirectory(output_json['source_directory'])
            validator = B38DirectoryValidator(target_dir)
            outdir = preprocessor.output_directory(target_dir)
            analysis_cram_path = outdir
            analysis_gvcf_path = outdir
            is_valid = validator.valid_directory()
            # guess ingest date from md5 checksum
            md5_file = os.path.join(analysis_gvcf_path, '.gvcf_file_md5s.json')
            if os.path.exists(md5_file):
                inferred_timestamp = putils.file_mtime(md5_file)
            else:
                is_valid = False

            if is_valid or args.force:
                session = Session()
                session.add(
                    ComputeWorkflowSample(
                        source_work_order=output_json['work_order'],
                        ingest_sample_name=output_json['ingest_sample_name'],
                        source_directory=output_json['source_directory'],
                        woi=output_json['woi'],
                        valid_source_directory=is_valid,
                        analysis_cram_path=analysis_cram_path,
                        analysis_gvcf_path=analysis_gvcf_path,
                        ingest_date=inferred_timestamp
                        )
                    )
                session.commit()
                sys.stderr.write('Loaded {0}\n'.format(output_json['ingest_sample_name']))
            else:
                sys.stderr.write('{0} is invalid and will not be loaded\n'.format(output_json['ingest_sample_name']))
