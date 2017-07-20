import csv
import yaml
import os
import csv
import time
import glob
import argparse
import subprocess
parser = argparse.ArgumentParser()

parser.add_argument( "file", type=str )
parser.add_argument( "out", type=str )
parser.add_argument( "--ccdg", action='store_true' )
parser.add_argument( "--tm", action='store_true' )
parser.add_argument( "--dir", type=str)
#parser.add_argument( "dir", type=str, action='store_true')

args = parser.parse_args()

results = {}
header_line = []

date = time.strftime( "%m/%d/%Y" )
out_all = args.out + '.build38.all.tsv'

wd = os.getcwd()
cwd = os.getcwd()

input_fields = [
    'WorkOrder',
    'date_QC',
    'DNA',
    'instrument_data_count',
    'instrument_data_ids',
    'WorkingDirectory'
]
yaml_fields = [
    'SAMPLE_ALIAS',
    'ALIGNED_READS',
    'ALIGNMENT_RATE',
    'FIRST_OF_PAIR_MISMATCH_RATE',
    'SECOND_OF_PAIR_MISMATCH_RATE',
    'FREEMIX',
    'CHIPMIX',
    'HAPLOID_COVERAGE',
    'PCT_10X',
    'PCT_20X',
    'TOTAL_BASES_Q20_OR_MORE',
    'discordant_rate',
    'interchromosomal_rate',
    'HET_SNP_Q',
    'HET_SNP_SENSITIVITY',
    'MEAN_COVERAGE',
    'MEAN_INSERT_SIZE',
    'STANDARD_DEVIATION',
    'PCT_ADAPTER',
    'PF_READS',
    'PF_ALIGNED_BASES',
    'TOTAL_PERCENT_DUPLICATION',
    'TOTAL_READS',
    'reads_mapped_as_singleton_percentage',
    'reads_mapped_in_proper_pairs_percentage',
]

cram_header = [ 'cram', 'cram.md5' ]
pair_header = [ 'PF_HQ_ALIGNED_Q20_BASES', 'STATUS' ]
cromwell = ['Flagstats']
fail_header = [ 'QC Failed Metrics']

def get_yaml( path ):
    with open( path ) as data:
        yaml_values = yaml.load_all( data )
        fails = []
        fail_met = []
        for yamlv in yaml_values:

            if (args.dir):
                results[ 'PF_HQ_ALIGNED_Q20_BASES' ] = yamlv[ 'PF_HQ_ALIGNED_Q20_BASES' ]
            else:
                results[ 'PF_HQ_ALIGNED_Q20_BASES' ] = yamlv[ 'PAIR' ][ 'PF_HQ_ALIGNED_Q20_BASES' ]

            if( args.ccdg ):
                if ( yamlv[ 'FREEMIX' ] < 0.05 and yamlv[ 'HAPLOID_COVERAGE' ] >= 19.5 and yamlv[ 'discordant_rate' ] < 5
                     and yamlv[ 'interchromosomal_rate' ] < 0.05 and yamlv[ 'FIRST_OF_PAIR_MISMATCH_RATE' ] < 0.05
                     and yamlv[ 'SECOND_OF_PAIR_MISMATCH_RATE' ] < 0.05 ):
                    results[ 'STATUS' ] = 'pass'
                else:
                    results[ 'STATUS' ] = 'fail'
            
                if ( yamlv[ 'FREEMIX' ] > 0.05 ):
                        fail_met.append( 'FREEMIX' )
                
                if ( yamlv[ 'HAPLOID_COVERAGE' ] < 19.5 ):
                        fail_met.append( 'HAPLOID_COVERAGE' )

                if ( yamlv[ 'discordant_rate' ] > 5 ):
                        fail_met.append( 'discordant_rate' )

                if ( yamlv[ 'interchromosomal_rate' ] > 0.05 ):
                        fail_met.append( 'interchromosomal_rate' )

                if ( yamlv[ 'FIRST_OF_PAIR_MISMATCH_RATE' ] > 0.05 ):
                        fail_met.append( 'FIRST_OF_PAIR_MISMATCH_RATE' )

                if ( yamlv[ 'SECOND_OF_PAIR_MISMATCH_RATE' ] > 0.05 ):
                        fail_met.append( 'SECOND_OF_PAIR_MISMATCH_RATE' )  
          
                if ( len(fail_met) == 0 ):
                    fail_met.append( 'NA' )

            fails = ','.join(fail_met)
            results[ 'QC Failed Metrics' ] = fails

            if ( args.tm ):
                if ( yamlv[ 'FREEMIX' ] < 0.01 and yamlv[ 'HAPLOID_COVERAGE' ] >= 30
                    and yamlv[ 'TOTAL_BASES_Q20_OR_MORE' ] >= 86000000000
                    and yamlv[ 'PCT_10X' ] > 0.95 and yamlv[ 'PCT_20X' ] > 0.90 ):
                    results[ 'STATUS' ] = 'pass'
                else:
                    results[ 'STATUS' ] = 'fail'
            
                if ( yamlv[ 'FREEMIX' ] > 0.01):
                    fail_met.append( 'FREEMIX' )

                if ( yamlv[ 'HAPLOID_COVERAGE' ] < 30 ):
                    fail_met.append( 'HAPLOID_COVERAGE' )

                if ( yamlv[ 'TOTAL_BASES_Q20_OR_MORE' ] < 86000000000 ):
                    fail_met.append( 'TOTAL_BASES_Q20_OR_MORE' )

                if ( yamlv[ 'PCT_10X' ] < 0.95 ):
                    fail_met.append(  'PCT_10X' )

                if ( yamlv[ 'PCT_20X' ] < 0.90 ):
                    fail_met.append( 'PCT_20X' )

                if ( len(fail_met) == 0 ):
                    fail_met.append( 'NA' )

            fails = ','.join(fail_met)
            results[ 'QC Failed Metrics' ] = fails

            for k, v in yamlv.items():                
                for field in yaml_fields:
                    if ( k == field ):
                        results[k] = v
    return results


