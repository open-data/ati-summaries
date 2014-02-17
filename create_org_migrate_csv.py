#!/usr/bin/env python

import json
import sys

ORGS = 'data/orgs.jsonl'
DATA_GC_CA_ORGS = 'data/data_gc_ca_orgs.json'

ORG_MIGRATE = 'data/org-migrate.csv'

def main():
    out = open(ORG_MIGRATE, 'w')
    migrate = []
    portal_orgs = json.load(open(DATA_GC_CA_ORGS))
    for line in open(ORGS):
        org = json.loads(line)
        dept_id = org.get('department_number')
        if not dept_id:
            continue
        original_name = pilot_uuid = original_title = ''
        if dept_id in portal_orgs:
            po = portal_orgs.pop(dept_id)
            original_title = po['title'].split('|')[0].strip()
            original_name = po['name']
            pilot_uuid = po['uuid']
        else:
            for i, po in portal_orgs.iteritems():
                if po['name'] == org['name'] or po['uuid'] == org['id']:
                    original_title = po['title'].split('|')[0].strip()
                    original_name = po['name']
                    pilot_uuid = po['uuid']
                    del portal_orgs[i]
                    break
        migrate.append((
            org['name'],
            org['title'],
            org['alternate_names'] if org['alternate_names'] != org['title'] else '',
            original_title if original_title != org['title'] else '',
            original_name if original_name != org['name'] else '',
            pilot_uuid,
            ))

    migrate.sort()
    for line in migrate:
        out.write(','.join('"%s"' % v.encode('utf-8') for v in line) + '\n')

    for po in portal_orgs.iteritems():
        sys.stderr.write(repr(po)+'\n')


if __name__ == '__main__':
    main()
