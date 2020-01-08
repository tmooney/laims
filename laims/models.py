from sqlalchemy import Column, Text, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class ComputeWorkflowSample(Base):

    __tablename__ = 'csp_sample'
    __table_args__ = (
            UniqueConstraint(
                'source_work_order',
                'woi',
                'source_directory',
                name='uniq_row'),
            )

    id = Column(Integer, primary_key=True)
    source_work_order = Column(Integer)
    woi = Column(Integer)
    ingest_sample_name = Column(Text, unique=True, nullable=False)
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

    cohorts = relationship("SampleCohort", back_populates="sample")
    files = relationship("SampleFile", back_populates="sample")
    metrics = relationship("SampleMetric", back_populates="sample")

#-- ComputeWorkflowSample

class SampleCohort(Base):

    __tablename__ = 'sample_cohorts'

    sample_id = Column(Integer, ForeignKey("csp_sample.id"), primary_key=True)
    name = Column(Text, primary_key=True)

    sample = relationship("ComputeWorkflowSample", back_populates="cohorts")

#-- SampleCohort

class SampleFile(Base):

    __tablename__ = 'sample_files'
    __table_args__ = (
        UniqueConstraint(
            'sample_id',
            'name',
            name='uniq_file',
        ),
    )

    sample_id = Column(Integer, ForeignKey("csp_sample.id"), primary_key=True)
    name = Column(Text, primary_key=True)
    value = Column(Text)

    sample = relationship("ComputeWorkflowSample", back_populates="files")

#-- SampleFile

class SampleMetric(Base):

    __tablename__ = 'sample_metrics'
    __table_args__ = (
        UniqueConstraint(
            'sample_id',
            'name',
            name='uniq_metric',
        ),
    )

    sample_id = Column(Integer, ForeignKey("csp_sample.id"), primary_key=True)
    name = Column(Text, primary_key=True)
    value = Column(Text)

    sample = relationship("ComputeWorkflowSample", back_populates="metrics")

#-- SampleMetric
