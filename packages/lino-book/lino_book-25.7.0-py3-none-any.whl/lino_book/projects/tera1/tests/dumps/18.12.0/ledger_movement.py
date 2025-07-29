# -*- coding: UTF-8 -*-
logger.info("Loading 478 objects to table ledger_movement...")
# fields: id, voucher, partner, seqno, account, amount, dc, match, cleared, value_date, vat_regime, vat_class, ana_account
loader.save(
    create_ledger_movement(1, 1, None, 1, 27, '450.00', True, u'', True,
                           date(2015, 1, 7), u'10', u'2', None))
loader.save(
    create_ledger_movement(2, 1, 101, 2, 2, '450.00', False, u'SLS 1/2015',
                           True, date(2015, 1, 7), None, None, None))
loader.save(
    create_ledger_movement(3, 2, None, 1, 27, '600.00', True, u'', True,
                           date(2015, 1, 8), u'10', u'2', None))
loader.save(
    create_ledger_movement(4, 2, None, 2, 19, '280.00', True, u'', True,
                           date(2015, 1, 8), u'10', u'2', None))
loader.save(
    create_ledger_movement(5, 2, 102, 3, 2, '880.00', False, u'SLS 2/2015',
                           True, date(2015, 1, 8), None, None, None))
loader.save(
    create_ledger_movement(6, 3, None, 1, 27, '1050.00', True, u'', True,
                           date(2015, 1, 9), u'20', u'2', None))
loader.save(
    create_ledger_movement(7, 3, 103, 2, 2, '1050.00', False, u'SLS 3/2015',
                           True, date(2015, 1, 9), None, None, None))
loader.save(
    create_ledger_movement(8, 4, None, 1, 19, '280.00', True, u'', True,
                           date(2015, 1, 10), u'10', u'2', None))
loader.save(
    create_ledger_movement(9, 4, 104, 2, 2, '280.00', False, u'SLS 4/2015',
                           True, date(2015, 1, 10), None, None, None))
loader.save(
    create_ledger_movement(10, 5, None, 1, 27, '450.00', True, u'', True,
                           date(2015, 1, 11), u'20', u'2', None))
loader.save(
    create_ledger_movement(11, 5, 105, 2, 2, '450.00', False, u'SLS 5/2015',
                           True, date(2015, 1, 11), None, None, None))
loader.save(
    create_ledger_movement(12, 6, None, 1, 27, '600.00', True, u'', True,
                           date(2015, 2, 7), u'30', u'2', None))
loader.save(
    create_ledger_movement(13, 6, None, 2, 19, '280.00', True, u'', True,
                           date(2015, 2, 7), u'30', u'2', None))
loader.save(
    create_ledger_movement(14, 6, 106, 3, 2, '880.00', False, u'SLS 6/2015',
                           True, date(2015, 2, 7), None, None, None))
loader.save(
    create_ledger_movement(15, 7, None, 1, 27, '450.00', True, u'', True,
                           date(2015, 2, 8), u'35', u'2', None))
loader.save(
    create_ledger_movement(16, 7, 107, 2, 2, '450.00', False, u'SLS 7/2015',
                           True, date(2015, 2, 8), None, None, None))
loader.save(
    create_ledger_movement(17, 8, None, 1, 27, '600.00', True, u'', True,
                           date(2015, 2, 9), u'10', u'2', None))
loader.save(
    create_ledger_movement(18, 8, None, 2, 19, '280.00', True, u'', True,
                           date(2015, 2, 9), u'10', u'2', None))
loader.save(
    create_ledger_movement(19, 8, 108, 3, 2, '880.00', False, u'SLS 8/2015',
                           True, date(2015, 2, 9), None, None, None))
loader.save(
    create_ledger_movement(20, 9, None, 1, 27, '1050.00', True, u'', True,
                           date(2015, 2, 10), u'30', u'2', None))
loader.save(
    create_ledger_movement(21, 9, 109, 2, 2, '1050.00', False, u'SLS 9/2015',
                           True, date(2015, 2, 10), None, None, None))
loader.save(
    create_ledger_movement(22, 10, None, 1, 19, '280.00', True, u'', True,
                           date(2015, 3, 7), u'35', u'2', None))
loader.save(
    create_ledger_movement(23, 10, 110, 2, 2, '280.00', False, u'SLS 10/2015',
                           True, date(2015, 3, 7), None, None, None))
loader.save(
    create_ledger_movement(24, 11, None, 1, 27, '450.00', True, u'', True,
                           date(2015, 4, 7), u'10', u'2', None))
loader.save(
    create_ledger_movement(25, 11, 111, 2, 2, '450.00', False, u'SLS 11/2015',
                           True, date(2015, 4, 7), None, None, None))
loader.save(
    create_ledger_movement(26, 12, None, 1, 27, '600.00', True, u'', True,
                           date(2015, 4, 8), u'30', u'2', None))
loader.save(
    create_ledger_movement(27, 12, None, 2, 19, '280.00', True, u'', True,
                           date(2015, 4, 8), u'30', u'2', None))
loader.save(
    create_ledger_movement(28, 12, 112, 3, 2, '880.00', False, u'SLS 12/2015',
                           True, date(2015, 4, 8), None, None, None))
loader.save(
    create_ledger_movement(29, 13, None, 1, 27, '450.00', True, u'', True,
                           date(2015, 4, 9), u'10', u'2', None))
loader.save(
    create_ledger_movement(30, 13, 113, 2, 2, '450.00', False, u'SLS 13/2015',
                           False, date(2015, 4, 9), None, None, None))
loader.save(
    create_ledger_movement(31, 14, None, 1, 27, '600.00', True, u'', True,
                           date(2015, 4, 10), u'20', u'2', None))
loader.save(
    create_ledger_movement(32, 14, None, 2, 19, '280.00', True, u'', True,
                           date(2015, 4, 10), u'20', u'2', None))
loader.save(
    create_ledger_movement(33, 14, 114, 3, 2, '880.00', False, u'SLS 14/2015',
                           True, date(2015, 4, 10), None, None, None))
loader.save(
    create_ledger_movement(34, 15, None, 1, 27, '1050.00', True, u'', True,
                           date(2015, 4, 11), u'10', u'2', None))
loader.save(
    create_ledger_movement(35, 15, 115, 2, 2, '1050.00', False, u'SLS 15/2015',
                           True, date(2015, 4, 11), None, None, None))
loader.save(
    create_ledger_movement(36, 16, None, 1, 19, '280.00', True, u'', True,
                           date(2015, 4, 12), u'10', u'2', None))
loader.save(
    create_ledger_movement(37, 16, 115, 2, 2, '280.00', False, u'SLS 16/2015',
                           False, date(2015, 4, 12), None, None, None))
loader.save(
    create_ledger_movement(38, 17, None, 1, 27, '450.00', True, u'', True,
                           date(2015, 4, 13), u'20', u'2', None))
