#!/usr/bin/env python

import json

ORGS = 'data/orgs.jsonl'
DATA_GC_CA_ORGS = 'data/data_gc_ca_orgs.json'

def main():
    migrate = []
    portal_orgs = json.load(open(DATA_GC_CA_ORGS))
    for line in open(ORGS):
        org = json.loads(line)
        dept_id = org.get('department_number')
        if not dept_id:
            continue
        original_name = pilot_uuid = ''
        if dept_id in portal_orgs:
            po = portal_orgs.pop(dept_id)
            original_name = po['name']
            if po['uuid'] == po['uuid'].upper():
                # dirty hack: portal uuids are all uppercase
                pilot_uuid = po['uuid']
        else:
            for i, po in portal_orgs.iteritems():
                if po['name'] == org['name']:
                    original_name = po['name']
                    if po['uuid'] == po['uuid'].upper():
                        pilot_uuid = po['uuid']
                    break
        migrate.append((
            org['name'],
            org['title'],
            org['alternate_names'] if org['alternate_names'] != org['title'] else '',
            original_name,
            pilot_uuid,
            ))

    migrate.sort()
    for line in migrate:
        print ','.join('"%s"' % v.encode('utf-8') for v in line)


if __name__ == '__main__':
    main()
