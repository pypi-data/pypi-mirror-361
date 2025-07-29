# -*- coding: UTF-8 -*-
logger.info("Loading 20 objects to table ana_account...")
# fields: id, ref, seqno, designation
loader.save(
    create_ana_account(1, u'1', 1,
                       ['Operation costs', 'Diplome', 'Operation costs']))
loader.save(
    create_ana_account(2, u'1100', 2,
                       ['Wages', 'L\xf6hne und Geh\xe4lter', 'Salaires']))
loader.save(
    create_ana_account(3, u'1200', 3, ['Transport', 'Transport', 'Transport']))
loader.save(
    create_ana_account(4, u'1300', 4, ['Training', 'Ausbildung', 'Formation']))
loader.save(
    create_ana_account(5, u'1400', 5,
                       ['Other costs', 'Sonstige Unkosten', 'Other costs']))
loader.save(
    create_ana_account(
        6, u'2', 6,
        ['Administrative costs', 'Verwaltungskosten', 'Administrative costs']))
loader.save(
    create_ana_account(
        7, u'2100', 7,
        ['Secretary wages', 'Geh\xe4lter Sekretariat', 'Secretary wages']))
loader.save(
    create_ana_account(
        8, u'2110', 8,
        ['Manager wages', 'Geh\xe4lter Direktion', 'Manager wages']))
loader.save(
    create_ana_account(9, u'2200', 9, ['Transport', 'Transport', 'Transport']))
loader.save(
    create_ana_account(10, u'2300', 10,
                       ['Training', 'Ausbildung', 'Formation']))
loader.save(
    create_ana_account(11, u'3', 11,
                       ['Investments', 'Investierungen', 'Investments']))
loader.save(
    create_ana_account(12, u'3000', 12,
                       ['Investment', 'Investierung', 'Investment']))
loader.save(
    create_ana_account(13, u'4', 13, ['Project 1', 'Projekt 1', 'Project 1']))
loader.save(
    create_ana_account(14, u'4100', 14,
                       ['Wages', 'L\xf6hne und Geh\xe4lter', 'Salaires']))
loader.save(
    create_ana_account(15, u'4200', 15,
                       ['Transport', 'Transport', 'Transport']))
loader.save(
    create_ana_account(16, u'4300', 16,
                       ['Training', 'Ausbildung', 'Formation']))
loader.save(
    create_ana_account(17, u'5', 17, ['Project 2', 'Projekt 2', 'Project 2']))
loader.save(
    create_ana_account(18, u'5100', 18,
                       ['Wages', 'L\xf6hne und Geh\xe4lter', 'Salaires']))
loader.save(
    create_ana_account(19, u'5200', 19,
                       ['Transport', 'Transport', 'Transport']))
loader.save(
    create_ana_account(20, u'5300', 20,
                       ['Other costs', 'Sonstige Unkosten', 'Other costs']))

loader.flush_deferred_objects()