loader.save(
    create_ledger_movement(39, 17, 116, 2, 2, '450.00', False, u'SLS 17/2015',
                           False, date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(40, 18, None, 1, 27, '600.00', True, u'', True,
                           date(2015, 4, 14), u'10', u'2', None))
loader.save(
    create_ledger_movement(41, 18, None, 2, 19, '280.00', True, u'', True,
                           date(2015, 4, 14), u'10', u'2', None))
loader.save(
    create_ledger_movement(42, 18, 117, 3, 2, '880.00', False, u'SLS 18/2015',
                           True, date(2015, 4, 14), None, None, None))
loader.save(
    create_ledger_movement(43, 19, None, 1, 27, '450.00', True, u'', True,
                           date(2015, 5, 7), u'20', u'2', None))
loader.save(
    create_ledger_movement(44, 19, 118, 2, 2, '450.00', False, u'SLS 19/2015',
                           False, date(2015, 5, 7), None, None, None))
loader.save(
    create_ledger_movement(45, 20, None, 1, 27, '600.00', True, u'', True,
                           date(2015, 5, 8), u'10', u'2', None))
loader.save(
    create_ledger_movement(46, 20, None, 2, 19, '280.00', True, u'', True,
                           date(2015, 5, 8), u'10', u'2', None))
loader.save(
    create_ledger_movement(47, 20, 119, 3, 2, '880.00', False, u'SLS 20/2015',
                           False, date(2015, 5, 8), None, None, None))
loader.save(
    create_ledger_movement(48, 21, None, 1, 27, '1050.00', True, u'', True,
                           date(2015, 5, 9), u'20', u'2', None))
loader.save(
    create_ledger_movement(49, 21, 120, 2, 2, '1050.00', False, u'SLS 21/2015',
                           False, date(2015, 5, 9), None, None, None))
loader.save(
    create_ledger_movement(50, 22, None, 1, 19, '280.00', True, u'', True,
                           date(2015, 5, 10), u'10', u'2', None))
loader.save(
    create_ledger_movement(51, 22, 121, 2, 2, '280.00', False, u'SLS 22/2015',
                           False, date(2015, 5, 10), None, None, None))
loader.save(
    create_ledger_movement(52, 23, None, 1, 27, '450.00', True, u'', True,
                           date(2015, 5, 11), u'20', u'2', None))
loader.save(
    create_ledger_movement(53, 23, 122, 2, 2, '450.00', False, u'SLS 23/2015',
                           False, date(2015, 5, 11), None, None, None))
loader.save(
    create_ledger_movement(54, 24, None, 1, 27, '600.00', True, u'', True,
                           date(2015, 5, 12), u'20', u'2', None))
loader.save(
    create_ledger_movement(55, 24, None, 2, 19, '280.00', True, u'', True,
                           date(2015, 5, 12), u'20', u'2', None))
loader.save(
    create_ledger_movement(56, 24, 122, 3, 2, '880.00', False, u'SLS 24/2015',
                           False, date(2015, 5, 12), None, None, None))
loader.save(
    create_ledger_movement(57, 25, None, 1, 27, '480.00', True, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(58, 25, None, 2, 19, '75.00', False, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(59, 25, 113, 3, 2, '405.00', False, u'SLS 25/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(60, 26, None, 1, 27, '390.00', True, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(61, 26, None, 2, 19, '40.00', False, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(62, 26, 114, 3, 2, '350.00', False, u'SLS 26/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(63, 27, None, 1, 27, '270.00', True, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(64, 27, 122, 2, 2, '270.00', False, u'SLS 27/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(65, 28, None, 1, 27, '360.00', True, u'', True,
                           date(2015, 1, 1), u'30', u'2', None))
loader.save(
    create_ledger_movement(66, 28, 180, 2, 2, '360.00', False, u'SLS 28/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(67, 29, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(68, 29, 150, 2, 2, '120.00', False, u'SLS 29/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(69, 30, None, 1, 27, '90.00', True, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(70, 30, 151, 2, 2, '90.00', False, u'SLS 30/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(71, 31, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(72, 31, None, 2, 19, '35.00', False, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(73, 31, 132, 3, 2, '85.00', False, u'SLS 31/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(74, 32, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(75, 32, 134, 2, 2, '60.00', False, u'SLS 32/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(76, 33, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(77, 33, None, 2, 19, '5.00', False, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(78, 33, 139, 3, 2, '115.00', False, u'SLS 33/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(79, 34, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(80, 34, 141, 2, 2, '60.00', False, u'SLS 34/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(81, 35, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(82, 35, 146, 2, 2, '120.00', False, u'SLS 35/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(83, 36, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 1, 1), u'35', u'2', None))
loader.save(
    create_ledger_movement(84, 36, 172, 2, 2, '60.00', False, u'SLS 36/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(85, 37, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(86, 37, None, 2, 19, '20.00', False, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(87, 37, 156, 3, 2, '100.00', False, u'SLS 37/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(88, 38, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(89, 38, 157, 2, 2, '60.00', False, u'SLS 38/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(90, 39, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(91, 39, None, 2, 19, '5.00', False, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(92, 39, 173, 3, 2, '115.00', False, u'SLS 39/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(93, 40, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(94, 40, 165, 2, 2, '60.00', False, u'SLS 40/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(95, 41, None, 1, 27, '300.00', True, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(96, 41, None, 2, 19, '40.00', False, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(97, 41, 115, 3, 2, '260.00', False, u'SLS 41/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(98, 42, None, 1, 27, '300.00', True, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(99, 42, None, 2, 19, '40.00', False, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(100, 42, 116, 3, 2, '260.00', False, u'SLS 42/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(101, 43, None, 1, 27, '300.00', True, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(102, 43, None, 2, 19, '40.00', False, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(103, 43, 117, 3, 2, '260.00', False, u'SLS 43/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(104, 44, None, 1, 27, '150.00', True, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(105, 44, 120, 2, 2, '150.00', False, u'SLS 44/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(106, 45, None, 1, 27, '150.00', True, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(107, 45, 119, 2, 2, '150.00', False, u'SLS 45/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(108, 46, None, 1, 27, '150.00', True, u'', True,
                           date(2015, 1, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(109, 46, 118, 2, 2, '150.00', False, u'SLS 46/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(110, 47, None, 1, 27, '150.00', True, u'', True,
                           date(2015, 1, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(111, 47, 123, 2, 2, '150.00', False, u'SLS 47/2015',
                           True, date(2015, 1, 1), None, None, None))
loader.save(
    create_ledger_movement(112, 48, None, 1, 27, '180.00', True, u'', True,
                           date(2015, 2, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(113, 48, 113, 2, 2, '180.00', False, u'SLS 48/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(114, 49, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(115, 49, 114, 2, 2, '120.00', False, u'SLS 49/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(116, 50, None, 1, 27, '150.00', True, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(117, 50, None, 2, 19, '5.00', False, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(118, 50, 122, 3, 2, '145.00', False, u'SLS 50/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(119, 51, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 2, 1), u'30', u'2', None))
loader.save(
    create_ledger_movement(120, 51, 180, 2, 2, '120.00', False, u'SLS 51/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(121, 52, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(122, 52, None, 2, 19, '35.00', False, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(123, 52, 150, 3, 2, '85.00', False, u'SLS 52/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(124, 53, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 2, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(125, 53, 151, 2, 2, '60.00', False, u'SLS 53/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(126, 54, None, 1, 27, '180.00', True, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(127, 54, None, 2, 19, '5.00', False, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(128, 54, 132, 3, 2, '175.00', False, u'SLS 54/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(129, 55, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(130, 55, 134, 2, 2, '60.00', False, u'SLS 55/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(131, 56, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 2, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(132, 56, 139, 2, 2, '120.00', False, u'SLS 56/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(133, 57, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 2, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(134, 57, 141, 2, 2, '60.00', False, u'SLS 57/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(135, 58, None, 1, 27, '180.00', True, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(136, 58, None, 2, 19, '35.00', False, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(137, 58, 146, 3, 2, '145.00', False, u'SLS 58/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(138, 59, None, 1, 27, '90.00', True, u'', True,
                           date(2015, 2, 1), u'35', u'2', None))
loader.save(
    create_ledger_movement(139, 59, 172, 2, 2, '90.00', False, u'SLS 59/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(140, 60, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(141, 60, None, 2, 19, '5.00', False, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(142, 60, 156, 3, 2, '115.00', False, u'SLS 60/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(143, 61, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 2, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(144, 61, 157, 2, 2, '60.00', False, u'SLS 61/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(145, 62, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 2, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(146, 62, None, 2, 19, '15.00', False, u'', True,
                           date(2015, 2, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(147, 62, 173, 3, 2, '105.00', False, u'SLS 62/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(148, 63, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 2, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(149, 63, 165, 2, 2, '60.00', False, u'SLS 63/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(150, 64, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 2, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(151, 64, 115, 2, 2, '60.00', False, u'SLS 64/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(152, 65, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(153, 65, 116, 2, 2, '60.00', False, u'SLS 65/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(154, 66, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 2, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(155, 66, 117, 2, 2, '60.00', False, u'SLS 66/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(156, 67, None, 1, 27, '30.00', True, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(157, 67, 120, 2, 2, '30.00', False, u'SLS 67/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(158, 68, None, 1, 27, '30.00', True, u'', True,
                           date(2015, 2, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(159, 68, 119, 2, 2, '30.00', False, u'SLS 68/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(160, 69, None, 1, 27, '30.00', True, u'', True,
                           date(2015, 2, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(161, 69, 118, 2, 2, '30.00', False, u'SLS 69/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(162, 70, None, 1, 27, '30.00', True, u'', True,
                           date(2015, 2, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(163, 70, 123, 2, 2, '30.00', False, u'SLS 70/2015',
                           True, date(2015, 2, 1), None, None, None))
loader.save(
    create_ledger_movement(164, 71, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 3, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(165, 71, None, 2, 19, '5.00', False, u'', True,
                           date(2015, 3, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(166, 71, 113, 3, 2, '115.00', False, u'SLS 71/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(167, 72, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 3, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(168, 72, 114, 2, 2, '60.00', False, u'SLS 72/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(169, 73, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 3, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(170, 73, None, 2, 19, '15.00', False, u'', True,
                           date(2015, 3, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(171, 73, 122, 3, 2, '105.00', False, u'SLS 73/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(172, 74, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 3, 1), u'30', u'2', None))
loader.save(
    create_ledger_movement(173, 74, 180, 2, 2, '60.00', False, u'SLS 74/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(174, 75, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 3, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(175, 75, 150, 2, 2, '120.00', False, u'SLS 75/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(176, 76, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 3, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(177, 76, 151, 2, 2, '60.00', False, u'SLS 76/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(178, 77, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 3, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(179, 77, 132, 2, 2, '120.00', False, u'SLS 77/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(180, 78, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 3, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(181, 78, 134, 2, 2, '60.00', False, u'SLS 78/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(182, 79, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 3, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(183, 79, None, 2, 19, '35.00', False, u'', True,
                           date(2015, 3, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(184, 79, 139, 3, 2, '85.00', False, u'SLS 79/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(185, 80, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 3, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(186, 80, 141, 2, 2, '60.00', False, u'SLS 80/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(187, 81, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 3, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(188, 81, None, 2, 19, '5.00', False, u'', True,
                           date(2015, 3, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(189, 81, 146, 3, 2, '115.00', False, u'SLS 81/2015',
                           False, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(190, 82, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 3, 1), u'35', u'2', None))
loader.save(
    create_ledger_movement(191, 82, 172, 2, 2, '60.00', False, u'SLS 82/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(192, 83, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 3, 1), u'20', u'2', None))
loader.save(
    create_ledger_movement(193, 83, 156, 2, 2, '120.00', False, u'SLS 83/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(194, 84, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 3, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(195, 84, 157, 2, 2, '60.00', False, u'SLS 84/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(196, 85, None, 1, 27, '120.00', True, u'', True,
                           date(2015, 3, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(197, 85, None, 2, 19, '20.00', False, u'', True,
                           date(2015, 3, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(198, 85, 173, 3, 2, '100.00', False, u'SLS 85/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(199, 86, None, 1, 27, '60.00', True, u'', True,
                           date(2015, 3, 1), u'10', u'2', None))
loader.save(
    create_ledger_movement(200, 86, 165, 2, 2, '60.00', False, u'SLS 86/2015',
                           True, date(2015, 3, 1), None, None, None))
loader.save(
    create_ledger_movement(201, 87, None, 1, 15, '40.00', False, u'', True,
                           date(2015, 1, 3), u'10', u'2', 2))
loader.save(
    create_ledger_movement(202, 87, 101, 2, 4, '40.00', True, u'PRC 1/2015',
                           True, date(2015, 1, 3), None, None, None))
loader.save(
    create_ledger_movement(203, 88, None, 1, 16, '60.40', False, u'', True,
                           date(2015, 1, 4), u'10', u'2', 3))
loader.save(
    create_ledger_movement(204, 88, None, 2, 14, '80.90', False, u'', True,
                           date(2015, 1, 4), u'10', u'2', 4))
loader.save(
    create_ledger_movement(205, 88, 102, 3, 4, '141.30', True, u'PRC 2/2015',
                           True, date(2015, 1, 4), None, None, None))
loader.save(
    create_ledger_movement(206, 89, None, 1, 15, '201.20', False, u'', True,
                           date(2015, 1, 5), u'20', u'2', 5))
loader.save(
    create_ledger_movement(207, 89, None, 2, 16, '402.40', False, u'', True,
                           date(2015, 1, 5), u'20', u'2', 7))
loader.save(
    create_ledger_movement(208, 89, 103, 3, 4, '603.60', True, u'PRC 3/2015',
                           True, date(2015, 1, 5), None, None, None))
loader.save(
    create_ledger_movement(209, 90, None, 1, 14, '1199.90', False, u'', True,
                           date(2015, 1, 6), u'10', u'2', 8))
loader.save(
    create_ledger_movement(210, 90, 104, 2, 4, '1199.90', True, u'PRC 4/2015',
                           True, date(2015, 1, 6), None, None, None))
loader.save(
    create_ledger_movement(211, 91, None, 1, 15, '3200.58', False, u'', True,
                           date(2015, 1, 7), u'20', u'2', 9))
loader.save(
    create_ledger_movement(212, 91, None, 2, 16, '41.10', False, u'', True,
                           date(2015, 1, 7), u'20', u'2', 10))
loader.save(
    create_ledger_movement(213, 91, 105, 3, 4, '3241.68', True, u'PRC 5/2015',
                           True, date(2015, 1, 7), None, None, None))
loader.save(
    create_ledger_movement(214, 92, None, 1, 14, '61.10', False, u'', True,
                           date(2015, 1, 8), u'30', u'2', 12))
loader.save(
    create_ledger_movement(215, 92, None, 2, 7, '24.88', True, u'', True,
                           date(2015, 1, 8), u'30', u'2', None))
loader.save(
    create_ledger_movement(216, 92, None, 3, 15, '82.30', False, u'', True,
                           date(2015, 1, 8), u'30', u'2', 14))
loader.save(
    create_ledger_movement(217, 92, 106, 4, 4, '118.52', True, u'PRC 6/2015',
                           True, date(2015, 1, 8), None, None, None))
loader.save(
    create_ledger_movement(218, 93, None, 1, 16, '199.90', False, u'', True,
                           date(2015, 1, 9), u'35', u'2', 15))
loader.save(
    create_ledger_movement(219, 93, None, 2, 7, '34.69', True, u'', True,
                           date(2015, 1, 9), u'35', u'2', None))
loader.save(
    create_ledger_movement(220, 93, 107, 3, 4, '165.21', True, u'PRC 7/2015',
                           True, date(2015, 1, 9), None, None, None))
loader.save(
    create_ledger_movement(221, 94, None, 1, 15, '40.60', False, u'', True,
                           date(2015, 2, 3), u'10', u'2', 16))
loader.save(
    create_ledger_movement(222, 94, 101, 2, 4, '40.60', True, u'PRC 8/2015',
                           True, date(2015, 2, 3), None, None, None))
loader.save(
    create_ledger_movement(223, 95, None, 1, 16, '60.90', False, u'', True,
                           date(2015, 2, 4), u'10', u'2', 18))
loader.save(
    create_ledger_movement(224, 95, None, 2, 14, '81.10', False, u'', True,
                           date(2015, 2, 4), u'10', u'2', 19))
loader.save(
    create_ledger_movement(225, 95, 102, 3, 4, '142.00', True, u'PRC 9/2015',
                           True, date(2015, 2, 4), None, None, None))
loader.save(
    create_ledger_movement(226, 96, None, 1, 15, '202.40', False, u'', True,
                           date(2015, 2, 5), u'20', u'2', 20))
loader.save(
    create_ledger_movement(227, 96, None, 2, 16, '399.90', False, u'', True,
                           date(2015, 2, 5), u'20', u'2', 2))
loader.save(
    create_ledger_movement(228, 96, 103, 3, 4, '602.30', True, u'PRC 10/2015',
                           True, date(2015, 2, 5), None, None, None))
loader.save(
    create_ledger_movement(229, 97, None, 1, 14, '1200.50', False, u'', True,
                           date(2015, 2, 6), u'10', u'2', 3))
loader.save(
    create_ledger_movement(230, 97, 104, 2, 4, '1200.50', True, u'PRC 11/2015',
                           True, date(2015, 2, 6), None, None, None))
loader.save(
    create_ledger_movement(231, 98, None, 1, 15, '3201.08', False, u'', True,
                           date(2015, 2, 7), u'20', u'2', 4))
loader.save(
    create_ledger_movement(232, 98, None, 2, 16, '41.30', False, u'', True,
                           date(2015, 2, 7), u'20', u'2', 5))
loader.save(
    create_ledger_movement(233, 98, 105, 3, 4, '3242.38', True, u'PRC 12/2015',
                           True, date(2015, 2, 7), None, None, None))
loader.save(
    create_ledger_movement(234, 99, None, 1, 14, '62.30', False, u'', True,
                           date(2015, 2, 8), u'30', u'2', 7))
loader.save(
    create_ledger_movement(235, 99, None, 2, 7, '24.66', True, u'', True,
                           date(2015, 2, 8), u'30', u'2', None))
loader.save(
    create_ledger_movement(236, 99, None, 3, 15, '79.80', False, u'', True,
                           date(2015, 2, 8), u'30', u'2', 8))
loader.save(
    create_ledger_movement(237, 99, 106, 4, 4, '117.44', True, u'PRC 13/2015',
                           True, date(2015, 2, 8), None, None, None))
loader.save(
    create_ledger_movement(238, 100, None, 1, 16, '200.50', False, u'', True,
                           date(2015, 2, 9), u'35', u'2', 9))
loader.save(
    create_ledger_movement(239, 100, None, 2, 7, '34.80', True, u'', True,
                           date(2015, 2, 9), u'35', u'2', None))
loader.save(
    create_ledger_movement(240, 100, 107, 3, 4, '165.70', True, u'PRC 14/2015',
                           True, date(2015, 2, 9), None, None, None))
loader.save(
    create_ledger_movement(241, 101, None, 1, 15, '41.10', False, u'', True,
                           date(2015, 3, 3), u'10', u'2', 10))
loader.save(
    create_ledger_movement(242, 101, 101, 2, 4, '41.10', True, u'PRC 15/2015',
                           True, date(2015, 3, 3), None, None, None))
loader.save(
    create_ledger_movement(243, 102, None, 1, 16, '61.10', False, u'', True,
                           date(2015, 3, 4), u'10', u'2', 12))
loader.save(
    create_ledger_movement(244, 102, None, 2, 14, '82.30', False, u'', True,
                           date(2015, 3, 4), u'10', u'2', 14))
loader.save(
    create_ledger_movement(245, 102, 102, 3, 4, '143.40', True, u'PRC 16/2015',
                           True, date(2015, 3, 4), None, None, None))
loader.save(
    create_ledger_movement(246, 103, None, 1, 15, '199.90', False, u'', True,
                           date(2015, 3, 5), u'20', u'2', 15))
loader.save(
    create_ledger_movement(247, 103, None, 2, 16, '400.50', False, u'', True,
                           date(2015, 3, 5), u'20', u'2', 16))
loader.save(
    create_ledger_movement(248, 103, 103, 3, 4, '600.40', True, u'PRC 17/2015',
                           True, date(2015, 3, 5), None, None, None))
loader.save(
    create_ledger_movement(249, 104, None, 1, 14, '1201.00', False, u'', True,
                           date(2015, 3, 6), u'10', u'2', 18))
loader.save(
    create_ledger_movement(250, 104, 104, 2, 4,
                           '1201.00', True, u'PRC 18/2015', True,
                           date(2015, 3, 6), None, None, None))
loader.save(
    create_ledger_movement(251, 105, None, 1, 15, '3201.28', False, u'', True,
                           date(2015, 3, 7), u'20', u'2', 19))
loader.save(
    create_ledger_movement(252, 105, None, 2, 16, '42.50', False, u'', True,
                           date(2015, 3, 7), u'20', u'2', 20))
loader.save(
    create_ledger_movement(253, 105, 105, 3, 4,
                           '3243.78', True, u'PRC 19/2015', True,
                           date(2015, 3, 7), None, None, None))
loader.save(
    create_ledger_movement(254, 106, None, 1, 14, '59.80', False, u'', True,
                           date(2015, 3, 8), u'30', u'2', 2))
loader.save(
    create_ledger_movement(255, 106, None, 2, 7, '24.33', True, u'', True,
                           date(2015, 3, 8), u'30', u'2', None))
loader.save(
    create_ledger_movement(256, 106, None, 3, 15, '80.40', False, u'', True,
                           date(2015, 3, 8), u'30', u'2', 3))
loader.save(
    create_ledger_movement(257, 106, 106, 4, 4, '115.87', True, u'PRC 20/2015',
                           True, date(2015, 3, 8), None, None, None))
loader.save(
    create_ledger_movement(258, 107, None, 1, 16, '201.00', False, u'', True,
                           date(2015, 3, 9), u'35', u'2', 4))
loader.save(
    create_ledger_movement(259, 107, None, 2, 7, '34.88', True, u'', True,
                           date(2015, 3, 9), u'35', u'2', None))
loader.save(
    create_ledger_movement(260, 107, 107, 3, 4, '166.12', True, u'PRC 21/2015',
                           True, date(2015, 3, 9), None, None, None))
loader.save(
    create_ledger_movement(261, 108, None, 1, 15, '41.30', False, u'', True,
                           date(2015, 4, 3), u'10', u'2', 5))
loader.save(
    create_ledger_movement(262, 108, 101, 2, 4, '41.30', True, u'PRC 22/2015',
                           True, date(2015, 4, 3), None, None, None))
loader.save(
    create_ledger_movement(263, 109, None, 1, 16, '62.30', False, u'', True,
                           date(2015, 4, 4), u'10', u'2', 7))
loader.save(
    create_ledger_movement(264, 109, None, 2, 14, '79.80', False, u'', True,
                           date(2015, 4, 4), u'10', u'2', 8))
loader.save(
    create_ledger_movement(265, 109, 102, 3, 4, '142.10', True, u'PRC 23/2015',
                           True, date(2015, 4, 4), None, None, None))
loader.save(
    create_ledger_movement(266, 110, None, 1, 15, '200.50', False, u'', True,
                           date(2015, 4, 5), u'20', u'2', 9))
loader.save(
    create_ledger_movement(267, 110, None, 2, 16, '401.00', False, u'', True,
                           date(2015, 4, 5), u'20', u'2', 10))
loader.save(
    create_ledger_movement(268, 110, 103, 3, 4, '601.50', True, u'PRC 24/2015',
                           True, date(2015, 4, 5), None, None, None))
loader.save(
    create_ledger_movement(269, 111, None, 1, 14, '1201.20', False, u'', True,
                           date(2015, 4, 6), u'10', u'2', 12))
loader.save(
    create_ledger_movement(270, 111, 104, 2, 4,
                           '1201.20', True, u'PRC 25/2015', True,
                           date(2015, 4, 6), None, None, None))
loader.save(
    create_ledger_movement(271, 112, None, 1, 15, '3202.48', False, u'', True,
                           date(2015, 4, 7), u'20', u'2', 14))
loader.save(
    create_ledger_movement(272, 112, None, 2, 16, '40.00', False, u'', True,
                           date(2015, 4, 7), u'20', u'2', 15))
loader.save(
    create_ledger_movement(273, 112, 105, 3, 4,
                           '3242.48', True, u'PRC 26/2015', True,
                           date(2015, 4, 7), None, None, None))
loader.save(
    create_ledger_movement(274, 113, None, 1, 14, '60.40', False, u'', True,
                           date(2015, 4, 8), u'30', u'2', 16))
loader.save(
    create_ledger_movement(275, 113, None, 2, 7, '24.52', True, u'', True,
                           date(2015, 4, 8), u'30', u'2', None))
loader.save(
    create_ledger_movement(276, 113, None, 3, 15, '80.90', False, u'', True,
                           date(2015, 4, 8), u'30', u'2', 18))
loader.save(
    create_ledger_movement(277, 113, 106, 4, 4, '116.78', True, u'PRC 27/2015',
                           True, date(2015, 4, 8), None, None, None))
loader.save(
    create_ledger_movement(278, 114, None, 1, 16, '201.20', False, u'', True,
                           date(2015, 4, 9), u'35', u'2', 19))
loader.save(
    create_ledger_movement(279, 114, None, 2, 7, '34.92', True, u'', True,
                           date(2015, 4, 9), u'35', u'2', None))
loader.save(
    create_ledger_movement(280, 114, 107, 3, 4, '166.28', True, u'PRC 28/2015',
                           True, date(2015, 4, 9), None, None, None))
loader.save(
    create_ledger_movement(281, 115, None, 1, 15, '42.50', False, u'', True,
                           date(2015, 5, 3), u'10', u'2', 20))
loader.save(
    create_ledger_movement(282, 115, 101, 2, 4, '42.50', True, u'PRC 29/2015',
                           False, date(2015, 5, 3), None, None, None))
loader.save(
    create_ledger_movement(283, 116, None, 1, 16, '59.80', False, u'', True,
                           date(2015, 5, 4), u'10', u'2', 2))
loader.save(
    create_ledger_movement(284, 116, None, 2, 14, '80.40', False, u'', True,
                           date(2015, 5, 4), u'10', u'2', 3))
loader.save(
    create_ledger_movement(285, 116, 102, 3, 4, '140.20', True, u'PRC 30/2015',
                           False, date(2015, 5, 4), None, None, None))
loader.save(
    create_ledger_movement(286, 117, None, 1, 15, '201.00', False, u'', True,
                           date(2015, 5, 5), u'20', u'2', 4))
loader.save(
    create_ledger_movement(287, 117, None, 2, 16, '401.20', False, u'', True,
                           date(2015, 5, 5), u'20', u'2', 5))
loader.save(
    create_ledger_movement(288, 117, 103, 3, 4, '602.20', True, u'PRC 31/2015',
                           False, date(2015, 5, 5), None, None, None))
loader.save(
    create_ledger_movement(289, 118, None, 1, 14, '1202.40', False, u'', True,
                           date(2015, 5, 6), u'10', u'2', 7))
loader.save(
    create_ledger_movement(290, 118, 104, 2, 4,
                           '1202.40', True, u'PRC 32/2015', False,
                           date(2015, 5, 6), None, None, None))
loader.save(
    create_ledger_movement(291, 119, None, 1, 15, '3199.98', False, u'', True,
                           date(2015, 5, 7), u'20', u'2', 8))
loader.save(
    create_ledger_movement(292, 119, None, 2, 16, '40.60', False, u'', True,
                           date(2015, 5, 7), u'20', u'2', 9))
loader.save(
    create_ledger_movement(293, 119, 105, 3, 4,
                           '3240.58', True, u'PRC 33/2015', False,
                           date(2015, 5, 7), None, None, None))
loader.save(
    create_ledger_movement(294, 120, None, 1, 14, '60.90', False, u'', True,
                           date(2015, 5, 8), u'30', u'2', 10))
loader.save(
    create_ledger_movement(295, 120, None, 2, 7, '24.65', True, u'', True,
                           date(2015, 5, 8), u'30', u'2', None))
loader.save(
    create_ledger_movement(296, 120, None, 3, 15, '81.10', False, u'', True,
                           date(2015, 5, 8), u'30', u'2', 12))
loader.save(
    create_ledger_movement(297, 120, 106, 4, 4, '117.35', True, u'PRC 34/2015',
                           False, date(2015, 5, 8), None, None, None))
loader.save(
    create_ledger_movement(298, 121, None, 1, 16, '202.40', False, u'', True,
                           date(2015, 5, 9), u'35', u'2', 14))
loader.save(
    create_ledger_movement(299, 121, None, 2, 7, '35.13', True, u'', True,
                           date(2015, 5, 9), u'35', u'2', None))
loader.save(
    create_ledger_movement(300, 121, 107, 3, 4, '167.27', True, u'PRC 35/2015',
                           False, date(2015, 5, 9), None, None, None))
loader.save(
    create_ledger_movement(301, 122, None, 1, 7, '24.88', False, u'', True,
                           date(2015, 1, 31), u'30', u'2', None))
loader.save(
    create_ledger_movement(302, 122, None, 2, 7, '34.69', False, u'', True,
                           date(2015, 1, 31), u'35', u'2', None))
loader.save(
    create_ledger_movement(303, 122, 199, 3, 6, '59.57', True, u'VAT 1/2015',
                           False, date(2015, 1, 31), None, None, None))
loader.save(
    create_ledger_movement(304, 123, None, 1, 7, '24.66', False, u'', True,
                           date(2015, 2, 28), u'30', u'2', None))
loader.save(
    create_ledger_movement(305, 123, None, 2, 7, '34.80', False, u'', True,
                           date(2015, 2, 28), u'35', u'2', None))
loader.save(
    create_ledger_movement(306, 123, 199, 3, 6, '59.46', True, u'VAT 2/2015',
                           False, date(2015, 2, 28), None, None, None))
loader.save(
    create_ledger_movement(307, 124, None, 1, 7, '24.33', False, u'', True,
                           date(2015, 3, 28), u'30', u'2', None))
loader.save(
    create_ledger_movement(308, 124, None, 2, 7, '34.88', False, u'', True,
                           date(2015, 3, 28), u'35', u'2', None))
loader.save(
    create_ledger_movement(309, 124, 199, 3, 6, '59.21', True, u'VAT 3/2015',
                           False, date(2015, 3, 28), None, None, None))
loader.save(
    create_ledger_movement(310, 125, 101, 1, 4, '40.00', False, u'PRC 1/2015',
                           True, date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(311, 125, 101, 2, 3, '40.00', True, u'PRC 1/2015',
                           False, date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(312, 125, 102, 3, 4, '141.30', False, u'PRC 2/2015',
                           True, date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(313, 125, 102, 4, 3, '141.30', True, u'PRC 2/2015',
                           False, date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(314, 125, 103, 5, 4, '603.60', False, u'PRC 3/2015',
                           True, date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(315, 125, 103, 6, 3, '603.60', True, u'PRC 3/2015',
                           False, date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(316, 125, 104, 7, 4,
                           '1199.90', False, u'PRC 4/2015', True,
                           date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(317, 125, 104, 8, 3, '1199.90', True, u'PRC 4/2015',
                           False, date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(318, 125, 101, 9, 2, '450.00', True, u'SLS 1/2015',
                           True, date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(319, 125, 101, 10, 3,
                           '450.00', False, u'SLS 1/2015', False,
                           date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(320, 125, 105, 11, 4,
                           '3241.68', False, u'PRC 5/2015', True,
                           date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(321, 125, 105, 12, 3,
                           '3241.68', True, u'PRC 5/2015', False,
                           date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(322, 125, 102, 13, 2, '880.00', True, u'SLS 2/2015',
                           True, date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(323, 125, 102, 14, 3,
                           '880.00', False, u'SLS 2/2015', False,
                           date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(324, 125, 106, 15, 4,
                           '118.52', False, u'PRC 6/2015', True,
                           date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(325, 125, 106, 16, 3, '118.52', True, u'PRC 6/2015',
                           False, date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(326, 125, 103, 17, 2,
                           '1050.00', True, u'SLS 3/2015', True,
                           date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(327, 125, 103, 18, 3,
                           '1050.00', False, u'SLS 3/2015', False,
                           date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(328, 125, 107, 19, 4,
                           '165.21', False, u'PRC 7/2015', True,
                           date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(329, 125, 107, 20, 3, '165.21', True, u'PRC 7/2015',
                           False, date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(330, 125, 104, 21, 2, '280.00', True, u'SLS 4/2015',
                           True, date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(331, 125, 104, 22, 3,
                           '280.00', False, u'SLS 4/2015', False,
                           date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(332, 125, 105, 23, 2, '450.00', True, u'SLS 5/2015',
                           True, date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(333, 125, 105, 24, 3,
                           '450.00', False, u'SLS 5/2015', False,
                           date(2015, 1, 13), None, None, None))
loader.save(
    create_ledger_movement(334, 126, 101, 1, 4, '40.60', False, u'PRC 8/2015',
                           True, date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(335, 126, 101, 2, 3, '40.60', True, u'PRC 8/2015',
                           False, date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(336, 126, 102, 3, 4, '142.00', False, u'PRC 9/2015',
                           True, date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(337, 126, 102, 4, 3, '142.00', True, u'PRC 9/2015',
                           False, date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(338, 126, 103, 5, 4,
                           '602.30', False, u'PRC 10/2015', True,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(339, 126, 103, 6, 3, '602.30', True, u'PRC 10/2015',
                           False, date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(340, 126, 104, 7, 4,
                           '1200.50', False, u'PRC 11/2015', True,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(341, 126, 104, 8, 3,
                           '1200.50', True, u'PRC 11/2015', False,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(342, 126, 106, 9, 2, '880.00', True, u'SLS 6/2015',
                           True, date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(343, 126, 106, 10, 3,
                           '880.00', False, u'SLS 6/2015', False,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(344, 126, 105, 11, 4,
                           '3242.38', False, u'PRC 12/2015', True,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(345, 126, 105, 12, 3,
                           '3242.38', True, u'PRC 12/2015', False,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(346, 126, 107, 13, 2, '450.00', True, u'SLS 7/2015',
                           True, date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(347, 126, 107, 14, 3,
                           '450.00', False, u'SLS 7/2015', False,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(348, 126, 106, 15, 4,
                           '117.44', False, u'PRC 13/2015', True,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(349, 126, 106, 16, 3,
                           '117.44', True, u'PRC 13/2015', False,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(350, 126, 108, 17, 2, '880.00', True, u'SLS 8/2015',
                           True, date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(351, 126, 108, 18, 3,
                           '880.00', False, u'SLS 8/2015', False,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(352, 126, 107, 19, 4,
                           '165.70', False, u'PRC 14/2015', True,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(353, 126, 107, 20, 3,
                           '165.70', True, u'PRC 14/2015', False,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(354, 126, 109, 21, 2,
                           '1050.00', True, u'SLS 9/2015', True,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(355, 126, 109, 22, 3,
                           '1050.00', False, u'SLS 9/2015', False,
                           date(2015, 2, 13), None, None, None))
loader.save(
    create_ledger_movement(356, 127, 101, 1, 4, '41.10', False, u'PRC 15/2015',
                           True, date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(357, 127, 101, 2, 3, '41.10', True, u'PRC 15/2015',
                           False, date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(358, 127, 102, 3, 4,
                           '143.40', False, u'PRC 16/2015', True,
                           date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(359, 127, 102, 4, 3, '143.40', True, u'PRC 16/2015',
                           False, date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(360, 127, 103, 5, 4,
                           '600.40', False, u'PRC 17/2015', True,
                           date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(361, 127, 103, 6, 3, '600.40', True, u'PRC 17/2015',
                           False, date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(362, 127, 104, 7, 4,
                           '1201.00', False, u'PRC 18/2015', True,
                           date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(363, 127, 104, 8, 3,
                           '1201.00', True, u'PRC 18/2015', False,
                           date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(364, 127, 110, 9, 2, '280.00', True, u'SLS 10/2015',
                           True, date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(365, 127, 110, 10, 3,
                           '280.00', False, u'SLS 10/2015', False,
                           date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(366, 127, 105, 11, 4,
                           '3243.78', False, u'PRC 19/2015', True,
                           date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(367, 127, 105, 12, 3,
                           '3243.78', True, u'PRC 19/2015', False,
                           date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(368, 127, 106, 13, 4,
                           '115.87', False, u'PRC 20/2015', True,
                           date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(369, 127, 106, 14, 3,
                           '115.87', True, u'PRC 20/2015', False,
                           date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(370, 127, 107, 15, 4,
                           '166.12', False, u'PRC 21/2015', True,
                           date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(371, 127, 107, 16, 3,
                           '166.12', True, u'PRC 21/2015', False,
                           date(2015, 3, 13), None, None, None))
loader.save(
    create_ledger_movement(372, 128, 101, 1, 4, '41.30', False, u'PRC 22/2015',
                           True, date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(373, 128, 101, 2, 3, '41.30', True, u'PRC 22/2015',
                           False, date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(374, 128, 102, 3, 4,
                           '142.10', False, u'PRC 23/2015', True,
                           date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(375, 128, 102, 4, 3, '142.10', True, u'PRC 23/2015',
                           False, date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(376, 128, 103, 5, 4,
                           '601.50', False, u'PRC 24/2015', True,
                           date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(377, 128, 103, 6, 3, '601.50', True, u'PRC 24/2015',
                           False, date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(378, 128, 104, 7, 4,
                           '1201.20', False, u'PRC 25/2015', True,
                           date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(379, 128, 104, 8, 3,
                           '1201.20', True, u'PRC 25/2015', False,
                           date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(380, 128, 111, 9, 2, '450.00', True, u'SLS 11/2015',
                           True, date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(381, 128, 111, 10, 3,
                           '450.00', False, u'SLS 11/2015', False,
                           date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(382, 128, 105, 11, 4,
                           '3242.48', False, u'PRC 26/2015', True,
                           date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(383, 128, 105, 12, 3,
                           '3242.48', True, u'PRC 26/2015', False,
                           date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(384, 128, 112, 13, 2,
                           '880.00', True, u'SLS 12/2015', True,
                           date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(385, 128, 112, 14, 3,
                           '880.00', False, u'SLS 12/2015', False,
                           date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(386, 128, 106, 15, 4,
                           '116.78', False, u'PRC 27/2015', True,
                           date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(387, 128, 106, 16, 3,
                           '116.78', True, u'PRC 27/2015', False,
                           date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(388, 128, 107, 17, 4,
                           '166.28', False, u'PRC 28/2015', True,
                           date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(389, 128, 107, 18, 3,
                           '166.28', True, u'PRC 28/2015', False,
                           date(2015, 4, 13), None, None, None))
loader.save(
    create_ledger_movement(390, 129, 113, 1, 2, '405.00', True, u'SLS 25/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(391, 129, 114, 2, 2, '350.00', True, u'SLS 26/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(392, 129, 115, 3, 2, '260.00', True, u'SLS 41/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(393, 129, 116, 4, 2, '260.00', True, u'SLS 42/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(394, 129, 117, 5, 2, '247.00', True, u'SLS 43/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(395, 129, 118, 6, 2, '150.00', True, u'SLS 46/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(396, 129, 119, 7, 2, '150.00', True, u'SLS 45/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(397, 129, 120, 8, 2, '150.00', True, u'SLS 44/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(398, 129, 123, 9, 2, '150.00', True, u'SLS 47/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(399, 129, 132, 10, 2, '85.00', True, u'SLS 31/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(400, 129, 134, 11, 2, '42.00', True, u'SLS 32/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(401, 129, 139, 12, 2,
                           '117.30', True, u'SLS 33/2015', True,
                           date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(402, 129, 141, 13, 2, '60.00', True, u'SLS 34/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(403, 129, 146, 14, 2,
                           '120.00', True, u'SLS 35/2015', True,
                           date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(404, 129, 150, 15, 2,
                           '120.00', True, u'SLS 29/2015', True,
                           date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(405, 129, 151, 16, 2, '90.00', True, u'SLS 30/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(406, 129, 156, 17, 2, '95.00', True, u'SLS 37/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(407, 129, 157, 18, 2, '60.00', True, u'SLS 38/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(408, 129, 165, 19, 2, '60.00', True, u'SLS 40/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(409, 129, 172, 20, 2, '60.00', True, u'SLS 36/2015',
                           True, date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(410, 129, 180, 21, 2,
                           '360.00', True, u'SLS 28/2015', True,
                           date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(411, 129, None, 22, 12, '3391.30', True, u'', True,
                           date(2015, 1, 21), None, None, None))
loader.save(
    create_ledger_movement(412, 130, 117, 1, 2, '13.00', True, u'SLS 43/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(413, 130, 122, 2, 2, '189.00', True, u'SLS 27/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(414, 130, 134, 3, 2, '18.36', True, u'SLS 32/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(415, 130, 139, 4, 2, '2.30', False, u'SLS 33/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(416, 130, 156, 5, 2, '5.00', True, u'SLS 37/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(417, 130, 173, 6, 2, '115.00', True, u'SLS 39/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(418, 130, 113, 7, 2, '180.00', True, u'SLS 48/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(419, 130, 114, 8, 2, '114.00', True, u'SLS 49/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(420, 130, 115, 9, 2, '60.00', True, u'SLS 64/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(421, 130, 116, 10, 2, '60.00', True, u'SLS 65/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(422, 130, 117, 11, 2, '60.00', True, u'SLS 66/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(423, 130, 119, 12, 2, '30.00', True, u'SLS 68/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(424, 130, 120, 13, 2, '30.00', True, u'SLS 67/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(425, 130, 122, 14, 2,
                           '101.50', True, u'SLS 50/2015', True,
                           date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(426, 130, 123, 15, 2, '30.60', True, u'SLS 70/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(427, 130, 132, 16, 2,
                           '175.00', True, u'SLS 54/2015', True,
                           date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(428, 130, 134, 17, 2, '60.00', True, u'SLS 55/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(429, 130, 139, 18, 2,
                           '120.00', True, u'SLS 56/2015', True,
                           date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(430, 130, 141, 19, 2, '60.00', True, u'SLS 57/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(431, 130, 146, 20, 2,
                           '137.75', True, u'SLS 58/2015', True,
                           date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(432, 130, 150, 21, 2, '85.00', True, u'SLS 52/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(433, 130, 151, 22, 2, '60.00', True, u'SLS 53/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(434, 130, 156, 23, 2,
                           '115.00', True, u'SLS 60/2015', True,
                           date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(435, 130, 165, 24, 2, '60.00', True, u'SLS 63/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(436, 130, 172, 25, 2, '90.00', True, u'SLS 59/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(437, 130, 173, 26, 2, '73.50', True, u'SLS 62/2015',
                           True, date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(438, 130, 180, 27, 2,
                           '122.40', True, u'SLS 51/2015', True,
                           date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(439, 130, None, 28, 12, '2162.81', True, u'', True,
                           date(2015, 2, 21), None, None, None))
loader.save(
    create_ledger_movement(440, 131, 122, 1, 2, '81.00', True, u'SLS 27/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(441, 131, 134, 2, 2, '0.36', False, u'SLS 32/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(442, 131, 114, 3, 2, '6.00', True, u'SLS 49/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(443, 131, 118, 4, 2, '30.00', True, u'SLS 69/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(444, 131, 122, 5, 2, '41.32', True, u'SLS 50/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(445, 131, 123, 6, 2, '0.60', False, u'SLS 70/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(446, 131, 146, 7, 2, '7.25', True, u'SLS 58/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(447, 131, 157, 8, 2, '60.00', True, u'SLS 61/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(448, 131, 180, 9, 2, '2.40', False, u'SLS 51/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(449, 131, 113, 10, 2,
                           '115.00', True, u'SLS 71/2015', True,
                           date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(450, 131, 114, 11, 2, '42.00', True, u'SLS 72/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(451, 131, 122, 12, 2,
                           '107.10', True, u'SLS 73/2015', True,
                           date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(452, 131, 132, 13, 2,
                           '120.00', True, u'SLS 77/2015', True,
                           date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(453, 131, 134, 14, 2, '60.00', True, u'SLS 78/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(454, 131, 139, 15, 2, '85.00', True, u'SLS 79/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(455, 131, 141, 16, 2, '60.00', True, u'SLS 80/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(456, 131, 146, 17, 2,
                           '109.25', True, u'SLS 81/2015', False,
                           date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(457, 131, 150, 18, 2,
                           '120.00', True, u'SLS 75/2015', True,
                           date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(458, 131, 151, 19, 2, '60.00', True, u'SLS 76/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(459, 131, 156, 20, 2,
                           '120.00', True, u'SLS 83/2015', True,
                           date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(460, 131, 165, 21, 2, '60.00', True, u'SLS 86/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(461, 131, 172, 22, 2, '60.00', True, u'SLS 82/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(462, 131, 173, 23, 2, '70.00', True, u'SLS 85/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(463, 131, 180, 24, 2, '61.20', True, u'SLS 74/2015',
                           True, date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(464, 131, None, 25, 12, '1471.76', True, u'', True,
                           date(2015, 3, 21), None, None, None))
loader.save(
    create_ledger_movement(465, 132, 122, 1, 2, '2.18', True, u'SLS 50/2015',
                           True, date(2015, 4, 21), None, None, None))
loader.save(
    create_ledger_movement(466, 132, 173, 2, 2, '31.50', True, u'SLS 62/2015',
                           True, date(2015, 4, 21), None, None, None))
loader.save(
    create_ledger_movement(467, 132, 114, 3, 2, '18.00', True, u'SLS 72/2015',
                           True, date(2015, 4, 21), None, None, None))
loader.save(
    create_ledger_movement(468, 132, 122, 4, 2, '2.10', False, u'SLS 73/2015',
                           True, date(2015, 4, 21), None, None, None))
loader.save(
    create_ledger_movement(469, 132, 146, 5, 2, '5.46', True, u'SLS 81/2015',
                           False, date(2015, 4, 21), None, None, None))
loader.save(
    create_ledger_movement(470, 132, 157, 6, 2, '60.00', True, u'SLS 84/2015',
                           True, date(2015, 4, 21), None, None, None))
loader.save(
    create_ledger_movement(471, 132, 173, 7, 2, '30.00', True, u'SLS 85/2015',
                           True, date(2015, 4, 21), None, None, None))
loader.save(
    create_ledger_movement(472, 132, 180, 8, 2, '1.20', False, u'SLS 74/2015',
                           True, date(2015, 4, 21), None, None, None))
loader.save(
    create_ledger_movement(473, 132, 114, 9, 2, '880.00', True, u'SLS 14/2015',
                           True, date(2015, 4, 21), None, None, None))
loader.save(
    create_ledger_movement(474, 132, 115, 10, 2,
                           '1050.00', True, u'SLS 15/2015', True,
                           date(2015, 4, 21), None, None, None))
loader.save(
    create_ledger_movement(475, 132, 115, 11, 2,
                           '196.00', True, u'SLS 16/2015', False,
                           date(2015, 4, 21), None, None, None))
loader.save(
    create_ledger_movement(476, 132, 116, 12, 2,
                           '459.00', True, u'SLS 17/2015', False,
                           date(2015, 4, 21), None, None, None))
loader.save(
    create_ledger_movement(477, 132, 117, 13, 2,
                           '880.00', True, u'SLS 18/2015', True,
                           date(2015, 4, 21), None, None, None))
loader.save(
    create_ledger_movement(478, 132, None, 14, 12, '3608.84', True, u'', True,
                           date(2015, 4, 21), None, None, None))

loader.flush_deferred_objects()
