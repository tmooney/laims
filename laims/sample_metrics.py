import click, os, sys, yaml
from sqlalchemy.orm.exc import NoResultFound

from laims.app import LaimsApp
from laims.models import ComputeWorkflowSample, SampleMetric
from laims.metrics import QcMetrics

# METRICS
# add

@click.group()
def laims_metrics_cli():
    """
    Commands and Helpers for Sample metrics
    """
    pass

# [add]
@click.command(help="add sample metrics into db")
def metrics_add_cmd():
    """
    Add Sample Metrics Into DB

    Currently adds these metrics from ALL samples:
    * picard wgs
     -  mean coverage
    * verify bam id
     - freemix
    """
    db = LaimsApp().db_connection()
    session = db()
    status = {"OK": 0, "NO_DIR": 0, "NO_VERIFY_BAMID": 0, "NO_PICARD_WGS": 0}
    for sample in session.query(ComputeWorkflowSample):
        dn = sample.analysis_cram_path
        qc_dn = os.path.join(dn, "qc")
        if not os.path.exists(dn) or not os.path.exists(qc_dn):
            status["NO_DIR"] += 1
            continue

        # verifyBamID
        qc = QcMetrics(dn=qc_dn)
        try:
            verifyBamID_metrics = qc.verifyBamID_metrics()
        except:
            status["NO_VERIFY_BAMID"] += 1
            continue
        _add_or_update_metrics(session=session, sample=sample, metrics=verifyBamID_metrics, names=["FREEMIX"])

        # picard wgs
        try:
            picard_wgs_metrics = qc.picard_wgs_metrics()
        except:
            status["NO_PICARD_WGS"] += 1
            continue
        _add_or_update_metrics(session=session, sample=sample, metrics=picard_wgs_metrics, names=["MEAN_COVERAGE"])
        status["OK"] += 1
    sys.stderr.write("STATUS:\n"+yaml.dump(status, indent=6))
laims_metrics_cli.add_command(metrics_add_cmd, name="add")

def _add_or_update_metrics(session, sample, metrics, names):
    for name in names:
        name_l = name.lower()
        metric = session.query(SampleMetric).get((sample.id, name_l))
        if metric is None:
            metric = SampleMetric(sample_id=sample.id, name=name_l, value=metrics[name])
        elif metrics[name] != metric.value:
            setattr(metric, name_l, metrics[name])
        session.add(metric)
    session.commit()

#-- _add_or_update_metrics
