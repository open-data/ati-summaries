#!/usr/bin/env python

import json

INPUT_JSONL = 'data/orgs.jsonl'

for l in open(INPUT_JSONL):
    org = json.loads(l)
    print json.dumps({
        'id': org['id'],
        'name': org['name'],
        'title' : u'%s | %s' % (org['title'], org['title_fr']),
        'extras': [
            {'key': 'department_number', 'value': org['department_number']},
            {'key': 'shortform', 'value': org['shortform']},
            {'key': 'shortform_fr', 'value': org['shortform_fr']},
            {'key': 'ati_email', 'value': org['email']},
            ],
        })
