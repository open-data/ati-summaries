#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import csv
import itertools

import xlwt

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

def fix_num_pages(pages):
    """
    Some page numbers were entered with a "." thousands separator
    which was then interpreted as a floating point by Excel.

    Try to repair that damage.
    """
    if u'.' in pages:
        try:
            return unicode(int(float(pages) * 1000))
        except ValueError:
            pass
    return pages

def normalize_request_number(num):
    """
    Some input data includes request numbers entered with slight
    variations such as: A2011-00013, A-2011-00013 and
    A-2013-00001, A-2013-0001

    This function normalizes request numbers by converting digits
    to integers and removing non-word characters such as '-'
    """

    split_re = re.compile(
        ur'[^\W\d]+' # "not (non-alphanumeric or numbers)" ~= only letters
        ur'|\d+' # also group numbers together
        , re.UNICODE)
    return tuple(
        int(g) if isdigit else g
        for isdigit, group in itertools.groupby(
            split_re.findall(num), key=lambda x: x.isdigit())
        for g in group
        )

def parse_source(src):
    for num, row in enumerate(unicode_csv_reader(src, delimiter="|")):
        assert len(row) == 10, (src, num, len(row))
        yield {
            'id': row[0],
            'org': fix_org_name(row[1]),
            'year': row[2],
            'month': row[3],
            'num': row[4],
            'norm_num': normalize_request_number(row[4]),
            'summary': row[5],
            'disp': row[6],
            'pages': fix_num_pages(row[7]),
            'contact': row[8],
            }

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


def write_matched(req_pairs, eng_org, fra_org, file_name):
    book = xlwt.Workbook()
    sheet = book.add_sheet('ATI AI')
    sheet.write(0, 3, eng_org)
    sheet.write(0, 4, fra_org)
    for col, h in enumerate([u'Year / Annee', u'Month / Mois',
            u'Request Number / Numero de la demande',
            u'ENG Summary / ENG Sommaire de la demande',
            u'FRA Summary / FRA Sommaire de la demande',
            u'Disposition',
            u'Number of Pages / Nombre de pages', 
            u'Contact Information / Information de contact']):
        sheet.write(1, col, h)
    sheet.col(0).width = 5 * 256
    sheet.col(1).width = 4 * 256
    sheet.col(2).width = 15 * 256
    sheet.col(3).width = 30 * 256
    sheet.col(4).width = 30 * 256
    sheet.col(5).width = 40 * 256

    row = 2
    sheet.set_panes_frozen(True) # frozen headings instead of split panes
    sheet.set_horz_split_pos(row) # in general, freeze after last heading row
    sheet.set_remove_splits(True) # if user does unfreeze, don't leave a split there

    req_pairs = sorted(req_pairs, key=lambda (eng, fra):
        (eng['year'], eng['month'], eng['num']))
    for eng, fra in req_pairs:
        def c(key):
            if eng[key] != fra[key]:
                return eng[key] + u' / ' + fra[key]
            return eng[key]
        for col, t in enumerate([c('year'), c('month'),
                c('num'), eng['summary'], fra['summary'],
                c('disp'), c('pages'), c('contact')]):
            sheet.write(row, col, t)
        row += 1
    book.save(file_name)


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
