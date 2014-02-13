#!/usr/bin/env python

import simplejson as json

ORGS = 'data/orgs.jsonl'


def main():
    choices = []
    for line in open(ORGS):
        org = json.loads(line)
        if 'department_number' not in org:
            continue
        choices.append({
            'eng': org['title'],
            'fra': org['title_fr'],
            'id': org['department_number'],
            'key': org['name'],
            })
    out = json.dumps(choices, ensure_ascii=False, indent=2, sort_keys=True)
    for line in out.split('\n'):
        print '          ' + line

if __name__ == '__main__':
    main()
