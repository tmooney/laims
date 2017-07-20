import csv
import sys
import subprocess
import argparse
parser = argparse.ArgumentParser()

parser.add_argument( "infile", type=str )
parser.add_argument( "outfile", type=str )
parser.add_argument( "--ccdg", action='store_true' )
parser.add_argument( "--tm", action='store_true' )
parser.add_argument( "--sample", type=int)
args = parser.parse_args()

orig_stdout = sys.stdout

ALIGNMENT_RATE, FREEMIX, HAPLOID_COVERAGE, discordant_rate, interchromosomal_rate = ([] for i in range(5))
alignment_rate_fail, freemix_fail, haploid_coverage_fail , discordant_rate_fail, interchromosomal_rate_fail = ( [] for i in range(5))

FIRST_OF_PAIR_MISMATCH_RATE, SECOND_OF_PAIR_MISMATCH_RATE, TOTAL_PERCENT_DUPLICATION, TOTAL_BASES_Q20_OR_MORE = ([] for i in range(4))
FIRST_OF_PAIR_MISMATCH_RATE_fail, SECOND_OF_PAIR_MISMATCH_RATE_fail, TOTAL_PERCENT_DUPLICATION_fail, TOTAL_BASES_Q20_OR_MORE_fail = ([] for i in range(4))

PCT_10X, PCT_20X, sample_pass, sample_fail = ([] for i in range(4))
PCT_10X_fail, PCT_20X_fail, DNA = ( [] for i in range(3))

with open(args.infile) as csvfile:

    reader = csv.DictReader(csvfile, delimiter="\t")
    for line in reader:
        ALIGNMENT_RATE.append(round(float(line['ALIGNMENT_RATE']), 5))
        FREEMIX.append(round(float(line['FREEMIX']), 5))
        HAPLOID_COVERAGE.append(round(float(line['HAPLOID_COVERAGE']), 5))
        discordant_rate.append(round(float(line['discordant_rate']), 5))
        interchromosomal_rate.append(round(float(line['interchromosomal_rate']), 5))
        FIRST_OF_PAIR_MISMATCH_RATE.append(round(float(line['FIRST_OF_PAIR_MISMATCH_RATE']), 5))
        SECOND_OF_PAIR_MISMATCH_RATE.append(round(float(line['SECOND_OF_PAIR_MISMATCH_RATE']), 5))
        TOTAL_BASES_Q20_OR_MORE.append(round(float(line['TOTAL_BASES_Q20_OR_MORE']), 5))
        TOTAL_PERCENT_DUPLICATION.append(round(float(line['TOTAL_PERCENT_DUPLICATION']), 5))
        PCT_10X.append(float(line['PCT_10X']))
        PCT_20X.append(float(line['PCT_20X']))
        DNA.append(line['DNA'])

        if (line['STATUS'] == 'pass'):
            sample_pass.append(line['STATUS'])

        if (line['STATUS'] == 'fail'):
            sample_fail.append(line['STATUS'])
            fail = line['QC Failed Metrics'].split(sep=',')
            for reason in fail:
                if (reason == 'ALIGNMENT_RATE' ):
                    alignment_rate_fail.append(reason)
                if (reason == 'FREEMIX'):
                    freemix_fail.append(reason)
                if (reason == 'HAPLOID_COVERAGE'):
                    haploid_coverage_fail.append(reason)
                if (reason == 'discordant_rate'):
                    discordant_rate_fail.append(reason)
                if (reason == 'interchromosomal_rate'):
                    interchromosomal_rate_fail.append(reason)
                if (reason == 'FIRST_OF_PAIR_MISMATCH_RATE'):
                    FIRST_OF_PAIR_MISMATCH_RATE_fail.append(reason)
                if (reason == 'SECOND_OF_PAIR_MISMATCH_RATE'):
                    SECOND_OF_PAIR_MISMATCH_RATE_fail.append(reason)
                if (reason == 'TOTAL_BASES_Q20_OR_MORE'):
                    TOTAL_BASES_Q20_OR_MORE_fail.append(reason)
                if (reason == 'TOTAL_PERCENT_DUPLICATION'):
                    TOTAL_PERCENT_DUPLICATION_fail.append(reason)
                if (reason == 'PCT_10X'):
                    PCT_10X_fail.append(reason)
                if (reason == 'PCT_20X'):
                    PCT_20X_fail.append(reason)

total_qc_samples = len(DNA)
total_pass_samples = len(sample_pass)
total_fail_samples = len(sample_fail)

if (args.ccdg and args.tm):
    print('Unable to run with ccdg and tm')
    exit()

f = open(args.outfile, 'w')
sys.stdout = f

print('Hi,'+"\n\n"+'QC is complete for this work order.')

if (args.ccdg):
    print("\n"+'QC Review Metrics: STANDARD'+"\n"+'CCDG metrics, QC Pass criteria are as below:'+"\n")

    print(
        'FREEMIX < 0.05',
        'HAPLOID_COVERAGE = or > 19.5',
        'discordant_rate < 0.05',
        'interchromosomal_rate < 0.05',
        'FIRST_OF_PAIR_MISMATCH_RATE < 0.05',
        'SECOND_OF_PAIR_MISMATCH_RATE < 0.05',
         sep="\n"
    )

if (args.tm):
    print("\n" + 'QC Review Metrics: STANDARD' + "\n" + 'TopMed metrics, QC Pass criteria are as below:' + "\n")

    print(
        'FREEMIX < 0.01',
        'HAPLOID_COVERAGE = or > 30',
        'TOTAL_BASES_Q20_OR_MORE = or more 86,000,000,000',
        'PCT_10X > 0.95',
        'PCT_20X > 0.90',
        sep="\n"
    )


