#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv

ENG_SOURCE = 'data/ati_en.csv'
FRA_SOURCE = 'data/ati_fr.csv'
ORG_MAPPING = 'data/orgMapping.csv'

ORG_FIXUPS = {
    u'http://www.cbc.radio-canada.ca/_structures/default/_img/logo-large.png':
        u'Canadian Broadcasting Corportation',
    u'Port of Trois-Rivi�res': u'Port of Trois-Rivières',
    u'Élections Canada':
        u'Bureau du directeur général des élections (Élections Canada)',
    }

DUPLICATED = 'duplicated'

def unicode_csv_reader(src, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(open(src, 'rb'),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def fix_org_name(name):
    name = name.replace(u'  ', u' ')
    name = ORG_FIXUPS.get(name, name)
    return name

def parse_source(src):
    for num, row in enumerate(unicode_csv_reader(src, delimiter="|")):
        assert len(row) == 10, (src, num, len(row))
        yield {
            'id': row[0],
            'org': fix_org_name(row[1]),
            'year': row[2],
            'month': row[3],
            'num': row[4],
            'summary': row[5],
            'disp': row[6],
            'pages': row[7],
            'contact': row[8],
            }

def group_requests_by_org(source):
    org_numbers = {}
    unmatched = []
    for req in source:
        requests = org_numbers.setdefault(req['org'], {})
        previous = requests.get(req['num'])
        if previous is DUPLICATED:
            unmatched.append(req)
        elif previous:
            unmatched.append(previous)
            unmatched.append(req)
            requests[req['num']] = DUPLICATED
        else:
            requests[req['num']] = req

    return org_numbers, unmatched


def write_unmatched(org_reqs, unmatched, file_name):
    f = open(file_name, 'wb')
    writer = csv.writer(f)

    unmatched = list(unmatched)
    unmatched.extend(req
        for org in org_reqs.values()
        for req in org.values()
        if req is not DUPLICATED)
    unmatched.sort(key=lambda req: (req['org'], req['num'], req['id']))
    writer.writerows(
        [org[x].encode('utf-8') for x in ('id', 'org', 'year', 'month',
            'num', 'summary', 'disp', 'pages',)]
        for org in unmatched)


def main():
    eng = parse_source(ENG_SOURCE)
    fra = parse_source(FRA_SOURCE)

    eng_headings = next(eng)
    fra_headings = next(fra)

    eng_reqs, eng_unmatched = group_requests_by_org(eng)
    fra_reqs, fra_unmatched = group_requests_by_org(fra)

    org_mapping = unicode_csv_reader(ORG_MAPPING)
    org_mapping_headings = next(org_mapping)
    for eng_org, fra_org in org_mapping:
        eng = eng_reqs.get(eng_org, {})
        fra = fra_reqs.get(fra_org, {})
        matched_num = []
        for num, eng_req in eng.iteritems():
            if eng_req is DUPLICATED:
                continue
            fra_req = fra.get(num)
            if not fra_req or fra_req is DUPLICATED:
                continue
            matched_num.append(num)
        for num in matched_num:
            del eng[num]
            del fra[num]

    write_unmatched(eng_reqs, eng_unmatched, 'data/unmatched_eng.csv')
    write_unmatched(fra_reqs, fra_unmatched, 'data/unmatched_fra.csv')


main()
