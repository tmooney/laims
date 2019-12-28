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

    metrics = relationship("SampleMetric", back_populates="sample")

#-- ComputeWorkflowSample

class SampleMetric(Base):

    __tablename__ = 'sample_metrics'
    __table_args__ = (
        UniqueConstraint(
            'sample_id',
            'name',
            name='uniq_metric',
        ),
    )

    id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey("csp_sample.id"))
    name = Column(Text)
    value = Column(Text)

    sample = relationship("ComputeWorkflowSample", back_populates="metrics")

#-- SampleMetric

