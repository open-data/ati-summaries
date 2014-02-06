#!/usr/bin/env python

import csv
import json

from read_fix_csv import unicode_csv_reader, parse_source
from write_xls import write_matched

ENG_SOURCE = 'data/ai-utf8-eng.csv'
FRA_SOURCE = 'data/ai-utf8-fra.csv'
ORGS = 'data/orgs.jsonl'

DUPLICATED = 'duplicated'


def group_requests_by_org(source):
    org_numbers = {}
    unmatched = []
    for req in source:
        try:
            int(req['year']), int(req['month']), int(req['pages'])
        except ValueError:
            unmatched.append(dict(req, reason='non-integer Y/M/pages'))
            continue
        requests = org_numbers.setdefault(req['org'], {})
        previous = requests.get(req['norm_num'])
        if previous is DUPLICATED:
            unmatched.append(dict(req, reason='duplicate with differences'))
        elif previous:
            if all(v == req[k] for k, v in previous.items() if k != 'id'):
                continue # ignore exact duplicates
            unmatched.append(dict(previous, reason='duplicate with differences'))
            unmatched.append(dict(req, reason='duplicate with differences'))
            requests[req['norm_num']] = DUPLICATED
        else:
            requests[req['norm_num']] = req

    return org_numbers, unmatched


def write_unmatched(org_reqs, unmatched, file_name, org_mapping=None):
    if org_mapping is None:
        org_mapping = {}

    f = open(file_name, 'wb')
    writer = csv.writer(f)

    unmatched = list(unmatched)
    duplicated_in_source = len(unmatched)
    print file_name, "duplicated in source:", duplicated_in_source
    unmatched.extend(
        (req if 'reason' in req else dict(req, reason='no match found'))
        for org in org_reqs.values()
        for req in org.values()
        if req is not DUPLICATED)
    print file_name, "unmatched:", len(unmatched) - duplicated_in_source
    unmatched.sort(key=lambda req: (
        org_mapping.get(req['org'], req['org']),
        req['norm_num'],
        req
        ))
    writer.writerows(
        [org[x].encode('utf-8') for x in ('org', 'year', 'month',
            'num', 'summary', 'disp', 'pages', 'reason',)]
        for org in unmatched)


def load_organizations():
    orgs = []
    dept_ids = set()
    for line in open(ORGS):
        org = json.loads(line)
        dept_id = org.get('department_number')
        if not dept_id:
            print "no dept id:", org['name']
            continue
        else:
            if dept_id in dept_ids:
                print "dept id repeated:", dept_id
            dept_ids.add(dept_id)
        if not org.get('title_fr'):
            print "no title_fr", org['name']
        orgs.append({
            'eng': org['title'],
            'fra': org.get('title_fr', org['title']),
            'dept_id': dept_id,
            'name': org['name'],
            })
    return orgs


def main():
    eng = parse_source(ENG_SOURCE)
    fra = parse_source(FRA_SOURCE)

    eng_headings = next(eng)
    fra_headings = next(fra)

    eng_reqs, eng_unmatched = group_requests_by_org(eng)
    fra_reqs, fra_unmatched = group_requests_by_org(fra)

    orgs = load_organizations()

    matched_total = 0
    for org in orgs:
        eng = eng_reqs.get(org['eng'], {})
        fra = fra_reqs.get(org['fra'], {})
        matched_num = []
        for num, eng_req in eng.iteritems():
            fra_req = fra.get(num)
            if eng_req is DUPLICATED:
                if fra_req and fra_req is not DUPLICATED:
                    fra_req['reason'] = 'matching eng record has errors'
                continue
            if fra_req is DUPLICATED:
                eng_req['reason'] = 'matching fra record has errors'
                continue
            if not fra_req:
                continue
            if any(eng_req[v] != fra_req[v] for v in
                    ('pages', 'year', 'month')):
                eng_req['reason'] = 'matching fra record has different Y/M/pages'
                fra_req['reason'] = 'matching eng record has different Y/M/pages'
                continue
            matched_num.append(num)

        if not matched_num:
            continue

        if org['name']:
            write_matched([(eng[m], fra[m]) for m in matched_num], org)
            matched_total += len(matched_num)
        else:
            print "not writing:", len(matched_num), "-", org['eng']

        for num in matched_num:
            del eng[num]
            del fra[num]

    print "wrote: {0} eng+fra records".format(matched_total)

    write_unmatched(eng_reqs, eng_unmatched, 'data/unmatched_eng.csv')
    write_unmatched(fra_reqs, fra_unmatched, 'data/unmatched_fra.csv',
        dict((o['fra'], o['eng']) for o in orgs))


if __name__ == '__main__':
    main()
