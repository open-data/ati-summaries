#!/usr/bin/env python

import json
from read_fix_csv import unicode_csv_reader

"""
convert from an exported list of orgs to a jsonl file that may be
imported by ckanext-scheming as organizations
"""

SOURCE_ORGS = 'data/orgs-utf8.csv'
OUTPUT_JSONL = 'data/orgs.jsonl'

def main():
    orgs = unicode_csv_reader(SOURCE_ORGS)
    out = open(OUTPUT_JSONL, 'w')
    for o in orgs:
        if o[0] == 'English':
            break

    print next(orgs)


main()
