# -*- coding: UTF-8 -*-
logger.info("Loading 16 objects to table sheets_accountentry...")
# fields: id, report, old_d, old_c, during_d, during_c, account
loader.save(
    create_sheets_accountentry(17, 1, '0.00', '0.00', '23138.96', '18623.67',
                               2))
loader.save(
    create_sheets_accountentry(18, 1, '0.00', '0.00', '7980.00', '22044.44',
                               3))
loader.save(
    create_sheets_accountentry(19, 1, '0.00', '0.00', '22044.44', '27556.94',
                               4))
loader.save(
    create_sheets_accountentry(20, 1, '0.00', '0.00', '178.24', '297.46', 7))
loader.save(
    create_sheets_accountentry(21, 1, '0.00', '0.00', '0.00', '178.24', 6))
loader.save(
    create_sheets_accountentry(22, 1, '0.00', '0.00', '0.00', '10634.71', 12))
loader.save(
    create_sheets_accountentry(23, 1, '0.00', '0.00', '17620.40', '0.00', 15))
loader.save(
    create_sheets_accountentry(24, 1, '0.00', '0.00', '3520.00', '0.00', 16))
loader.save(
    create_sheets_accountentry(25, 1, '0.00', '0.00', '6714.00', '0.00', 14))
loader.save(
    create_sheets_accountentry(26, 1, '0.00', '0.00', '480.00', '3360.00', 19))
loader.save(
    create_sheets_accountentry(27, 1, '0.00', '0.00', '0.00', '20250.00', 27))
loader.save(
    create_sheets_accountentry(28, 1, '0.00', '0.00', '53341.64', '68700.75',
                               21))
loader.save(
    create_sheets_accountentry(29, 1, '0.00', '0.00', '0.00', '10634.71', 22))
loader.save(
    create_sheets_accountentry(30, 1, '0.00', '0.00', '27854.40', '0.00', 23))
loader.save(
    create_sheets_accountentry(31, 1, '0.00', '0.00', '27854.40', '0.00', 24))
loader.save(
    create_sheets_accountentry(32, 1, '0.00', '0.00', '480.00', '23610.00',
                               26))

loader.flush_deferred_objects()
