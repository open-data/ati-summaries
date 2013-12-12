#!/usr/bin/env python

import json
import uuid
from read_fix_csv import unicode_csv_reader

"""
convert from an exported list of orgs to a jsonl file that may be
imported by ckanext-scheming as organizations
"""

SOURCE_ORGS = 'data/orgs-utf8.csv'
ORG_UUIDS = 'data/data_gc_ca_orgs.json'
OUTPUT_JSONL = 'data/orgs.jsonl'

def org_name(en_abbr, fr_abbr, dept_no):
    if not en_abbr:
        return "org" + dept_no
    if en_abbr == fr_abbr:
        return en_abbr.lower()
    return (en_abbr + '-' + fr_abbr).lower().replace(' ', '')

def main():
    orgs = unicode_csv_reader(SOURCE_ORGS)
    out = open(OUTPUT_JSONL, 'w')
    org_uuids = json.loads(open(ORG_UUIDS).read())
    for o in orgs:
        if o[0] == 'English':
            break
    for o in orgs:
        old_org = org_uuids.get(o[8])
        name = org_name(o[1], o[5], o[8])
        assert name
        if old_org:
            oid = old_org['uuid']
        else:
            print 'no uuid:', o[0], repr(o[8])
            oid = str(uuid.uuid5(uuid.NAMESPACE_URL,
                (u'http://data.gc.ca/data/organization/%s' % name).encode(
                    'ascii')))
        out.write(json.dumps({
            'id': oid,
            'title': o[0],
            'name': name,
            'alternate_names': o[2],
            'homepage': o[3],
            'title_fr': o[4],
            'alternate_names_fr': o[6],
            'homepage_fr': o[7],
            'department_number': o[8],
            'phone': o[9],
            'fax': o[10],
            'email': o[11],
            'address': o[12],
            'address_fr': o[13],
            }, sort_keys=True) + '\n')

main()
