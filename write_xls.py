import xlwt

OUTPUT_PATTERN = 'xls/{0}.xls'


def write_matched(req_pairs, org):
    book = xlwt.Workbook()
    sheet = book.add_sheet('ATI AI')
    sheet.write(0, 2, org['name'])
    sheet.write(0, 3, org['eng'])
    sheet.write(0, 4, org['fra'])
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
    book.save(OUTPUT_PATTERN.format(org['name']))
