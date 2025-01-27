# -*- coding: utf-8 -*-

import re
import csv
import itertools

ORG_FIXUPS = {
    u'http://www.cbc.radio-canada.ca/_structures/default/_img/logo-large.png':
        u'Canadian Broadcasting Corportation',
    u'Port of Trois-Rivi�res': u'Port of Trois-Rivières',
    u'Élections Canada':
        u'Bureau du directeur général des élections (Élections Canada)',
    }

def unicode_csv_reader(src, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(open(src, 'rb'),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def fix_org_name(name):
    name = name.replace(u'  ', u' ')
    name = name.replace(u'  ', u' ')
    name = ORG_FIXUPS.get(name, name)
    return name

def fix_num_pages(pages):
    """
    Some page numbers were entered with a "." thousands separator
    which was then interpreted as a floating point by Excel.

    Try to repair that damage.
    """
    p = pages
    # other junk seen in input data
    p = p.replace('pages', '')
    p = p.replace('page', '')
    p = p.replace(',', '')
    p = p.replace(' ', '')
    p = p.replace('*', '')
    if u'.' in pages:
        try:
            return unicode(int(float(p) * 1000))
        except ValueError:
            pass
    try:
        return unicode(int(p))
    except ValueError:
        return pages

def fix_numeric(num):
    try:
        return unicode(int(num))
    except ValueError:
        return num

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
    for num, row in enumerate(unicode_csv_reader(src)):
        assert len(row) == 7, (src, num + 1, row)
        try:
            int(fix_num_pages(row[5]))
        except ValueError:
            pass
        else:
            # disp and pages are reversed
            row[5], row[6] = row[6], row[5]
        yield {
            'org': fix_org_name(row[0]),
            'year': fix_numeric(row[1]),
            'month': fix_numeric(row[2]),
            'num': row[3],
            'norm_num': normalize_request_number(row[3]),
            'summary': row[4],
            'disp': row[5],
            'pages': fix_num_pages(row[6]),
            }
