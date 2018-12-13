# Copying Over Data From Production

Say we are looking at data from SCCS cohort/study.  So we go to:

    /gscmnt/gc2802/halllab/dlarson/jira/BIO-2169_Build38_Realign/SCCS/

Given the work order via the QC email, we go to [IMP][1]. And then on that page "export to CSV", and copy the following file:

     2857106.ComputeWorkflowExecution.csv

into the above mentioned project directory.

We filter on that file for the `Aligned Bam to BQSR Cram and VCF Without Genotype` and `completed` elements via.

     cat {} | tr '\,' '\t' | sed 's/\"//g' | cut -f 8,9 

This results in the following file:

     2857106.ComputeWorkflowExecution.completed.csv
 
Then we get the QC pasing information from an email by Aye, Heather and/or Lee. And that file is: 

    2857106.218.120718.qcpass.samplemap.tsv

Then we identify the samples (the first column) that are good, and re-filter the `2857106.ComputeWorkflowExecution.completed.csv` file on those good sample to result in the final file that is supplied to the `laims ingest` command:
 
    2857106.ComputeWorkflowExecution.qcpass.csv 

## Running the `laims ingest` command

    # inside the genome perl docker image
    cd /tmp
    git clone https://github.com/ernfrid/laims
    cd laims
    export PATH=/gscmnt/gc2802/halllab/idas/software/local/bin:$PATH
    pip install -e .
    laims ingest \
       --job-group <job-group> \  # limit to 200 (400 on weekends)
       --output-dir /gscmnt/gc2758/analysis/ccdg/data/path \
       /path/to/2857106.ComputeWorkflowExecution.qcpass.csv 

### What `laims ingest` is doing

1. Copies the CRAM, GVCFs, and QCs into the relevant `--output-dir` hall-lab directory.
2. A sqlite3 database is updated and is located here:
    
        /gscmnt/gc2802/halllab/ccdg_resources/tracking/tracking.db
  
  An example output directory will have the following template:

```
$ tree /gscmnt/gc2758/analysis/ccdg/data/<sample-name>/
/gscmnt/gc2758/analysis/ccdg/data/<sample-name>/
├── <sample-name>.chr1.g.vcf.gz
├── <sample-name>.chr1.g.vcf.gz.tbi
├── <sample-name>.cram
├── <sample-name>.cram.crai
├── <sample-name>.extChr.g.vcf.gz
├── <sample-name>.extChr.g.vcf.gz.tbi
├── ...
├── qc
│   ├── GC_bias.txt
│   ├── GC_bias_chart.pdf
│   ├── GC_bias_summary.txt
│   ├── X_chrom.variant_calling_detail_metrics
│   ├── X_chrom.variant_calling_summary_metrics
│   ├── alignment_summary.txt
│   ├── all_chrom.variant_calling_detail_metrics
│   ├── all_chrom.variant_calling_summary_metrics
│   ├── bamutil_stats.txt
│   ├── flagstat.out
│   ├── insert_size.pdf
│   ├── insert_size_summary.txt
│   ├── mark_dups_metrics.txt
│   ├── verify_bam_id.depthRG
│   ├── verify_bam_id.depthSM
│   ├── verify_bam_id.selfRG
│   ├── verify_bam_id.selfSM
│   └── wgs_metric_summary.txt
└── sv
    ├── <sample-name>.cn.bed
    ├── <sample-name>.cn.txt
    ├── <sample-name>.cnvnator.out
    │   ├── <sample-name>.cram.hist.root
    │   └── <sample-name>.cram.root
    ├── <sample-name>.cram -> /gscmnt/gc2758/analysis/ccdg/data/<sample-name>/<sample-name>.cram
    ├── <sample-name>.cram.crai -> /gscmnt/gc2758/analysis/ccdg/data/<sample-name>/<sample-name>.cram.crai
    ├── <sample-name>.cram.json
    ├── <sample-name>.discordants.bam
    ├── <sample-name>.discordants.bam.bai
    ├── <sample-name>.gt.vcf
    ├── <sample-name>.log
    ├── <sample-name>.splitters.bam
    ├── <sample-name>.splitters.bam.bai
    ├── <sample-name>.vcf
    ├── cnvnator.<sample-name>.log
    ├── genotype.<sample-name>.log
    └── lumpy.<sample-name>.log

3 directories, 87 files
```

The `sv` subdirectory is the result from running `laims call-sv`

# Copying Over Data to the Cloud

We upload in terms of work order sets, as they are smaller and easier to handle.

## Get the sample list to copy

    DBPATH=/gscmnt/gc2802/halllab/ccdg_resources/tracking/tracking.db
    sqlite3 ${DBPATH}
    sqlite3> .output /path/to/all_samples.tracking.txt
    sqlite3> select * from csp_sample;

Afterwards, we filter out the sample-name and gvcfs-paths that we'd like to copy over and place them into a directory like so:
    
    /gscmnt/gc2802/halllab/dlarson/jira/BIO-2169_Build38_Realign/cohort/upload_gvcf_batch6/<work-order>.tsv

We use the `prepare_batch.pl` script :

    cat /gscmnt/gc2802/halllab/dlarson/jira/BIO-2169_Build38_Realign/cohort/upload_gvcf_batch6/<work-order>.tsv | perl prepare_batch.pl
    
to 

1.  create the `for_upload` directory inside the `upload_gvcf_batch6` directory.
2.  create appropriate symlinks inside the `for_upload` directory

Once the `for_upload` directory is setup, we can then run the `gsutil` command like so:

   gsutil -m rsync -r ${PWD}/for_upload gs://bucket-name

The `prepare_batch.pl` script looks like:

```perl
#!/usr/bin/perl

use File::Spec;
use File::Path qw( make_path );

# expect lines from compute output

my $root_dir = "/gscmnt/gc2802/halllab/dlarson/jira/BIO-2169_Build38_Realign/Finrisk/upload_gvcf_batch6/for_upload3/";
my $cohort = "FINRISK";

while(<>) {
    chomp;
    my @fields = split "\t", $_;
    next if $fields[0] =~ /Sample/;
    my ($sample, $output_directory) = @fields[0,1];
    my $containing_dir = File::Spec->catfile($root_dir, $cohort, $sample, '');
    my @output_files = glob(File::Spec->catfile($output_directory, $sample) . "*g.vcf.gz*");
    make_path($containing_dir) or die "Unable to create directory $containing_dir\n";
    for my $file (@output_files) {
        `ln -s $file $containing_dir`;
        if ($?) {
            die "Unable to symlink $file to $containing_dir\n";
        }
    }
}
```

# Re-banding

The GVCFs produced in the LIMS production pipeline (for older pipelines) the `GQ` attribute inside the `FORMAT` field was originally banded to 3 levels (5, 20, and 60).  [See step 10 in the "Sequence Analysis Steps" in confluence](https://confluence.ris.wustl.edu/pages/viewpage.action?pageId=26968484).  We need this to be changed to this [(See step 10 in the new pipeline on confluence)](https://confluence.ris.wustl.edu/display/BIO/Proposed+CCDG+Analysis+Workflow+-+2017.7.14#?lucidIFH-viewer-89b394c=1).

The following `laims` command will re-band old GVCFs into new GVCFs with the newer banding strategy:

    laims reband <blah> <blah>  # something work order based

[1]:  https://imp-lims.gsc.wustl.edu/entity/setup-work-order/2857106?Perspective=Compute_Workflow_Execution
