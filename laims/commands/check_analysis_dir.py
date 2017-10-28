import sys
import os.path

from logzero import logger

from laims.build38analysisdirectory import AnalysisDirectory, QcDirectory
from laims.models import Base, ComputeWorkflowSample

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def check_analysis_dir(app):
    db_url = 'sqlite:///' + app.database
    db = create_engine(db_url)
    Base.metadata.create_all(db)
    Session = sessionmaker(bind=db)

    session = Session()
    for sample in session.query(ComputeWorkflowSample).filter(
            ComputeWorkflowSample.analysis_gvcf_path is not None,
            ComputeWorkflowSample.analysis_cram_path is not None):
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
                logger.warn('{0} should be examined and a new attempt made to pre-process the gvcfs etc.'.format(sample.source_directory))
            else:
                qc_directory = QcDirectory(os.path.join(sample.analysis_gvcf_path, 'qc'))
                qc_synced = qc_directory.is_complete
                if not qc_synced:
                    logger.warn('{0} has a missing or incomplete qc directory. Attempt to resync.'.format(sample.source_directory))

    session.commit()
