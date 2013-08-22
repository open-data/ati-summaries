#!/usr/bin/python

import csv

ENG_SOURCE = 'data/ati_en.csv'
FRA_SOURCE = 'data/ati_fr.csv'


def unicode_csv_reader(src, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(open(src),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def parse_source(src):
    for num, row in enumerate(unicode_csv_reader(src, delimiter="|")):
        assert len(row) == 10, (src, num, len(row))
        yield row

def main():
    eng = parse_source(ENG_SOURCE)
    fra = parse_source(FRA_SOURCE)

    eng_headings = next(eng)
    fra_headings = next(fra)
    print eng_headings, fra_headings


main()
