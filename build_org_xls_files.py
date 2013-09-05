#!/usr/bin/env python

import csv
import json

from read_fix_csv import unicode_csv_reader, parse_source
from write_xls import write_matched

ENG_SOURCE = 'data/ati_en.csv'
FRA_SOURCE = 'data/ati_fr.csv'
ORG_MAPPING = 'data/orgMapping.csv'
DATA_GC_CA_ORGS = 'data/data_gc_ca_orgs.json'

DUPLICATED = 'duplicated'


def group_requests_by_org(source):
    org_numbers = {}
    unmatched = []
    for req in source:
        requests = org_numbers.setdefault(req['org'], {})
        previous = requests.get(req['norm_num'])
        if previous is DUPLICATED:
            unmatched.append(req)
        elif previous:
            if all(v == req[k] for k, v in previous.items() if k != 'id'):
                continue # ignore exact duplicates
            unmatched.append(previous)
            unmatched.append(req)
            requests[req['norm_num']] = DUPLICATED
        else:
            requests[req['norm_num']] = req

    return org_numbers, unmatched


def write_unmatched(org_reqs, unmatched, file_name, org_mapping):
    f = open(file_name, 'wb')
    writer = csv.writer(f)

    unmatched = list(unmatched)
    print len(unmatched)
    unmatched.extend(req
        for org in org_reqs.values()
        for req in org.values()
        if req is not DUPLICATED)
    print len(unmatched)
    unmatched.sort(key=lambda req: (
        org_mapping.get(req['org'], req['org']),
        req['norm_num'],
        req['id']))
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

    org_mapping_source = unicode_csv_reader(ORG_MAPPING)
    org_mapping_headings = next(org_mapping_source)
    org_mapping = dict((o[1], o[0]) for o in org_mapping_source)
    for fra_org, eng_org in org_mapping.items():
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

        if eng_org.startswith('Health Canada'):
            write_matched([(eng[m], fra[m]) for m in matched_num],
                eng_org, fra_org, 'data/health_canada.xls')

        for num in matched_num:
            del eng[num]
            del fra[num]

    write_unmatched(eng_reqs, eng_unmatched, 'data/unmatched_eng.csv',
        org_mapping)
    write_unmatched(fra_reqs, fra_unmatched, 'data/unmatched_fra.csv',
        org_mapping)


if __name__ == '__main__':
    main()
