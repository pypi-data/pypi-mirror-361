# -*- coding: UTF-8 -*-
logger.info("Loading 15 objects to table sheets_itementry...")
# fields: id, report, old_d, old_c, during_d, during_c, item
loader.save(
    create_sheets_itementry(16, 1, '0.00', '0.00', '23138.96', '18623.67', 3))
loader.save(
    create_sheets_itementry(17, 1, '0.00', '0.00', '22044.44', '27556.94', 11))
loader.save(
    create_sheets_itementry(18, 1, '0.00', '0.00', '178.24', '475.70', 12))
loader.save(
    create_sheets_itementry(19, 1, '0.00', '0.00', '0.00', '10634.71', 13))
loader.save(
    create_sheets_itementry(20, 1, '0.00', '0.00', '7980.00', '22044.44', 14))
loader.save(
    create_sheets_itementry(21, 1, '0.00', '0.00', '6714.00', '0.00', 19))
loader.save(
    create_sheets_itementry(22, 1, '0.00', '0.00', '17620.40', '0.00', 20))
loader.save(
    create_sheets_itementry(23, 1, '0.00', '0.00', '3520.00', '0.00', 21))
loader.save(
    create_sheets_itementry(24, 1, '0.00', '0.00', '480.00', '23610.00', 24))
loader.save(
    create_sheets_itementry(25, 1, '0.00', '0.00', '23138.96', '18623.67', 1))
loader.save(
    create_sheets_itementry(26, 1, '0.00', '0.00', '23138.96', '18623.67', 2))
loader.save(
    create_sheets_itementry(27, 1, '0.00', '0.00', '30202.68', '60711.79', 9))
loader.save(
    create_sheets_itementry(28, 1, '0.00', '0.00', '30202.68', '60711.79', 10))
loader.save(
    create_sheets_itementry(29, 1, '0.00', '0.00', '27854.40', '0.00', 18))
loader.save(
    create_sheets_itementry(30, 1, '0.00', '0.00', '480.00', '23610.00', 23))

loader.flush_deferred_objects()
