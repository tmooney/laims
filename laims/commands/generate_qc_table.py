from __future__ import division

from collections import defaultdict
from crimson import picard, verifybamid, flagstat
from logzero import logger
import sys
import os

from laims.build38analysisdirectory import QcDirectory
from laims.models import ComputeWorkflowSample
from laims.database import open_db


class QcTable(object):

    def __init__(self):
        self.lines = list()
        self.header_set = set()
        self.header_order = list()
        self.exclusions = set(
                ('LIBRARY', 'SAMPLE', 'ACCUMULATION_LEVEL')
                )

    def add_to_metric_line(self, metric_line, key, value):
        if key in self.exclusions:
            return
        if key in metric_line:
            raise KeyError('{0} already in dictionary'.format(key))
        else:
            metric_line[key] = value
            if key not in self.header_set:
                self.header_order.append(key)
                self.header_set.add(key)

    def add_generic_picard_columns(self, line, metrics, key_prefix=None):
        for key in metrics['metrics']['contents']:
            table_key = key
            if key_prefix is not None:
                table_key = '_'.join([key_prefix, key])
            self.add_to_metric_line(line, table_key, metrics['metrics']['contents'][key])

    def add_picard_alignment_columns(self, line, alignment_metrics):
        for picard_line in alignment_metrics['metrics']['contents']:
            category = picard_line['CATEGORY']
            for key in picard_line:
                if key != 'CATEGORY':
                    new_key = '_'.join([category, key])
                    self.add_to_metric_line(line, new_key, picard_line[key])

    def add_picard_markdup_columns(self, line, markdup_metrics):
        # NOTE If there are more than one library then the contents
        # are a list of dictionaries. Otherwise it is simply a dict
        data = markdup_metrics['metrics']['contents']
        if isinstance(data, list):
            # Multiple libraries
            # We can sum up everything but PERCENT_DUPLICATION
            # I think it is ok to sum ESTIMATED_LIBRARY_SIZE between the two libraries
            totals = defaultdict(int)
            for lib in data:
                for key in lib:
                    if key not in ('LIBRARY', 'PERCENT_DUPLICATION'):
                        totals[key] += int(lib[key])
            totals['PERCENT_DUPLICATION'] = (totals['UNPAIRED_READ_DUPLICATES'] + totals['READ_PAIR_DUPLICATES']) / float(totals['UNPAIRED_READS_EXAMINED'] + totals['READ_PAIRS_EXAMINED'])
            totals['PERCENT_DUPLICATION'] = '{:.6f}'.format(totals['PERCENT_DUPLICATION'])
            data = totals
        for key in data:
            self.add_to_metric_line(line, key, data[key])

    def add_flagstat_columns(self, line, flagstat_metrics):
        for key in flagstat_metrics['pass_qc']:
            new_key = 'flagstat_' + key
            self.add_to_metric_line(line, new_key, flagstat_metrics['pass_qc'][key])

    def add_freemix_column(self, line, verifybamid_metrics):
        key = 'FREEMIX'
        self.add_to_metric_line(line, key, verifybamid_metrics[key])

    @staticmethod
    def haploid_coverage(metric_line):
        return '{0:.6g}'.format(metric_line['MEAN_COVERAGE'] * ((1 - metric_line['PCT_EXC_DUPE']) / (1 - metric_line['PCT_EXC_TOTAL'])))

    @staticmethod
    def interchromosomal_rate(metric_line):
        return '{0:.6g}'.format(metric_line['flagstat_diff_chrom'] / metric_line['flagstat_paired'])

    @staticmethod
    def discordant_rate(metric_line):
        # crimson doesn't parse percentages
        # recalculating them here
        mapped_percent = float('{0:.2f}'.format(metric_line['flagstat_mapped'] / metric_line['flagstat_total'] * 100))
        proper_pair_percent = float('{0:0.2f}'.format(metric_line['flagstat_paired_proper'] / metric_line['flagstat_paired_sequencing'] * 100))
        return mapped_percent - proper_pair_percent

    def add(self, sample_name, input_dir, internal_sample_name):
        metric_line = dict()

        self.add_to_metric_line(metric_line, 'SAMPLE_NAME', sample_name)
        self.add_to_metric_line(metric_line, 'INTERNAL_NAME', internal_sample_name)

        flagstat_metrics = flagstat.parse(input_dir.flagstat_file())
        self.add_flagstat_columns(metric_line, flagstat_metrics)

        alignment_metrics = picard.parse(input_dir.picard_alignment_metrics_file())
        self.add_picard_alignment_columns(metric_line, alignment_metrics)

        dup_metrics = picard.parse(input_dir.picard_mark_duplicates_metrics_file())
        self.add_picard_markdup_columns(metric_line, dup_metrics)

        ins_metrics = picard.parse(input_dir.picard_insert_size_metrics_file())
        self.add_generic_picard_columns(metric_line, ins_metrics, 'INS')

        wgs_metrics = picard.parse(input_dir.picard_wgs_metrics_file())
        self.add_generic_picard_columns(metric_line, wgs_metrics)

        gc_metrics = picard.parse(input_dir.picard_gc_bias_metrics_file())
        self.add_generic_picard_columns(metric_line, gc_metrics)

        verifybamid_metrics = verifybamid.parse(input_dir.verifybamid_self_sample_file())
        self.add_freemix_column(metric_line, verifybamid_metrics)

        self.add_to_metric_line(metric_line, 'HAPLOID_COVERAGE', self.haploid_coverage(metric_line))
        self.add_to_metric_line(metric_line, 'interchromosomal_rate', self.interchromosomal_rate(metric_line))
        self.add_to_metric_line(metric_line, 'discordant_rate', self.discordant_rate(metric_line))

        self.lines.append('\t'.join([ str(metric_line[key]) for key in self.header_order ]))

    def write(self, filehandle):
        filehandle.write('\t'.join(self.header_order))
        filehandle.write('\n')
        for line in self.lines:
            filehandle.write(line)
            filehandle.write('\n')


def generate(app, workorders):
    Session = open_db(app.database)
    table = QcTable()
    for wo in workorders:
        session = Session()
        for sample in session.query(ComputeWorkflowSample).filter(
                ComputeWorkflowSample.source_work_order == wo
                ):
            if (sample.analysis_cram_verifyed):
                qc_dir = QcDirectory(os.path.join(sample.analysis_gvcf_path, 'qc'))
                if qc_dir.is_complete:
                    logger.info('Adding qc for {0}'.format(sample.analysis_gvcf_path))
                    table.add(qc_dir.sample_name(), qc_dir, sample.ingest_sample_name)
    table.write(sys.stdout)
