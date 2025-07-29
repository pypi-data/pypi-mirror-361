# -*- coding: UTF-8 -*-
logger.info("Loading 27 objects to table ledger_account...")
# fields: id, ref, seqno, name, sheet_item, common_account, needs_partner, clearable, default_amount, sales_allowed, purchases_allowed, wages_allowed, taxes_allowed, clearings_allowed, bank_po_allowed, vat_column, ana_account, needs_ana
loader.save(
    create_ledger_account(
        1, u'1000', 1,
        ['Net income (loss)', 'Net income (loss)', 'Net income (loss)'], 17,
        '1000', True, True, None, False, False, False, False, False, False,
        None, None, False))
loader.save(
    create_ledger_account(21, u'4', 21, [
        'Commercial assets & liabilities', 'Commercial assets & liabilities',
        'Commercial assets & liabilities'
    ], None, None, False, False, None, False, False, False, False, False,
                          False, None, None, False))
loader.save(
    create_ledger_account(2, u'4000', 2, ['Customers', 'Kunden', 'Clients'], 3,
                          '4000', True, True, None, False, False, False, False,
                          False, False, None, None, False))
loader.save(
    create_ledger_account(3, u'4300', 3, [
        'Pending Payment Orders', 'Offene Zahlungsauftr\xe4ge',
        'Ordres de paiement ouverts'
    ], 14, '4300', True, True, None, False, False, False, False, False, False,
                          None, None, False))
loader.save(
    create_ledger_account(4, u'4400', 4,
                          ['Suppliers', 'Lieferanten', 'Fournisseurs'], 11,
                          '4400', True, True, None, False, False, False, False,
                          False, False, None, None, False))
loader.save(
    create_ledger_account(5, u'4500', 5,
                          ['Employees', 'Angestellte', 'Employ\xe9s'], None,
                          '4500', True, True, None, False, False, False, False,
                          False, False, None, None, False))
loader.save(
    create_ledger_account(
        7, u'4510', 7, ['VAT due', 'Geschuldete Mehrwertsteuer', 'TVA d\xfbe'],
        12, '4510', False, False, None, False, False, False, False, False,
        False, u'54', None, False))
loader.save(
    create_ledger_account(8, u'4511', 8, [
        'VAT returnable', 'R\xfcckzahlbare Mehrwertsteuer',
        'TVA \xe0 retourner'
    ], 12, '4511', False, False, None, False, False, False, False, False,
                          False, None, None, False))
loader.save(
    create_ledger_account(
        9, u'4512', 9,
        ['VAT deductible', 'Abziehbare Mehrwertsteuer', 'TVA d\xe9ductible'],
        12, '4512', False, False, None, False, False, False, False, False,
        False, None, None, False))
loader.save(
    create_ledger_account(
        10, u'4513', 10,
        ['VAT declared', 'Deklarierte Mehrwertsteuer', 'TVA d\xe9clar\xe9e'],
        12, '4513', False, False, None, False, False, False, False, False,
        False, None, None, False))
loader.save(
    create_ledger_account(6, u'4600', 6,
                          ['Tax Offices', 'Steuer\xe4mter', 'Tax Offices'], 12,
                          '4600', True, True, None, False, False, False, False,
                          False, False, None, None, False))
loader.save(
    create_ledger_account(11, u'4900', 11,
                          ['Waiting account', 'Wartekonto', 'Waiting account'],
                          14, '4900', True, True, None, False, False, False,
                          False, False, False, None, None, False))
loader.save(
    create_ledger_account(22, u'5', 22, [
        'Financial assets & liabilities', 'Financial assets & liabilities',
        'Financial assets & liabilities'
    ], None, None, False, False, None, False, False, False, False, False,
                          False, None, None, False))
loader.save(
    create_ledger_account(12, u'5500', 12,
                          ['BestBank', 'BestBank', 'BestBank'], 13, '5500',
                          False, False, None, False, False, False, False,
                          False, False, None, None, False))
loader.save(
    create_ledger_account(13, u'5700', 13, ['Cash', 'Kasse', 'Caisse'], 13,
                          '5700', False, False, None, False, False, False,
                          False, False, False, None, None, False))
loader.save(
    create_ledger_account(23, u'6', 23,
                          ['Expenses', 'Ausgaben', 'D\xe9penses'], None, None,
                          False, False, None, False, False, False, False,
                          False, False, None, None, False))
loader.save(
    create_ledger_account(24, u'60', 24,
                          ['Operation costs', 'Diplome', 'Operation costs'],
                          None, None, False, False, None, False, False, False,
                          False, False, False, None, None, False))
loader.save(
    create_ledger_account(15, u'6010', 15, [
        'Purchase of services', 'Eink\xe4ufe von Dienstleistungen',
        'Achats de services'
    ], 20, '6010', False, False, None, False, True, False, False, False, False,
                          u'75', None, True))
loader.save(
    create_ledger_account(16, u'6020', 16, [
        'Purchase of investments', 'Investierungsk\xe4ufe',
        "Achats d'investissement"
    ], 21, '6020', False, False, None, False, True, False, False, False, False,
                          u'72', None, True))
loader.save(
    create_ledger_account(
        14, u'6040', 14,
        ['Purchase of goods', 'Wareneink\xe4ufe', 'Achats de marchandises'],
        19, '6040', False, False, None, False, True, False, False, False,
        False, u'71', None, True))
loader.save(
    create_ledger_account(25, u'61', 25,
                          ['Wages', 'L\xf6hne und Geh\xe4lter', 'Salaires'],
                          None, None, False, False, None, False, False, False,
                          False, False, False, None, None, False))
loader.save(
    create_ledger_account(17, u'6300', 17,
                          ['Wages', 'L\xf6hne und Geh\xe4lter', 'Salaires'],
                          20, '6300', False, False, None, False, False, False,
                          False, False, False, None, None, False))
loader.save(
    create_ledger_account(18, u'6900', 18,
                          ['Net income', 'Net income', 'Net income'], 22,
                          '6900', False, False, None, False, False, False,
                          False, False, False, None, None, False))
loader.save(
    create_ledger_account(26, u'7', 26, ['Revenues', 'Revenues', 'Revenues'],
                          None, None, False, False, None, False, False, False,
                          False, False, False, None, None, False))
loader.save(
    create_ledger_account(19, u'7000', 19, ['Sales', 'Verkauf', 'Ventes'], 24,
                          '7000', False, False, None, True, False, False,
                          False, False, False, None, None, False))
loader.save(
    create_ledger_account(
        27, u'7010', 27,
        ['Sales on therapies', 'Sales on therapies', 'Sales on therapies'], 24,
        None, False, False, None, False, False, False, False, False, False,
        None, None, False))
loader.save(
    create_ledger_account(20, u'7900', 20,
                          ['Net loss', 'Net loss', 'Net loss'], 25, '7900',
                          False, False, None, False, False, False, False,
                          False, False, None, None, False))

loader.flush_deferred_objects()
