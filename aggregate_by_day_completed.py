#!/usr/bin/env python

import csv
import sys
import datetime

if __name__ == '__main__':
    reader = csv.DictReader(sys.stdin, delimiter='\t')
    for row in reader:
        completed = datetime.datetime.strptime(row['date_completed'], '%Y-%m-%d %H:%M:%S')
        started = datetime.datetime.strptime(row['date_scheduled'], '%Y-%m-%d %H:%M:%S')
        duration = completed - started
        print '\t'.join(map(str, [completed.date().isoformat(), (duration.seconds / 60) + (duration.days * 24 * 60)]))

        

