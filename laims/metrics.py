import csv, glob, os

class QcMetrics(object):

    def __init__(self, dn):
        """
        Expectations is a dictionary where the key is a glob
        pattern and the value is the number of files expected to be returned
        """
        self.dn = dn

    #-- __init__

    @staticmethod
    def verifyBamID_bn():
        return "verify_bam_id.selfSM"

    def verifyBamID_GT_bn():
        return "GT_verify_bam_id.selfSM"

    def verifyBamID_fn(self):
        bn = QcMetrics.verifyBamID_bn()
        files = glob.glob( os.path.join(self.dn, bn) )
        if len(files) == 1: return files[0]
        bn_gt = QcMetrics.verifyBamID_GT_bn()
        files = glob.glob( os.path.join(self.dn, bn_gt) )
        if len(files) == 1: return files[0]
        raise FileNotFoundError("Failed to find verify bam id file ({} or {}) in {}".format(bn, bn_gt, self.dn))

    def verifyBamID_metrics(self):
        fn = self.verifyBamID_fn()
        with open(fn, "r") as f:
            rdr = csv.DictReader(f, delimiter="\t")
            metrics = next(rdr)
        if metrics is None:
            raise Exception("Failed to find Verify BamID metrics in {}".format(fn))
        return metrics

    #-- verifyBamID

    @staticmethod
    def picard_wgs_bn():
        return "wgs_metric_summary.txt"

    def picard_wgs_fn(self):
        bn = QcMetrics.picard_wgs_bn()
        files = glob.glob( os.path.join(self.dn, bn) )
        if len(files) == 1: return files[0]
        raise FileNotFoundError("Failed to find picard wgs ({}) in {}".format(bn, self.dn))

    def picard_wgs_metrics(self):
        fn = self.picard_wgs_fn()
        with open(fn, "r") as f:
            for l in f:
                if l.rstrip() == "## METRICS CLASS\tpicard.analysis.CollectWgsMetrics$WgsMetrics":
                    break
            rdr = csv.DictReader(f, delimiter="\t")
            metrics = next(rdr)
        if metrics is None:
            raise Exception("Failed to find Picard WGS metrics in {}".format(fn))
        return metrics

    #-- picard wgs

#-- QcMetrics
