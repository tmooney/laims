#!/usr/bin/perl

use warnings;
use strict;

use List::Util qw( max );
use Cwd;

my %expectations = (
    "*.cram" => 1,
    "*.crai" => 1,
    "*.chr*.g.vcf.gz" => 24,
    "*.chr*.g.vcf.gz.tbi" => 24,
    "*.extChr.g.vcf.gz" => 1,
    "*.extChr.g.vcf.gz.tbi" => 1,
    "X_chrom*" => 2,
    "all_chrom*" => 2,
    "bamutil_stats.txt" => 1,
    "flagstat.out" => 1,
    "insert_size*" => 2,
    "mark_dups_metrics.txt" => 1,
    "verify_bam_id*" => 4,
    "wgs_metric_summary.txt" => 1,
    "GC_bias*" => 3,
);

for my $dir (@ARGV) {
    chomp $dir;
    if (-d $dir ) {
        chdir $dir;
        my $done = completed();
        if (defined $done) {
            print "$dir\tdone\t$done", "\n";
        }
        else {
            print "$dir\tincomplete\t", "\n";
        }
    }
}

sub expected {
    my ($glob, $num) = @_;
    my @files = glob($glob);
    return scalar(@files) == $num;
}

sub most_recent_timestamp {
    my (@files) = @_;
    return max(map { my @stats = stat($_); $stats[9] } @files);
}
    

sub completed {
    my $done = 0;
    for my $key (keys %expectations) {
        unless(expected($key, $expectations{$key})) {
            warn "Unexpected number of files for glob: $key\n";
            return undef;
        }
        my $mrt = most_recent_timestamp(glob($key));
        if ($mrt > $done) {
            $done = $mrt;
        }
    }
    return $done;
}

