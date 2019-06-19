from .context import laims

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from laims.models import Base, ComputeWorkflowSample
 
engine = create_engine('sqlite:///tests/test_app/test.db')
Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
sample = ComputeWorkflowSample(
   id= "1",
   source_work_order= "2854371",
   woi= " 1541201",
   ingest_sample_name= "H_XS-356091-0186761975",
   source_directory= "/gscmnt/gc13035/production/2853358/compute_159065627",
   valid_source_directory= None,
   passed_qc= None,
   analysis_cram_path= "/gscmnt/gc2758/analysis/ccdg/data/H_XS-356091-0186761975",
   analysis_cram_verifyed= None,
   analysis_gvcf_path= "/gscmnt/gc2758/analysis/ccdg/data/H_XS-356091-0186761975",
   analysis_gvcfs_verified= None,
   analysis_sv_path= "/gscmnt/gc2758/analysis/ccdg/data/H_XS-356091-0186761975/sv",
   analysis_sv_verified= None,
   #ingest_date= "2017-07-19 03:43:15.208094",
)
session.add(sample)
session.commit()
