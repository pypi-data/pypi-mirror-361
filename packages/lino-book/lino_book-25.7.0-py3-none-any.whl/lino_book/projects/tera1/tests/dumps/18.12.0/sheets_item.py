# -*- coding: UTF-8 -*-
logger.info("Loading 25 objects to table sheets_item...")
# fields: id, ref, designation, dc, sheet_type, common_item, mirror_ref
loader.save(
    create_sheets_item(1, u'1', ['Assets', 'Verm\xf6gen', 'Actifs'], False,
                       'B', '1', None))
loader.save(
    create_sheets_item(2, u'10',
                       ['Current assets', 'Current assets', 'Current assets'],
                       False, 'B', '10', None))
loader.save(
    create_sheets_item(3, u'1000', [
        'Customers receivable', 'Customers receivable', 'Customers receivable'
    ], False, 'B', '1000', None))
loader.save(
    create_sheets_item(
        4, u'1010',
        ['Taxes receivable', 'Taxes receivable', 'Taxes receivable'], False,
        'B', '1010', u'2010'))
loader.save(
    create_sheets_item(5, u'1020', [
        'Cash and cash equivalents', 'Cash and cash equivalents',
        'Cash and cash equivalents'
    ], False, 'B', '1020', u'2020'))
loader.save(
    create_sheets_item(
        6, u'1030',
        ['Current transfers', 'Current transfers', 'Current transfers'], False,
        'B', '1030', u'2030'))
loader.save(
    create_sheets_item(7, u'1090', [
        'Other current assets', 'Other current assets', 'Other current assets'
    ], False, 'B', '1090', u'2090'))
loader.save(
    create_sheets_item(
        8, u'11',
        ['Non-current assets', 'Non-current assets', 'Non-current assets'],
        False, 'B', '11', None))
loader.save(
    create_sheets_item(9, u'2', ['Passiva', 'Passiva', 'Passiva'], True, 'B',
                       '2', None))
loader.save(
    create_sheets_item(10, u'20',
                       ['Liabilities', 'Verpflichtungen', 'Passifs'], True,
                       'B', '20', None))
loader.save(
    create_sheets_item(
        11, u'2000',
        ['Suppliers payable', 'Suppliers payable', 'Suppliers payable'], True,
        'B', '2000', None))
loader.save(
    create_sheets_item(12, u'2010',
                       ['Taxes payable', 'Taxes payable', 'Taxes payable'],
                       True, 'B', '2010', u'1010'))
loader.save(
    create_sheets_item(13, u'2020', ['Banks', 'Banks', 'Banks'], True, 'B',
                       '2020', u'1020'))
loader.save(
    create_sheets_item(
        14, u'2030',
        ['Current transfers', 'Current transfers', 'Current transfers'], True,
        'B', '2030', u'1030'))
loader.save(
    create_sheets_item(
        15, u'2090',
        ['Other liabilities', 'Other liabilities', 'Other liabilities'], True,
        'B', '2090', u'1090'))
loader.save(
    create_sheets_item(16, u'21',
                       ['Own capital', 'Own capital', 'Own capital'], True,
                       'B', '21', None))
loader.save(
    create_sheets_item(
        17, u'2150',
        ['Net income (loss)', 'Net income (loss)', 'Net income (loss)'], True,
        'B', '2150', None))
loader.save(
    create_sheets_item(18, u'6', ['Expenses', 'Ausgaben', 'D\xe9penses'],
                       False, 'R', '6', None))
loader.save(
    create_sheets_item(19, u'6000',
                       ['Cost of sales', 'Cost of sales', 'Cost of sales'],
                       False, 'R', '6000', None))
loader.save(
    create_sheets_item(
        20, u'6100',
        ['Operating expenses', 'Operating expenses', 'Operating expenses'],
        False, 'R', '6100', None))
loader.save(
    create_sheets_item(21, u'6200',
                       ['Other expenses', 'Other expenses', 'Other expenses'],
                       False, 'R', '6200', None))
loader.save(
    create_sheets_item(22, u'6900', ['Net income', 'Net income', 'Net income'],
                       False, 'R', '6900', u'7900'))
loader.save(
    create_sheets_item(23, u'7', ['Revenues', 'Revenues', 'Revenues'], True,
                       'R', '7', None))
loader.save(
    create_sheets_item(24, u'7000', ['Net sales', 'Net sales', 'Net sales'],
                       True, 'R', '7000', None))
loader.save(
    create_sheets_item(25, u'7900', ['Net loss', 'Net loss', 'Net loss'], True,
                       'R', '7900', u'6900'))

loader.flush_deferred_objects()
