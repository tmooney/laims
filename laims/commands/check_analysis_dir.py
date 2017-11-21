import os.path

from logzero import logger

from laims.build38analysisdirectory import AnalysisDirectory, QcDirectory
from laims.models import ComputeWorkflowSample
from laims.database import open_db


def check_analysis_dir(app):
    Session = open_db(app.database)
    session = Session()
    for sample in session.query(ComputeWorkflowSample):
        if (sample.analysis_gvcf_path is None or sample.analysis_gvcf_path is None):
            logger.warn('No analysis directory in database for {0}. Is the source directory invalid?'.format(sample.source_directory))
            continue
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
                else:
                    logger.info('{0} complete.'.format(sample.source_directory))

    session.commit()
