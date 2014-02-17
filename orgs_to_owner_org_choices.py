#!/usr/bin/env python

import simplejson as json

ORGS = 'data/orgs.jsonl'


def main():
    choices = []
    for line in open(ORGS):
        org = json.loads(line)
        if not org.get('department_number'):
            continue
        choices.append({
            'eng': org['title'],
            'fra': org['title_fr'],
            'id': int(org['department_number']),
            'key': org['name'],
            'pilot_uuid': org['id'],
            })
    out = json.dumps(choices, indent=2, sort_keys=True,
        separators=(', ', ': '))
    for line in out.split('\n')[1:-1]:
        print '          ' + line.encode('utf-8')

if __name__ == '__main__':
    main()
