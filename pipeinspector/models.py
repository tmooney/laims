from sqlalchemy import Column, Text, Integer, Boolean, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
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
    source_work_order = Column(Integer, index=True)
    woi = Column(Integer, index=True)
    ingest_sample_name = Column(Text, unique=True, nullable=False, index=True)
    source_directory = Column(Text, unique=True, nullable=False, index=True)
    valid_source_directory = Column(Boolean)
    passed_qc = Column(Boolean)
    analysis_cram_path = Column(Text)
    analysis_cram_verifyed = Column(Boolean)
    analysis_gvcf_path = Column(Text)
    analysis_gvcfs_verified = Column(Boolean)
    analysis_sv_path = Column(Text)
    analysis_sv_verified = Column(Boolean)
    ingest_date = Column(DateTime, default=datetime.datetime.utcnow)
    sample_info = relationship('SampleInfo')


class Callset(Base):

    __tablename__ = 'callset'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=False)
    jira_issue = Column(Text, nullable=False)
    freeze_date = Column(DateTime, default=datetime.datetime.utcnow)
    samples = relationship('SampleInfo')


class SampleInfo(Base):

    __tablename__ = 'sample_info'
    callset_id = Column(Integer, ForeignKey('callset.id'), primary_key=True)
    csp_sample_id = Column(Integer, ForeignKey('csp_sample.woi'), primary_key=True)
    admin_project_id = Column(Integer, index=True)
    admin_project_name = Column(Text, nullable=True, index=True)
    nomenclature = Column(Text, nullable=True)
    read_group_sample_name = Column(Text, nullable=True)
    common_name = Column(Text, nullable=True)
    organism_individual_id = Column(Integer, nullable=False)
    organism_individual_name = Column(Text, nullable=False)
    organism_individual_full_name = Column(Text, nullable=False)
    organism_sample_id = Column(Integer, nullable=False)
    organism_sample_name = Column(Text, nullable=False)
    organism_sample_full_name = Column(Text, nullable=False)
    race = Column(Text, nullable=True)
    ethnicity = Column(Text, nullable=True)
    gender = Column(Text, nullable=True)
    case_control_value = Column(Text, nullable=True)
    recorded_age = Column(Text, nullable=True)
    processing_data = relationship('ComputeWorkflowSample')
    callset = relationship('Callset')

