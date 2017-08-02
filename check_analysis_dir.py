#!/usr/bin/env python

import sys
import argparse

from pipeinspector.build38analysisdirectory import AnalysisDirectory
from pipeinspector.models import Base, ComputeWorkflowSample

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check analysis directory for completeness', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('database', metavar='<FILE>', help='sqlite database of samples')
    args = parser.parse_args()
    db_url = 'sqlite:///' + args.database
    db = create_engine(db_url)
    Base.metadata.create_all(db)
    Session = sessionmaker(bind=db)

    session = Session()
    for sample in session.query(ComputeWorkflowSample).filter(
            ComputeWorkflowSample.analysis_gvcf_path != None,
            ComputeWorkflowSample.analysis_cram_path != None):
        if (sample.analysis_cram_verifyed is None
                or not sample.analysis_cram_verifyed 
                or sample.analysis_gvcfs_verified is None 
                or not sample.analysis_gvcfs_verified):
            directory = AnalysisDirectory(sample.analysis_gvcf_path)
            is_complete = directory.is_complete
            sample.analysis_gvcfs_verified = is_complete
            sample.analysis_cram_verifyed = is_complete
            if not is_complete:
                # Print source_directory so we can attempt to process again
                sys.stderr.write('{0} should be examined and a new attempt made to pre-process the gvcfs etc\n'.format(sample.source_directory))
    session.commit()