def get_read_groups( path ):
    file_name = '/verify_bam_id.selfRG'
    new_path =  path + file_name
    read_groups = set()
    with open( new_path ) as data:
        reader = csv.DictReader( data, delimiter="\t" )
        for line in reader:
            read_groups.add( line[ 'RG' ] )
    return read_groups

def get_cram ( path ):
    cram_path = path + '/*.cram'
    if glob.glob( cram_path ):
        for cram in glob.glob( cram_path ):
            results[ 'cram' ] = cram
    else:
        results[ 'cram' ] = 'NA'

    md5_path = path + '/*cram.md5'
    if glob.glob( md5_path ):
        for md5 in glob.glob( md5_path ):
            results[ 'cram.md5'] = md5
    else:
        results[ 'cram.md5' ] = 'NA'
            

with open( args.file ) as csvfile, open( out_all, 'w' ) as outfile: 

    reader = csv.DictReader( csvfile, delimiter="\t" )

    header_fields = input_fields + cram_header + yaml_fields + pair_header + cromwell +fail_header 
    w = csv.DictWriter( outfile, header_fields, delimiter="\t" )
    w.writeheader()

    fail_file = args.out + '.build38.yamlfail.tsv'
    fail = open(fail_file, 'w')
    fail_print = False

    pass_file = args.out + '.build38.qcpass.tsv'
    passfh = open(pass_file, 'w')
    wr = csv.DictWriter( passfh, header_fields, delimiter="\t" )
    wr.writeheader()

    out_fail = args.out + '.build38.fail.tsv'
    failfh = open(out_fail, 'w')
    fr = csv.DictWriter( failfh, header_fields, delimiter="\t" )
    fr.writeheader()

    samplemap = args.out + '.qcpass.samplemap.tsv'
    sm = open(samplemap, 'w')

    for line in reader:

        line = {k.replace(' ', ''): v for k, v in line.items() if k is not None}

        results[ 'WorkOrder' ] = line[ 'WorkOrder' ]
        results[ 'date_QC' ] = date
        results[ 'DNA' ] = line[ 'DNA' ]
        results[ 'WorkingDirectory' ] = line[ 'WorkingDirectory' ]

        flag = subprocess.run(["python", "/gscuser/awollam/aw/check_flagstats_in_cromwell.py", "/gscmnt/gc13035/production/compute_157903910"], stdout=subprocess.PIPE)
        flagout = flag.stdout.decode()
        foug = flagout.split()
        results['Flagstats'] = foug[1]
        

        if (args.dir):
            file_name = os.path.basename(os.path.normpath(line['WorkingDirectory']))
            file_name = file_name + '.qc_metrics.yaml'
            qc_dir_file = args.dir + file_name
            
        else:

            file_name = '/qc_metrics.yaml'
            qc_dir_file =  line[ 'WorkingDirectory' ] + file_name
        
        if  os.path.exists( qc_dir_file )==True:

            yaml_dict = get_yaml( qc_dir_file )
            read_groups = get_read_groups( line['WorkingDirectory'] )
            get_cram( line[ 'WorkingDirectory' ] )
         
            css = ','.join( sorted( read_groups ) ) # comma-separated string
            count = len( read_groups )

            # Make a new dict using above data, plus fields from line
            results[ 'instrument_data_ids' ] = css
            results[ 'instrument_data_count' ] = count
            # Use csv.DictWriter to write the new dict to outfile.

            w.writerow( results )

            if results[ 'STATUS' ] == 'pass':
                sm.write( results[ 'DNA' ] + "\t" + results[ 'cram' ] + "\t" + results[ 'cram.md5' ] + "\n" )
                wr.writerow( results )

            if results[ 'STATUS' ] == 'fail':
                fr.writerow( results )
                

        else:
            fail_print = True
            nofile = 'NA'
            print( results[ 'WorkOrder' ] + "\t" + results[ 'date_QC' ] + "\t" + results[ 'DNA' ]
                  + "\t" + results[ 'WorkingDirectory' ] + "\t" + nofile )
            fail.write( results[ 'WorkOrder' ] + "\t" + results[ 'date_QC' ] + "\t" + results[ 'DNA' ]
                          + "\t" + results[ 'WorkingDirectory' ] + "\t" + nofile + "\n" )
        

if ( fail_print == True ):
    print( 'Samples without yaml files output to: ' + fail_file )
else:
    print( 'All yaml files exist' )

exit()
