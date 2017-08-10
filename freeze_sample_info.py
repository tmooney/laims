#!/usr/bin/env python

from pipeinspector.models import Base, ComputeWorkflowSample, Callset, SampleInfo
from lims import LIMS

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import argparse


def setup_db(file_):
    db = create_engine('sqlite:///' + file_)
    Base.metadata.create_all(db)
    return sessionmaker(bind=db)


def sample_info_adaptor(row):
    return {
            'callset': new_callset,
            'csp_sample_id': row['woi_id'],
            'admin_project_id': row['admin_project_id'],
            'admin_project_name': row['admin_project_name'],
            'nomenclature': row['nomenclature'],
            'read_group_sample_name': row['read_group_sample_name'],
            'common_name': row['common_name'],
            'organism_individual_id': row['organism_individual_id'],
            'organism_individual_name': row['organism_individual_name'],
            'organism_individual_full_name': row['organism_individual_full_name'],
            'organism_sample_id': row['organism_sample_id'],
            'organism_sample_name': row['organism_sample_name'],
            'organism_sample_full_name': row['organism_sample_full_name'],
            'race': row['race'],
            'ethnicity': row['ethnicity'],
            'gender': row['gender'],
            'case_control_value': row['case_control_value'],
            'recorded_age': row['recorded_age'],
            }


if __name__ == '__main__':
    Session = setup_db('test.db')
    session = Session()
    new_callset = Callset(
                    name='TestCallset',
                    description='This is only a test',
                    jira_issue='BIO-0000',
                  )
    session.add(
            new_callset
            )
    session.flush()
    woi = set()
    work_orders= set()

    for x in session.query(ComputeWorkflowSample).all():
        woi.add(x.woi)
        work_orders.add(x.source_work_order)

    l = LIMS()
    for wo in work_orders:
        for row in l.sample_informations(wo):
            if row['woi_id'] in woi:
                # insert into Table
                sample_info = SampleInfo(**sample_info_adaptor(row))
                session.add(sample_info)
    session.commit()