print("\n"+'Report Summary:'+"\n"+'Library Type: NA')
if (args.sample):
    print('Total Samples Sequenced: ', args.sample)
print('Total Samples QC\'ed: ', total_qc_samples)
print('Samples That Meet QC Criteria =', total_pass_samples)
print('Samples that Fail QC Criteria =', total_fail_samples, "\n")

print('Failed Samples:')

if (len(alignment_rate_fail) > 0):
    print('ALIGNMENT_RATE: ', len(alignment_rate_fail) )
if (len(freemix_fail) > 0):
    print('FREEMIX: ', len(freemix_fail) )
if (len(haploid_coverage_fail) > 0):
    print('HAPLOID_COVERAGE: ', len(haploid_coverage_fail) )
if (len(discordant_rate_fail) > 0):
    print('DISCORDANT_RATE: ', len(discordant_rate_fail) )
if (len(interchromosomal_rate_fail) > 0):
    print('INTERCHROMOSOMAL_RATE: ', len(interchromosomal_rate_fail) )
if (len(FIRST_OF_PAIR_MISMATCH_RATE_fail) > 0):
    print('FIRST_OF_PAIR_MISMATCH_RATE: ', len(FIRST_OF_PAIR_MISMATCH_RATE_fail) )
if (len(SECOND_OF_PAIR_MISMATCH_RATE_fail) > 0):
    print('SECOND_OF_PAIR_MISMATCH_RATE: ', len(SECOND_OF_PAIR_MISMATCH_RATE_fail) )
if (len(TOTAL_BASES_Q20_OR_MORE_fail) > 0):
    print('TOTAL_BASES_Q20_OR_MORE: ', len(TOTAL_BASES_Q20_OR_MORE_fail) )
if (len(TOTAL_PERCENT_DUPLICATION_fail) > 0):
    print('TOTAL_PERCENT_DUPLICATION: ', len(TOTAL_PERCENT_DUPLICATION_fail) )
if (len(PCT_10X_fail) > 0):
    print('PCT_10X: ', len(PCT_10X_fail) )
if (len(PCT_20X_fail) > 0):
    print('PCT_20X: ', len(PCT_20X_fail) )
else:
    print('NA')

print()
print('Summary Statistics:', "\n")


print('ALIGNMENT_RATE - Average: ', round((sum(ALIGNMENT_RATE)/len(ALIGNMENT_RATE)), 5),
      '(', min(ALIGNMENT_RATE), '-', max(ALIGNMENT_RATE), ')')

print('FREEMIX - Average: ', round((sum(FREEMIX)/len(FREEMIX)), 5), '(', min(FREEMIX), '-', max(FREEMIX), ')')

print('HAPLOID_COVERAGE - Average: ', round((sum(HAPLOID_COVERAGE)/len(HAPLOID_COVERAGE)), 5),
      '(', min(HAPLOID_COVERAGE), '-', max(HAPLOID_COVERAGE), ')')

print('discordant_rate - Average: ', round((sum(discordant_rate)/len(discordant_rate)), 5), '(', min(discordant_rate), '-', max(discordant_rate), ')')

print('interchromosomal_rate - Average: ', round((sum(interchromosomal_rate)/len(interchromosomal_rate)), 5),
  '(', min(interchromosomal_rate), '-', max(interchromosomal_rate), ')')

print('FIRST_OF_PAIR_MISMATCH_RATE - Average: ', round((sum(FIRST_OF_PAIR_MISMATCH_RATE)/len(FIRST_OF_PAIR_MISMATCH_RATE)), 5),
  '(', min(FIRST_OF_PAIR_MISMATCH_RATE), '-', max(FIRST_OF_PAIR_MISMATCH_RATE), ')')

print('SECOND_OF_PAIR_MISMATCH_RATE - Average: ', round((sum(SECOND_OF_PAIR_MISMATCH_RATE)/len(SECOND_OF_PAIR_MISMATCH_RATE)), 5),
  '(', min(SECOND_OF_PAIR_MISMATCH_RATE), '-', max(SECOND_OF_PAIR_MISMATCH_RATE), ')')

print('TOTAL_PERCENT_DUPLICATION - Average: ', round((sum(TOTAL_PERCENT_DUPLICATION)/len(TOTAL_PERCENT_DUPLICATION)), 5),
      '(', min(TOTAL_PERCENT_DUPLICATION), '-', max(TOTAL_PERCENT_DUPLICATION), ')')

print('TOTAL_BASES_Q20_OR_MORE - Average: ', round((sum(TOTAL_BASES_Q20_OR_MORE)/len(TOTAL_BASES_Q20_OR_MORE)), 5),
      '(', min(TOTAL_BASES_Q20_OR_MORE), '-', max(TOTAL_BASES_Q20_OR_MORE), ')')

print('PCT_10X - Average: ', round((sum(PCT_10X)/len(PCT_10X)), 5), '(', min(PCT_10X), '-', max(PCT_10X), ')')

print('PCT_20X - Average: ', round((sum(PCT_20X)/len(PCT_20X)), 5), '(', min(PCT_20X), '-', max(PCT_20X), ')')

print()
print('Attachments: ')
print(args.infile, 'contains all the stats for samples that have been QCed')
print('qcpass.samplemap.tsv contains the file paths to QC passed samples')
print('build38.fail.tsv contains the stats for failed samples')
print('NOTES: NA')

sys.stdout = orig_stdout
f.close()
subprocess.run(["cat", args.outfile])
exit()
