# -*- coding: UTF-8 -*-
logger.info("Loading 20 objects to table sheets_anaaccountentry...")
# fields: id, report, old_d, old_c, during_d, during_c, ana_account
loader.save(
    create_sheets_anaaccountentry(21, 1, '0.00', '0.00', '559.50', '0.00', 2))
loader.save(
    create_sheets_anaaccountentry(22, 1, '0.00', '0.00', '1421.70', '0.00', 3))
loader.save(
    create_sheets_anaaccountentry(23, 1, '0.00', '0.00', '3683.98', '0.00', 4))
loader.save(
    create_sheets_anaaccountentry(24, 1, '0.00', '0.00', '685.00', '0.00', 5))
loader.save(
    create_sheets_anaaccountentry(25, 1, '0.00', '0.00', '1729.40', '0.00', 7))
loader.save(
    create_sheets_anaaccountentry(26, 1, '0.00', '0.00', '4559.48', '0.00', 8))
loader.save(
    create_sheets_anaaccountentry(27, 1, '0.00', '0.00', '3642.18', '0.00', 9))
loader.save(
    create_sheets_anaaccountentry(28, 1, '0.00', '0.00', '544.10', '0.00', 10))
loader.save(
    create_sheets_anaaccountentry(29, 1, '0.00', '0.00', '1404.50', '0.00',
                                  12))
loader.save(
    create_sheets_anaaccountentry(30, 1, '0.00', '0.00', '3569.48', '0.00',
                                  14))
loader.save(
    create_sheets_anaaccountentry(31, 1, '0.00', '0.00', '439.80', '0.00', 15))
loader.save(
    create_sheets_anaaccountentry(32, 1, '0.00', '0.00', '501.50', '0.00', 16))
loader.save(
    create_sheets_anaaccountentry(33, 1, '0.00', '0.00', '1342.80', '0.00',
                                  18))
loader.save(
    create_sheets_anaaccountentry(34, 1, '0.00', '0.00', '3483.58', '0.00',
                                  19))
loader.save(
    create_sheets_anaaccountentry(35, 1, '0.00', '0.00', '287.40', '0.00', 20))
loader.save(
    create_sheets_anaaccountentry(36, 1, '0.00', '0.00', '6350.18', '0.00', 1))
loader.save(
    create_sheets_anaaccountentry(37, 1, '0.00', '0.00', '10475.16', '0.00',
                                  6))
loader.save(
    create_sheets_anaaccountentry(38, 1, '0.00', '0.00', '1404.50', '0.00',
                                  11))
loader.save(
    create_sheets_anaaccountentry(39, 1, '0.00', '0.00', '4510.78', '0.00',
                                  13))
loader.save(
    create_sheets_anaaccountentry(40, 1, '0.00', '0.00', '5113.78', '0.00',
                                  17))

loader.flush_deferred_objects()
