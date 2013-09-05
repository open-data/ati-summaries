#!/usr/bin/env python

DATA_GC_CA = "http://data.gc.ca/data/"
OUTPUT_FILE = "data/data_gc_ca_orgs.json"

import json
import ckanapi

def main():
    out = {}

    od = ckanapi.RemoteCKAN(DATA_GC_CA)
    org_names = od.action.organization_list()
    for name in org_names:
        org = od.action.organization_show(id=name)
        dep_nums = [e['value']
            for e in org['extras'] if e['key'] == 'department_number']
        if not dep_nums:
            continue
        out[dep_nums[0]] = {
            'uuid': org['id'],
            'title': org['title'],
            'name': name,
            }
        print name

    with open(OUTPUT_FILE, 'wb') as f:
        f.write(json.dumps(out, sort_keys=True, indent=2))

main()
