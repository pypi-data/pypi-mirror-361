# -*- coding: UTF-8 -*-
logger.info("Loading 31 objects to table sepa_account...")
# fields: id, partner, iban, bic, remark, primary
loader.save(
    create_sepa_account(1, 188, u'EE872200221012067904', u'HABAEE2X', u'',
                        True))
loader.save(
    create_sepa_account(2, 189, u'EE732200221045112758', u'HABAEE2X', u'',
                        True))
loader.save(
    create_sepa_account(3, 190, u'EE232200001180005555', u'HABAEE2X',
                        u'Eraklilendile', True))
loader.save(
    create_sepa_account(4, 190, u'EE322200221112223334', u'HABAEE2X',
                        u'\xc4rikliendile', False))
loader.save(
    create_sepa_account(5, 190, u'EE081010002059413005', u'EEUHEE2X', u'',
                        False))
loader.save(
    create_sepa_account(6, 190, u'EE703300332099000006', u'FOREEE2X', u'',
                        False))
loader.save(
    create_sepa_account(7, 190, u'EE431700017000115797', u'NDEAEE2X', u'',
                        False))
loader.save(
    create_sepa_account(8, 191, u'EE382200221013987931', u'HABAEE2X', u'',
                        True))
loader.save(
    create_sepa_account(9, 192, u'EE522200221013264447', u'HABAEE2X', u'',
                        True))
loader.save(
    create_sepa_account(10, 193, u'EE202200221001178338', u'HABAEE2X', u'',
                        True))
loader.save(
    create_sepa_account(11, 193, u'EE781010220002715011', u'', u'', False))
loader.save(
    create_sepa_account(12, 193, u'EE321700017000231134', u'', u'', False))
loader.save(
    create_sepa_account(13, 194, u'BE46000325448336', u'BPOTBEB1', u'', True))
loader.save(
    create_sepa_account(14, 194, u'BE81000325873924', u'BPOTBEB1', u'', False))
loader.save(
    create_sepa_account(15, 195, u'BE79827081803833', u'ETHIBEBB', u'', True))
loader.save(
    create_sepa_account(16, 196, u'BE98348031033293', u'BBRUBEBB', u'', True))
loader.save(
    create_sepa_account(17, 197, u'BE38248017357572', u'GEBABEBB', u'', True))
loader.save(
    create_sepa_account(18, 101, u'EE436294797788261706', u'BBRUBEBB', u'',
                        True))
loader.save(
    create_sepa_account(19, 102, u'BE83540256917919', u'BBRUBEBB', u'', True))
loader.save(
    create_sepa_account(20, 103, u'BE70458836777241', u'BBRUBEBB', u'', True))
loader.save(
    create_sepa_account(21, 104, u'BE62315236188996', u'BBRUBEBB', u'', True))
loader.save(
    create_sepa_account(22, 105, u'BE08853988745497', u'BBRUBEBB', u'', True))
loader.save(
    create_sepa_account(23, 106, u'NL60UQGK4026224708', u'BBRUBEBB', u'',
                        True))
loader.save(
    create_sepa_account(24, 107, u'NL03ZSEU7683047716', u'BBRUBEBB', u'',
                        True))
loader.save(
    create_sepa_account(25, 108, u'DE70417630904413326955', u'BBRUBEBB', u'',
                        True))
loader.save(
    create_sepa_account(26, 109, u'DE20747128173755343928', u'BBRUBEBB', u'',
                        True))
loader.save(
    create_sepa_account(27, 110, u'DE35925967355688573820', u'BBRUBEBB', u'',
                        True))
loader.save(
    create_sepa_account(28, 111, u'FR5928381777532178049892704', u'BBRUBEBB',
                        u'', True))
loader.save(
    create_sepa_account(29, 112, u'FR6815265988888370706343396', u'BBRUBEBB',
                        u'', True))
loader.save(
    create_sepa_account(30, 199, u'BE31486666479523', u'BBRUBEBB', u'', True))
loader.save(
    create_sepa_account(31, 198, u'BE03747769840658', u'BBRUBEBB', u'', True))

loader.flush_deferred_objects()
