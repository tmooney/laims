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


[1]:  https://imp-lims.gsc.wustl.edu/entity/setup-work-order/2857106?Perspective=Compute_Workflow_Execution
