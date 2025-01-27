import xlwt

OUTPUT_PATTERN = 'xls/{0}.xls'


def write_matched(req_pairs, org):
    book = xlwt.Workbook()
    sheet = book.add_sheet('ATI AI')
    heading_xf = xlwt.easyxf('pattern: pattern solid, fore_color gray25;')
    sheet.write(0, 0, int(org['dept_id']), heading_xf)
    sheet.write(0, 1, '', heading_xf)
    sheet.write(0, 2, org['name'], heading_xf)
    sheet.write(0, 3, org['eng'], heading_xf)
    sheet.write(0, 4, org['fra'], heading_xf)
    sheet.write(0, 5, '', heading_xf)
    sheet.write(0, 6, '', heading_xf)
    heading_xf = xlwt.easyxf('font: bold on; '
        'pattern: pattern solid, fore_color light_green;')
    for col, h in enumerate([u'Year/Annee', u'Month/Mois',
            u'Number/Numero',
            u'ENG Summary/Sommaire',
            u'FRA Summary/Sommaire',
            u'Disposition',
            u'Pages',
            ]):
        sheet.write(1, col, h, heading_xf)
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
        for col, t in enumerate([int(c('year')), int(c('month')),
                c('num'), eng['summary'], fra['summary'],
                c('disp'), int(c('pages'))]):
            sheet.write(row, col, t)
        row += 1
    book.save(OUTPUT_PATTERN.format(org['name']))
