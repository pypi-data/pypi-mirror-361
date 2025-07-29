# -*- coding: UTF-8 -*-
logger.info("Loading 353 objects to table cal_event...")
# fields: id, modified, created, project, start_date, start_time, end_date, end_time, build_time, build_method, owner_type, owner_id, user, assigned_to, summary, description, access_class, sequence, auto_type, priority, event_type, transparent, room, state, amount
loader.save(
    create_cal_event(1, dt(2018, 12, 22, 12, 25,
                           8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2013, 1, 1), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 1, None, None, u"New Year's Day", u'',
                     None, 0, 1, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(2, dt(2018, 12, 22, 12, 25,
                           8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2014, 1, 1), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 1, None, None, u"New Year's Day", u'',
                     None, 0, 2, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(3, dt(2018, 12, 22, 12, 25,
                           8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2015, 1, 1), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 1, None, None, u"New Year's Day", u'',
                     None, 0, 3, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(4, dt(2018, 12, 22, 12, 24,
                           52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 1, 1), None, None, None, None, None,
                     cal_RecurrentEvent, 1, None, None, u"New Year's Day", u'',
                     None, 0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(5, dt(2018, 12, 22, 12, 24,
                           52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 1, 1), None, None, None, None, None,
                     cal_RecurrentEvent, 1, None, None, u"New Year's Day", u'',
                     None, 0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(6, dt(2018, 12, 22, 12, 24,
                           52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 1, 1), None, None, None, None, None,
                     cal_RecurrentEvent, 1, None, None, u"New Year's Day", u'',
                     None, 0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(7, dt(2018, 12, 22, 12, 24,
                           52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 1, 1), None, None, None, None, None,
                     cal_RecurrentEvent, 1, None, None, u"New Year's Day", u'',
                     None, 0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(8, dt(2018, 12, 22, 12, 24,
                           52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2020, 1, 1), None, None, None, None, None,
                     cal_RecurrentEvent, 1, None, None, u"New Year's Day", u'',
                     None, 0, 8, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(9, dt(2018, 12, 22, 12, 25, 8),
                     dt(2018, 12, 22, 12, 24, 52), None, date(2013, 5, 1),
                     None, None, None, None, u'appypdf', cal_RecurrentEvent, 2,
                     None, None, u"International Workers' Day", u'', None, 0,
                     1, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(10, dt(2018, 12, 22, 12, 25, 8),
                     dt(2018, 12, 22, 12, 24, 52), None, date(2014, 5, 1),
                     None, None, None, None, u'appypdf', cal_RecurrentEvent, 2,
                     None, None, u"International Workers' Day", u'', None, 0,
                     2, u'30', 1, False, None, u'60', None))
loader.save(
    create_cal_event(11, dt(2018, 12, 22, 12, 25, 8),
                     dt(2018, 12, 22, 12, 24, 52), None, date(2015, 5, 1),
                     None, None, None, None, u'appypdf', cal_RecurrentEvent, 2,
                     None, None, u"International Workers' Day", u'', None, 0,
                     3, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(12, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 5,
                          1), None, None, None, None, None, cal_RecurrentEvent,
                     2, None, None, u"International Workers' Day", u'', None,
                     0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(13, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 5,
                          1), None, None, None, None, None, cal_RecurrentEvent,
                     2, None, None, u"International Workers' Day", u'', None,
                     0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(14, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 5,
                          1), None, None, None, None, None, cal_RecurrentEvent,
                     2, None, None, u"International Workers' Day", u'', None,
                     0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(15, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 5,
                          1), None, None, None, None, None, cal_RecurrentEvent,
                     2, None, None, u"International Workers' Day", u'', None,
                     0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(16, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2020, 5,
                          1), None, None, None, None, None, cal_RecurrentEvent,
                     2, None, None, u"International Workers' Day", u'', None,
                     0, 8, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(17, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2013, 7, 21), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 3, None, None, u'National Day', u'',
                     None, 0, 1, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(18, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2014, 7, 21), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 3, None, None, u'National Day', u'',
                     None, 0, 2, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(19, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2015, 7, 21), None, None, None, None, None,
                     cal_RecurrentEvent, 3, None, None, u'National Day', u'',
                     None, 0, 3, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(20, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 7, 21), None, None, None, None, None,
                     cal_RecurrentEvent, 3, None, None, u'National Day', u'',
                     None, 0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(21, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 7, 21), None, None, None, None, None,
                     cal_RecurrentEvent, 3, None, None, u'National Day', u'',
                     None, 0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(22, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 7, 21), None, None, None, None, None,
                     cal_RecurrentEvent, 3, None, None, u'National Day', u'',
                     None, 0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(23, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 7, 21), None, None, None, None, None,
                     cal_RecurrentEvent, 3, None, None, u'National Day', u'',
                     None, 0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(24, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2013, 8, 15), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 4, None, None, u'Assumption of Mary',
                     u'', None, 0, 1, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(25, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2014, 8, 15), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 4, None, None, u'Assumption of Mary',
                     u'', None, 0, 2, u'30', 1, False, None, u'60', None))
loader.save(
    create_cal_event(26, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2015, 8, 15), None, None, None, None, None,
                     cal_RecurrentEvent, 4, None, None, u'Assumption of Mary',
                     u'', None, 0, 3, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(27, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 8, 15), None, None, None, None, None,
                     cal_RecurrentEvent, 4, None, None, u'Assumption of Mary',
                     u'', None, 0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(28, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 8, 15), None, None, None, None, None,
                     cal_RecurrentEvent, 4, None, None, u'Assumption of Mary',
                     u'', None, 0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(29, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 8, 15), None, None, None, None, None,
                     cal_RecurrentEvent, 4, None, None, u'Assumption of Mary',
                     u'', None, 0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(30, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 8, 15), None, None, None, None, None,
                     cal_RecurrentEvent, 4, None, None, u'Assumption of Mary',
                     u'', None, 0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(31, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2013, 10, 31), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 5, None, None, u"All Souls' Day", u'',
                     None, 0, 1, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(32, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2014, 10, 31), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 5, None, None, u"All Souls' Day", u'',
                     None, 0, 2, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(33, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2015, 10, 31), None, None, None, None, None,
                     cal_RecurrentEvent, 5, None, None, u"All Souls' Day", u'',
                     None, 0, 3, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(34, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 10, 31), None, None, None, None, None,
                     cal_RecurrentEvent, 5, None, None, u"All Souls' Day", u'',
                     None, 0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(35, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 10, 31), None, None, None, None, None,
                     cal_RecurrentEvent, 5, None, None, u"All Souls' Day", u'',
                     None, 0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(36, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 10, 31), None, None, None, None, None,
                     cal_RecurrentEvent, 5, None, None, u"All Souls' Day", u'',
                     None, 0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(37, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 10, 31), None, None, None, None, None,
                     cal_RecurrentEvent, 5, None, None, u"All Souls' Day", u'',
                     None, 0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(38, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2013, 11, 1), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 6, None, None, u"All Saints' Day",
                     u'', None, 0, 1, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(39, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2014, 11, 1), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 6, None, None, u"All Saints' Day",
                     u'', None, 0, 2, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(40, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2015, 11, 1), None, None, None, None, None,
                     cal_RecurrentEvent, 6, None, None, u"All Saints' Day",
                     u'', None, 0, 3, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(41, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 11, 1), None, None, None, None, None,
                     cal_RecurrentEvent, 6, None, None, u"All Saints' Day",
                     u'', None, 0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(42, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 11, 1), None, None, None, None, None,
                     cal_RecurrentEvent, 6, None, None, u"All Saints' Day",
                     u'', None, 0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(43, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 11, 1), None, None, None, None, None,
                     cal_RecurrentEvent, 6, None, None, u"All Saints' Day",
                     u'', None, 0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(44, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 11, 1), None, None, None, None, None,
                     cal_RecurrentEvent, 6, None, None, u"All Saints' Day",
                     u'', None, 0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(45, dt(2018, 12, 22, 12, 25, 8),
                     dt(2018, 12, 22, 12, 24, 52), None, date(2013, 11, 11),
                     None, None, None, None, u'appypdf', cal_RecurrentEvent, 7,
                     None, None, u'Armistice with Germany', u'', None, 0, 1,
                     u'30', 1, False, None, u'60', None))
loader.save(
    create_cal_event(46, dt(2018, 12, 22, 12, 25, 8),
                     dt(2018, 12, 22, 12, 24, 52), None, date(2014, 11, 11),
                     None, None, None, None, u'appypdf', cal_RecurrentEvent, 7,
                     None, None, u'Armistice with Germany', u'', None, 0, 2,
                     u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(47, dt(2018, 12, 22, 12, 24, 52),
                     dt(2018, 12, 22, 12, 24, 52), None, date(2015, 11, 11),
                     None, None, None, None, None, cal_RecurrentEvent, 7, None,
                     None, u'Armistice with Germany', u'', None, 0, 3, u'30',
                     1, False, None, u'10', None))
loader.save(
    create_cal_event(48, dt(2018, 12, 22, 12, 24, 52),
                     dt(2018, 12, 22, 12, 24, 52), None, date(2016, 11, 11),
                     None, None, None, None, None, cal_RecurrentEvent, 7, None,
                     None, u'Armistice with Germany', u'', None, 0, 4, u'30',
                     1, False, None, u'10', None))
loader.save(
    create_cal_event(49, dt(2018, 12, 22, 12, 24, 52),
                     dt(2018, 12, 22, 12, 24, 52), None, date(2017, 11, 11),
                     None, None, None, None, None, cal_RecurrentEvent, 7, None,
                     None, u'Armistice with Germany', u'', None, 0, 5, u'30',
                     1, False, None, u'10', None))
loader.save(
    create_cal_event(50, dt(2018, 12, 22, 12, 24, 52),
                     dt(2018, 12, 22, 12, 24, 52), None, date(2018, 11, 11),
                     None, None, None, None, None, cal_RecurrentEvent, 7, None,
                     None, u'Armistice with Germany', u'', None, 0, 6, u'30',
                     1, False, None, u'10', None))
loader.save(
    create_cal_event(51, dt(2018, 12, 22, 12, 24, 52),
                     dt(2018, 12, 22, 12, 24, 52), None, date(2019, 11, 11),
                     None, None, None, None, None, cal_RecurrentEvent, 7, None,
                     None, u'Armistice with Germany', u'', None, 0, 7, u'30',
                     1, False, None, u'10', None))
loader.save(
    create_cal_event(52, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2013, 12, 25), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 8, None, None, u'Christmas', u'',
                     None, 0, 1, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(53, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2014, 12, 25), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 8, None, None, u'Christmas', u'',
                     None, 0, 2, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(54, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2015, 12, 25), None, None, None, None, None,
                     cal_RecurrentEvent, 8, None, None, u'Christmas', u'',
                     None, 0, 3, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(55, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 12, 25), None, None, None, None, None,
                     cal_RecurrentEvent, 8, None, None, u'Christmas', u'',
                     None, 0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(56, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 12, 25), None, None, None, None, None,
                     cal_RecurrentEvent, 8, None, None, u'Christmas', u'',
                     None, 0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(57, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 12, 25), None, None, None, None, None,
                     cal_RecurrentEvent, 8, None, None, u'Christmas', u'',
                     None, 0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(58, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 12, 25), None, None, None, None, None,
                     cal_RecurrentEvent, 8, None, None, u'Christmas', u'',
                     None, 0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(59, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2013, 3, 31), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 9, None, None, u'Easter sunday', u'',
                     None, 0, 1, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(60, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2014, 4, 20), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 9, None, None, u'Easter sunday', u'',
                     None, 0, 2, u'30', 1, False, None, u'60', None))
loader.save(
    create_cal_event(61, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2015, 4, 5), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 9, None, None, u'Easter sunday', u'',
                     None, 0, 3, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(62, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 3, 27), None, None, None, None, None,
                     cal_RecurrentEvent, 9, None, None, u'Easter sunday', u'',
                     None, 0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(63, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 4, 16), None, None, None, None, None,
                     cal_RecurrentEvent, 9, None, None, u'Easter sunday', u'',
                     None, 0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(64, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 4, 1), None, None, None, None, None,
                     cal_RecurrentEvent, 9, None, None, u'Easter sunday', u'',
                     None, 0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(65, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 4, 21), None, None, None, None, None,
                     cal_RecurrentEvent, 9, None, None, u'Easter sunday', u'',
                     None, 0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(66, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2020, 4, 12), None, None, None, None, None,
                     cal_RecurrentEvent, 9, None, None, u'Easter sunday', u'',
                     None, 0, 8, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(67, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2013, 4, 1), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 10, None, None, u'Easter monday', u'',
                     None, 0, 1, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(68, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2014, 4, 21), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 10, None, None, u'Easter monday', u'',
                     None, 0, 2, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(69, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2015, 4, 6), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 10, None, None, u'Easter monday', u'',
                     None, 0, 3, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(70, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 3, 28), None, None, None, None, None,
                     cal_RecurrentEvent, 10, None, None, u'Easter monday', u'',
                     None, 0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(71, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 4, 17), None, None, None, None, None,
                     cal_RecurrentEvent, 10, None, None, u'Easter monday', u'',
                     None, 0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(72, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 4, 2), None, None, None, None, None,
                     cal_RecurrentEvent, 10, None, None, u'Easter monday', u'',
                     None, 0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(73, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 4, 22), None, None, None, None, None,
                     cal_RecurrentEvent, 10, None, None, u'Easter monday', u'',
                     None, 0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(74, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2020, 4, 13), None, None, None, None, None,
                     cal_RecurrentEvent, 10, None, None, u'Easter monday', u'',
                     None, 0, 8, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(75, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2013, 5, 9), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 11, None, None, u'Ascension of Jesus',
                     u'', None, 0, 1, u'30', 1, False, None, u'60', None))
loader.save(
    create_cal_event(76, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2014, 5, 29), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 11, None, None, u'Ascension of Jesus',
                     u'', None, 0, 2, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(77, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2015, 5, 14), None, None, None, None, None,
                     cal_RecurrentEvent, 11, None, None, u'Ascension of Jesus',
                     u'', None, 0, 3, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(78, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 5, 5), None, None, None, None, None,
                     cal_RecurrentEvent, 11, None, None, u'Ascension of Jesus',
                     u'', None, 0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(79, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 5, 25), None, None, None, None, None,
                     cal_RecurrentEvent, 11, None, None, u'Ascension of Jesus',
                     u'', None, 0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(80, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 5, 10), None, None, None, None, None,
                     cal_RecurrentEvent, 11, None, None, u'Ascension of Jesus',
                     u'', None, 0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(81, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 5, 30), None, None, None, None, None,
                     cal_RecurrentEvent, 11, None, None, u'Ascension of Jesus',
                     u'', None, 0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(82, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2020, 5, 21), None, None, None, None, None,
                     cal_RecurrentEvent, 11, None, None, u'Ascension of Jesus',
                     u'', None, 0, 8, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(83, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2013, 5, 20), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 12, None, None, u'Pentecost', u'',
                     None, 0, 1, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(84, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2014, 6, 9), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 12, None, None, u'Pentecost', u'',
                     None, 0, 2, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(85, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2015, 5, 25), None, None, None, None, None,
                     cal_RecurrentEvent, 12, None, None, u'Pentecost', u'',
                     None, 0, 3, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(86, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 5, 16), None, None, None, None, None,
                     cal_RecurrentEvent, 12, None, None, u'Pentecost', u'',
                     None, 0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(87, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 6, 5), None, None, None, None, None,
                     cal_RecurrentEvent, 12, None, None, u'Pentecost', u'',
                     None, 0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(88, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 5, 21), None, None, None, None, None,
                     cal_RecurrentEvent, 12, None, None, u'Pentecost', u'',
                     None, 0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(89, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 6, 10), None, None, None, None, None,
                     cal_RecurrentEvent, 12, None, None, u'Pentecost', u'',
                     None, 0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(90, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2013, 3, 29), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 13, None, None, u'Good Friday', u'',
                     None, 0, 1, u'30', 1, False, None, u'60', None))
loader.save(
    create_cal_event(91, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2014, 4, 18), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 13, None, None, u'Good Friday', u'',
                     None, 0, 2, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(92, dt(2018, 12, 22, 12, 25,
                            8), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2015, 4, 3), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 13, None, None, u'Good Friday', u'',
                     None, 0, 3, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(93, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 3, 25), None, None, None, None, None,
                     cal_RecurrentEvent, 13, None, None, u'Good Friday', u'',
                     None, 0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(94, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 4, 14), None, None, None, None, None,
                     cal_RecurrentEvent, 13, None, None, u'Good Friday', u'',
                     None, 0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(95, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 3, 30), None, None, None, None, None,
                     cal_RecurrentEvent, 13, None, None, u'Good Friday', u'',
                     None, 0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(96, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 4, 19), None, None, None, None, None,
                     cal_RecurrentEvent, 13, None, None, u'Good Friday', u'',
                     None, 0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(97, dt(2018, 12, 22, 12, 24,
                            52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2020, 4, 10), None, None, None, None, None,
                     cal_RecurrentEvent, 13, None, None, u'Good Friday', u'',
                     None, 0, 8, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(98, dt(2018, 12, 22, 12, 25,
                            9), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2013, 2, 13), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 14, None, None, u'Ash Wednesday', u'',
                     None, 0, 1, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(99, dt(2018, 12, 22, 12, 25,
                            9), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2014, 3, 5), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 14, None, None, u'Ash Wednesday', u'',
                     None, 0, 2, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(100, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2015, 2, 18), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 14, None, None, u'Ash Wednesday', u'',
                     None, 0, 3, u'30', 1, False, None, u'60', None))
loader.save(
    create_cal_event(101, dt(2018, 12, 22, 12, 24,
                             52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 2, 10), None, None, None, None, None,
                     cal_RecurrentEvent, 14, None, None, u'Ash Wednesday', u'',
                     None, 0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(102, dt(2018, 12, 22, 12, 24,
                             52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 3, 1), None, None, None, None, None,
                     cal_RecurrentEvent, 14, None, None, u'Ash Wednesday', u'',
                     None, 0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(103, dt(2018, 12, 22, 12, 24,
                             52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 2, 14), None, None, None, None, None,
                     cal_RecurrentEvent, 14, None, None, u'Ash Wednesday', u'',
                     None, 0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(104, dt(2018, 12, 22, 12, 24,
                             52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 3, 6), None, None, None, None, None,
                     cal_RecurrentEvent, 14, None, None, u'Ash Wednesday', u'',
                     None, 0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(105, dt(2018, 12, 22, 12, 24,
                             52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2020, 2, 26), None, None, None, None, None,
                     cal_RecurrentEvent, 14, None, None, u'Ash Wednesday', u'',
                     None, 0, 8, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(106, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2013, 2, 11), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 15, None, None, u'Rosenmontag', u'',
                     None, 0, 1, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(107, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2014, 3, 3), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 15, None, None, u'Rosenmontag', u'',
                     None, 0, 2, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(108, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2015, 2, 16), None, None, None, None, u'appypdf',
                     cal_RecurrentEvent, 15, None, None, u'Rosenmontag', u'',
                     None, 0, 3, u'30', 1, False, None, u'50', None))
loader.save(
    create_cal_event(109, dt(2018, 12, 22, 12, 24,
                             52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2016, 2, 8), None, None, None, None, None,
                     cal_RecurrentEvent, 15, None, None, u'Rosenmontag', u'',
                     None, 0, 4, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(110, dt(2018, 12, 22, 12, 24,
                             52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2017, 2, 27), None, None, None, None, None,
                     cal_RecurrentEvent, 15, None, None, u'Rosenmontag', u'',
                     None, 0, 5, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(111, dt(2018, 12, 22, 12, 24,
                             52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2018, 2, 12), None, None, None, None, None,
                     cal_RecurrentEvent, 15, None, None, u'Rosenmontag', u'',
                     None, 0, 6, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(112, dt(2018, 12, 22, 12, 24,
                             52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2019, 3, 4), None, None, None, None, None,
                     cal_RecurrentEvent, 15, None, None, u'Rosenmontag', u'',
                     None, 0, 7, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(113, dt(2018, 12, 22, 12, 24,
                             52), dt(2018, 12, 22, 12, 24, 52), None,
                     date(2020, 2, 24), None, None, None, None, None,
                     cal_RecurrentEvent, 15, None, None, u'Rosenmontag', u'',
                     None, 0, 8, u'30', 1, False, None, u'10', None))
loader.save(
    create_cal_event(114, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 1,
                     date(2014, 11, 4), None, None, None, None, u'appypdf',
                     courses_Course, 1, 4, None, u' 1', u'', u'30', 0, 1,
                     u'30', 4, False, None, u'50', '5.00'))
loader.save(
    create_cal_event(115, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 1,
                     date(2014, 11, 18), None, None, None, None, u'appypdf',
                     courses_Course, 1, 4, None, u' 2', u'', u'30', 0, 2,
                     u'30', 4, False, None, u'60', None))
loader.save(
    create_cal_event(116, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 1,
                     date(2014, 12, 2), None, None, None, None, u'appypdf',
                     courses_Course, 1, 4, None, u' 3', u'', u'30', 0, 3,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(117, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 1,
                     date(2014, 12, 16), None, None, None, None, u'appypdf',
                     courses_Course, 1, 4, None, u' 4', u'', u'30', 0, 4,
                     u'30', 4, False, None, u'50', '15.00'))
loader.save(
    create_cal_event(118, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 1,
                     date(2014, 12, 30), None, None, None, None, u'appypdf',
                     courses_Course, 1, 4, None, u' 5', u'', u'30', 0, 5,
                     u'30', 4, False, None, u'50', '20.00'))
loader.save(
    create_cal_event(119, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 1,
                     date(2015, 1, 13), None, None, None, None, u'appypdf',
                     courses_Course, 1, 4, None, u' 6', u'', u'30', 0, 6,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(120, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 1,
                     date(2015, 1, 27), None, None, None, None, u'appypdf',
                     courses_Course, 1, 4, None, u' 7', u'', u'30', 0, 7,
                     u'30', 4, False, None, u'60', None))
loader.save(
    create_cal_event(121, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 1,
                     date(2015, 2, 10), None, None, None, None, u'appypdf',
                     courses_Course, 1, 4, None, u' 8', u'', u'30', 0, 8,
                     u'30', 4, False, None, u'50', '5.00'))
loader.save(
    create_cal_event(122, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 1,
                     date(2015, 2, 24), None, None, None, None, u'appypdf',
                     courses_Course, 1, 4, None, u' 9', u'', u'30', 0, 9,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(123, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 1,
                     date(2015, 3, 10), None, None, None, None, u'appypdf',
                     courses_Course, 1, 4, None, u' 10', u'', u'30', 0, 10,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(124, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 2,
                     date(2014, 11, 5), None, None, None, None, u'appypdf',
                     courses_Course, 2, 5, None, u' 1', u'', u'30', 0, 1,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(125, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 2,
                     date(2014, 11, 19), None, None, None, None, u'appypdf',
                     courses_Course, 2, 5, None, u' 2', u'', u'30', 0, 2,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(126, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 2,
                     date(2014, 12, 3), None, None, None, None, u'appypdf',
                     courses_Course, 2, 5, None, u' 3', u'', u'30', 0, 3,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(127, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 2,
                     date(2014, 12, 17), None, None, None, None, u'appypdf',
                     courses_Course, 2, 5, None, u' 4', u'', u'30', 0, 4,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(128, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 2,
                     date(2014, 12, 31), None, None, None, None, u'appypdf',
                     courses_Course, 2, 5, None, u' 5', u'', u'30', 0, 5,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(129, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 2,
                     date(2015, 1, 14), None, None, None, None, u'appypdf',
                     courses_Course, 2, 5, None, u' 6', u'', u'30', 0, 6,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(130, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 2,
                     date(2015, 1, 28), None, None, None, None, u'appypdf',
                     courses_Course, 2, 5, None, u' 7', u'', u'30', 0, 7,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(131, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 2,
                     date(2015, 2, 11), None, None, None, None, u'appypdf',
                     courses_Course, 2, 5, None, u' 8', u'', u'30', 0, 8,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(132, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 2,
                     date(2015, 2, 25), None, None, None, None, u'appypdf',
                     courses_Course, 2, 5, None, u' 9', u'', u'30', 0, 9,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(133, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 58), 2,
                     date(2015, 3, 11), None, None, None, None, u'appypdf',
                     courses_Course, 2, 5, None, u' 10', u'', u'30', 0, 10,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(134, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 59), 7,
                     date(2014, 11, 10), None, None, None, None, u'appypdf',
                     courses_Course, 7, 4, None, u' 1', u'', u'30', 0, 1,
                     u'30', 4, False, None, u'50', '15.00'))
loader.save(
    create_cal_event(135, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 59), 7,
                     date(2014, 11, 24), None, None, None, None, u'appypdf',
                     courses_Course, 7, 4, None, u' 2', u'', u'30', 0, 2,
                     u'30', 4, False, None, u'60', '20.00'))
loader.save(
    create_cal_event(136, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 59), 7,
                     date(2014, 12, 8), None, None, None, None, u'appypdf',
                     courses_Course, 7, 4, None, u' 3', u'', u'30', 0, 3,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(137, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 59), 7,
                     date(2014, 12, 22), None, None, None, None, u'appypdf',
                     courses_Course, 7, 4, None, u' 4', u'', u'30', 0, 4,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(138, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 59), 7,
                     date(2015, 1, 5), None, None, None, None, u'appypdf',
                     courses_Course, 7, 4, None, u' 5', u'', u'30', 0, 5,
                     u'30', 4, False, None, u'50', '5.00'))
loader.save(
    create_cal_event(139, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 59), 7,
                     date(2015, 1, 19), None, None, None, None, u'appypdf',
                     courses_Course, 7, 4, None, u' 6', u'', u'30', 0, 6,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(140, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 59), 7,
                     date(2015, 2, 2), None, None, None, None, u'appypdf',
                     courses_Course, 7, 4, None, u' 7', u'', u'30', 0, 7,
                     u'30', 4, False, None, u'60', None))
loader.save(
    create_cal_event(141, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 59), 7,
                     date(2015, 2, 17), None, None, None, None, u'appypdf',
                     courses_Course, 7, 4, None, u' 8', u'', u'30', 0, 8,
                     u'30', 4, False, None, u'50', '15.00'))
loader.save(
    create_cal_event(142, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 59), 7,
                     date(2015, 3, 3), None, None, None, None, u'appypdf',
                     courses_Course, 7, 4, None, u' 9', u'', u'30', 0, 9,
                     u'30', 4, False, None, u'50', '20.00'))
loader.save(
    create_cal_event(143, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 59), 7,
                     date(2015, 3, 17), None, None, None, None, u'appypdf',
                     courses_Course, 7, 4, None, u' 10', u'', u'30', 0, 10,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(144, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 59), 8,
                     date(2014, 11, 12), None, None, None, None, u'appypdf',
                     courses_Course, 8, 5, None, u' 1', u'', u'30', 0, 1,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(145, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 59), 8,
                     date(2014, 11, 26), None, None, None, None, u'appypdf',
                     courses_Course, 8, 5, None, u' 2', u'', u'30', 0, 2,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(146, dt(2018, 12, 22, 12, 25,
                             9), dt(2018, 12, 22, 12, 24, 59), 8,
                     date(2014, 12, 10), None, None, None, None, u'appypdf',
                     courses_Course, 8, 5, None, u' 3', u'', u'30', 0, 3,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(147, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 24, 59), 8,
                     date(2014, 12, 24), None, None, None, None, u'appypdf',
                     courses_Course, 8, 5, None, u' 4', u'', u'30', 0, 4,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(148, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 24, 59), 8,
                     date(2015, 1, 7), None, None, None, None, u'appypdf',
                     courses_Course, 8, 5, None, u' 5', u'', u'30', 0, 5,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(149, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 24, 59), 8,
                     date(2015, 1, 21), None, None, None, None, u'appypdf',
                     courses_Course, 8, 5, None, u' 6', u'', u'30', 0, 6,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(150, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 24, 59), 8,
                     date(2015, 2, 4), None, None, None, None, u'appypdf',
                     courses_Course, 8, 5, None, u' 7', u'', u'30', 0, 7,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(151, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 24, 59), 8,
                     date(2015, 2, 19), None, None, None, None, u'appypdf',
                     courses_Course, 8, 5, None, u' 8', u'', u'30', 0, 8,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(152, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 24, 59), 8,
                     date(2015, 3, 5), None, None, None, None, u'appypdf',
                     courses_Course, 8, 5, None, u' 9', u'', u'30', 0, 9,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(153, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 24, 59), 8,
                     date(2015, 3, 19), None, None, None, None, u'appypdf',
                     courses_Course, 8, 5, None, u' 10', u'', u'30', 0, 10,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(154, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 13,
                     date(2014, 11, 16), None, None, None, None, u'appypdf',
                     courses_Course, 13, 4, None, u' 1', u'', u'30', 0, 1,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(155, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 13,
                     date(2014, 11, 30), None, None, None, None, u'appypdf',
                     courses_Course, 13, 4, None, u' 2', u'', u'30', 0, 2,
                     u'30', 4, False, None, u'60', '5.00'))
loader.save(
    create_cal_event(156, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 13,
                     date(2014, 12, 14), None, None, None, None, u'appypdf',
                     courses_Course, 13, 4, None, u' 3', u'', u'30', 0, 3,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(157, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 13,
                     date(2014, 12, 28), None, None, None, None, u'appypdf',
                     courses_Course, 13, 4, None, u' 4', u'', u'30', 0, 4,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(158, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 13,
                     date(2015, 1, 11), None, None, None, None, u'appypdf',
                     courses_Course, 13, 4, None, u' 5', u'', u'30', 0, 5,
                     u'30', 4, False, None, u'50', '15.00'))
loader.save(
    create_cal_event(159, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 13,
                     date(2015, 1, 25), None, None, None, None, u'appypdf',
                     courses_Course, 13, 4, None, u' 6', u'', u'30', 0, 6,
                     u'30', 4, False, None, u'50', '20.00'))
loader.save(
    create_cal_event(160, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 13,
                     date(2015, 2, 8), None, None, None, None, u'appypdf',
                     courses_Course, 13, 4, None, u' 7', u'', u'30', 0, 7,
                     u'30', 4, False, None, u'60', None))
loader.save(
    create_cal_event(161, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 13,
                     date(2015, 2, 22), None, None, None, None, u'appypdf',
                     courses_Course, 13, 4, None, u' 8', u'', u'30', 0, 8,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(162, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 13,
                     date(2015, 3, 8), None, None, None, None, u'appypdf',
                     courses_Course, 13, 4, None, u' 9', u'', u'30', 0, 9,
                     u'30', 4, False, None, u'50', '5.00'))
loader.save(
    create_cal_event(163, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 13,
                     date(2015, 3, 22), None, None, None, None, u'appypdf',
                     courses_Course, 13, 4, None, u' 10', u'', u'30', 0, 10,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(164, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 14,
                     date(2014, 11, 17), None, None, None, None, u'appypdf',
                     courses_Course, 14, 5, None, u' 1', u'', u'30', 0, 1,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(165, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 14,
                     date(2014, 12, 1), None, None, None, None, u'appypdf',
                     courses_Course, 14, 5, None, u' 2', u'', u'30', 0, 2,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(166, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 14,
                     date(2014, 12, 15), None, None, None, None, u'appypdf',
                     courses_Course, 14, 5, None, u' 3', u'', u'30', 0, 3,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(167, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 14,
                     date(2014, 12, 29), None, None, None, None, u'appypdf',
                     courses_Course, 14, 5, None, u' 4', u'', u'30', 0, 4,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(168, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 14,
                     date(2015, 1, 12), None, None, None, None, u'appypdf',
                     courses_Course, 14, 5, None, u' 5', u'', u'30', 0, 5,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(169, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 14,
                     date(2015, 1, 26), None, None, None, None, u'appypdf',
                     courses_Course, 14, 5, None, u' 6', u'', u'30', 0, 6,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(170, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 14,
                     date(2015, 2, 9), None, None, None, None, u'appypdf',
                     courses_Course, 14, 5, None, u' 7', u'', u'30', 0, 7,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(171, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 14,
                     date(2015, 2, 23), None, None, None, None, u'appypdf',
                     courses_Course, 14, 5, None, u' 8', u'', u'30', 0, 8,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(172, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 14,
                     date(2015, 3, 9), None, None, None, None, u'appypdf',
                     courses_Course, 14, 5, None, u' 9', u'', u'30', 0, 9,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(173, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 14,
                     date(2015, 3, 23), None, None, None, None, u'appypdf',
                     courses_Course, 14, 5, None, u' 10', u'', u'30', 0, 10,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(174, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 19,
                     date(2014, 11, 22), None, None, None, None, u'appypdf',
                     courses_Course, 19, 4, None, u' 1', u'', u'30', 0, 1,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(175, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 19,
                     date(2014, 12, 6), None, None, None, None, u'appypdf',
                     courses_Course, 19, 4, None, u' 2', u'', u'30', 0, 2,
                     u'30', 4, False, None, u'60', '15.00'))
loader.save(
    create_cal_event(176, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 19,
                     date(2014, 12, 20), None, None, None, None, u'appypdf',
                     courses_Course, 19, 4, None, u' 3', u'', u'30', 0, 3,
                     u'30', 4, False, None, u'50', '20.00'))
loader.save(
    create_cal_event(177, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 19,
                     date(2015, 1, 3), None, None, None, None, u'appypdf',
                     courses_Course, 19, 4, None, u' 4', u'', u'30', 0, 4,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(178, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 19,
                     date(2015, 1, 17), None, None, None, None, u'appypdf',
                     courses_Course, 19, 4, None, u' 5', u'', u'30', 0, 5,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(179, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 19,
                     date(2015, 1, 31), None, None, None, None, u'appypdf',
                     courses_Course, 19, 4, None, u' 6', u'', u'30', 0, 6,
                     u'30', 4, False, None, u'50', '5.00'))
loader.save(
    create_cal_event(180, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 19,
                     date(2015, 2, 14), None, None, None, None, u'appypdf',
                     courses_Course, 19, 4, None, u' 7', u'', u'30', 0, 7,
                     u'30', 4, False, None, u'60', None))
loader.save(
    create_cal_event(181, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 19,
                     date(2015, 2, 28), None, None, None, None, u'appypdf',
                     courses_Course, 19, 4, None, u' 8', u'', u'30', 0, 8,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(182, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 19,
                     date(2015, 3, 14), None, None, None, None, u'appypdf',
                     courses_Course, 19, 4, None, u' 9', u'', u'30', 0, 9,
                     u'30', 4, False, None, u'50', '15.00'))
loader.save(
    create_cal_event(183, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 0), 19,
                     date(2015, 3, 28), None, None, None, None, u'appypdf',
                     courses_Course, 19, 4, None, u' 10', u'', u'30', 0, 10,
                     u'30', 4, False, None, u'50', '20.00'))
loader.save(
    create_cal_event(184, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 1), 20,
                     date(2014, 11, 23), None, None, None, None, u'appypdf',
                     courses_Course, 20, 5, None, u' 1', u'', u'30', 0, 1,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(185, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 1), 20,
                     date(2014, 12, 7), None, None, None, None, u'appypdf',
                     courses_Course, 20, 5, None, u' 2', u'', u'30', 0, 2,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(186, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 1), 20,
                     date(2014, 12, 21), None, None, None, None, u'appypdf',
                     courses_Course, 20, 5, None, u' 3', u'', u'30', 0, 3,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(187, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 1), 20,
                     date(2015, 1, 4), None, None, None, None, u'appypdf',
                     courses_Course, 20, 5, None, u' 4', u'', u'30', 0, 4,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(188, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 1), 20,
                     date(2015, 1, 18), None, None, None, None, u'appypdf',
                     courses_Course, 20, 5, None, u' 5', u'', u'30', 0, 5,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(189, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 1), 20,
                     date(2015, 2, 1), None, None, None, None, u'appypdf',
                     courses_Course, 20, 5, None, u' 6', u'', u'30', 0, 6,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(190, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 1), 20,
                     date(2015, 2, 15), None, None, None, None, u'appypdf',
                     courses_Course, 20, 5, None, u' 7', u'', u'30', 0, 7,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(191, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 1), 20,
                     date(2015, 3, 1), None, None, None, None, u'appypdf',
                     courses_Course, 20, 5, None, u' 8', u'', u'30', 0, 8,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(192, dt(2018, 12, 22, 12, 25,
                             10), dt(2018, 12, 22, 12, 25, 1), 20,
                     date(2015, 3, 15), None, None, None, None, u'appypdf',
                     courses_Course, 20, 5, None, u' 9', u'', u'30', 0, 9,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(193, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 20,
                     date(2015, 3, 29), None, None, None, None, u'appypdf',
                     courses_Course, 20, 5, None, u' 10', u'', u'30', 0, 10,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(194, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 25,
                     date(2014, 11, 28), None, None, None, None, u'appypdf',
                     courses_Course, 25, 4, None, u' 1', u'', u'30', 0, 1,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(195, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 25,
                     date(2014, 12, 12), None, None, None, None, u'appypdf',
                     courses_Course, 25, 4, None, u' 2', u'', u'30', 0, 2,
                     u'30', 4, False, None, u'60', None))
loader.save(
    create_cal_event(196, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 25,
                     date(2014, 12, 26), None, None, None, None, u'appypdf',
                     courses_Course, 25, 4, None, u' 3', u'', u'30', 0, 3,
                     u'30', 4, False, None, u'50', '5.00'))
loader.save(
    create_cal_event(197, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 25,
                     date(2015, 1, 9), None, None, None, None, u'appypdf',
                     courses_Course, 25, 4, None, u' 4', u'', u'30', 0, 4,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(198, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 25,
                     date(2015, 1, 23), None, None, None, None, u'appypdf',
                     courses_Course, 25, 4, None, u' 5', u'', u'30', 0, 5,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(199, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 25,
                     date(2015, 2, 6), None, None, None, None, u'appypdf',
                     courses_Course, 25, 4, None, u' 6', u'', u'30', 0, 6,
                     u'30', 4, False, None, u'50', '15.00'))
loader.save(
    create_cal_event(200, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 25,
                     date(2015, 2, 20), None, None, None, None, u'appypdf',
                     courses_Course, 25, 4, None, u' 7', u'', u'30', 0, 7,
                     u'30', 4, False, None, u'60', '20.00'))
loader.save(
    create_cal_event(201, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 25,
                     date(2015, 3, 6), None, None, None, None, u'appypdf',
                     courses_Course, 25, 4, None, u' 8', u'', u'30', 0, 8,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(202, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 25,
                     date(2015, 3, 20), None, None, None, None, u'appypdf',
                     courses_Course, 25, 4, None, u' 9', u'', u'30', 0, 9,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(203, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 25,
                     date(2015, 4, 4), None, None, None, None, u'appypdf',
                     courses_Course, 25, 4, None, u' 10', u'', u'30', 0, 10,
                     u'30', 4, False, None, u'50', '5.00'))
loader.save(
    create_cal_event(204, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 26,
                     date(2014, 11, 29), None, None, None, None, u'appypdf',
                     courses_Course, 26, 5, None, u' 1', u'', u'30', 0, 1,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(205, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 26,
                     date(2014, 12, 13), None, None, None, None, u'appypdf',
                     courses_Course, 26, 5, None, u' 2', u'', u'30', 0, 2,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(206, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 26,
                     date(2014, 12, 27), None, None, None, None, u'appypdf',
                     courses_Course, 26, 5, None, u' 3', u'', u'30', 0, 3,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(207, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 26,
                     date(2015, 1, 10), None, None, None, None, u'appypdf',
                     courses_Course, 26, 5, None, u' 4', u'', u'30', 0, 4,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(208, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 26,
                     date(2015, 1, 24), None, None, None, None, u'appypdf',
                     courses_Course, 26, 5, None, u' 5', u'', u'30', 0, 5,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(209, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 1), 26,
                     date(2015, 2, 7), None, None, None, None, u'appypdf',
                     courses_Course, 26, 5, None, u' 6', u'', u'30', 0, 6,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(210, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 26,
                     date(2015, 2, 21), None, None, None, None, u'appypdf',
                     courses_Course, 26, 5, None, u' 7', u'', u'30', 0, 7,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(211, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 26,
                     date(2015, 3, 7), None, None, None, None, u'appypdf',
                     courses_Course, 26, 5, None, u' 8', u'', u'30', 0, 8,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(212, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 26,
                     date(2015, 3, 21), None, None, None, None, u'appypdf',
                     courses_Course, 26, 5, None, u' 9', u'', u'30', 0, 9,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(213, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 26,
                     date(2015, 4, 4), None, None, None, None, u'appypdf',
                     courses_Course, 26, 5, None, u' 10', u'', u'30', 0, 10,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(214, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 31,
                     date(2014, 12, 4), None, None, None, None, u'appypdf',
                     courses_Course, 31, 4, None, u' 1', u'', u'30', 0, 1,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(215, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 31,
                     date(2014, 12, 18), None, None, None, None, u'appypdf',
                     courses_Course, 31, 4, None, u' 2', u'', u'30', 0, 2,
                     u'30', 4, False, None, u'60', None))
loader.save(
    create_cal_event(216, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 31,
                     date(2015, 1, 2), None, None, None, None, u'appypdf',
                     courses_Course, 31, 4, None, u' 3', u'', u'30', 0, 3,
                     u'30', 4, False, None, u'50', '15.00'))
loader.save(
    create_cal_event(217, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 31,
                     date(2015, 1, 16), None, None, None, None, u'appypdf',
                     courses_Course, 31, 4, None, u' 4', u'', u'30', 0, 4,
                     u'30', 4, False, None, u'50', '20.00'))
loader.save(
    create_cal_event(218, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 31,
                     date(2015, 1, 30), None, None, None, None, u'appypdf',
                     courses_Course, 31, 4, None, u' 5', u'', u'30', 0, 5,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(219, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 31,
                     date(2015, 2, 13), None, None, None, None, u'appypdf',
                     courses_Course, 31, 4, None, u' 6', u'', u'30', 0, 6,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(220, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 31,
                     date(2015, 2, 27), None, None, None, None, u'appypdf',
                     courses_Course, 31, 4, None, u' 7', u'', u'30', 0, 7,
                     u'30', 4, False, None, u'60', '5.00'))
loader.save(
    create_cal_event(221, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 31,
                     date(2015, 3, 13), None, None, None, None, u'appypdf',
                     courses_Course, 31, 4, None, u' 8', u'', u'30', 0, 8,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(222, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 31,
                     date(2015, 3, 27), None, None, None, None, u'appypdf',
                     courses_Course, 31, 4, None, u' 9', u'', u'30', 0, 9,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(223, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 2), 31,
                     date(2015, 4, 10), None, None, None, None, u'appypdf',
                     courses_Course, 31, 4, None, u' 10', u'', u'30', 0, 10,
                     u'30', 4, False, None, u'50', '15.00'))
loader.save(
    create_cal_event(224, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 32,
                     date(2014, 12, 5), None, None, None, None, u'appypdf',
                     courses_Course, 32, 5, None, u' 1', u'', u'30', 0, 1,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(225, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 32,
                     date(2014, 12, 19), None, None, None, None, u'appypdf',
                     courses_Course, 32, 5, None, u' 2', u'', u'30', 0, 2,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(226, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 32,
                     date(2015, 1, 2), None, None, None, None, u'appypdf',
                     courses_Course, 32, 5, None, u' 3', u'', u'30', 0, 3,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(227, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 32,
                     date(2015, 1, 16), None, None, None, None, u'appypdf',
                     courses_Course, 32, 5, None, u' 4', u'', u'30', 0, 4,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(228, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 32,
                     date(2015, 1, 30), None, None, None, None, u'appypdf',
                     courses_Course, 32, 5, None, u' 5', u'', u'30', 0, 5,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(229, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 32,
                     date(2015, 2, 13), None, None, None, None, u'appypdf',
                     courses_Course, 32, 5, None, u' 6', u'', u'30', 0, 6,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(230, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 32,
                     date(2015, 2, 27), None, None, None, None, u'appypdf',
                     courses_Course, 32, 5, None, u' 7', u'', u'30', 0, 7,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(231, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 32,
                     date(2015, 3, 13), None, None, None, None, u'appypdf',
                     courses_Course, 32, 5, None, u' 8', u'', u'30', 0, 8,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(232, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 32,
                     date(2015, 3, 27), None, None, None, None, u'appypdf',
                     courses_Course, 32, 5, None, u' 9', u'', u'30', 0, 9,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(233, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 32,
                     date(2015, 4, 10), None, None, None, None, u'appypdf',
                     courses_Course, 32, 5, None, u' 10', u'', u'30', 0, 10,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(234, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 37,
                     date(2014, 12, 10), None, None, None, None, u'appypdf',
                     courses_Course, 37, 4, None, u' 1', u'', u'30', 0, 1,
                     u'30', 4, False, None, u'50', '20.00'))
loader.save(
    create_cal_event(235, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 37,
                     date(2014, 12, 24), None, None, None, None, u'appypdf',
                     courses_Course, 37, 4, None, u' 2', u'', u'30', 0, 2,
                     u'30', 4, False, None, u'60', None))
loader.save(
    create_cal_event(236, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 37,
                     date(2015, 1, 7), None, None, None, None, u'appypdf',
                     courses_Course, 37, 4, None, u' 3', u'', u'30', 0, 3,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(237, dt(2018, 12, 22, 12, 25,
                             11), dt(2018, 12, 22, 12, 25, 3), 37,
                     date(2015, 1, 21), None, None, None, None, u'appypdf',
                     courses_Course, 37, 4, None, u' 4', u'', u'30', 0, 4,
                     u'30', 4, False, None, u'50', '5.00'))
loader.save(
    create_cal_event(238, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 3), 37,
                     date(2015, 2, 4), None, None, None, None, u'appypdf',
                     courses_Course, 37, 4, None, u' 5', u'', u'30', 0, 5,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(239, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 3), 37,
                     date(2015, 2, 19), None, None, None, None, u'appypdf',
                     courses_Course, 37, 4, None, u' 6', u'', u'30', 0, 6,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(240, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 37,
                     date(2015, 3, 5), None, None, None, None, u'appypdf',
                     courses_Course, 37, 4, None, u' 7', u'', u'30', 0, 7,
                     u'30', 4, False, None, u'60', '15.00'))
loader.save(
    create_cal_event(241, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 37,
                     date(2015, 3, 19), None, None, None, None, u'appypdf',
                     courses_Course, 37, 4, None, u' 8', u'', u'30', 0, 8,
                     u'30', 4, False, None, u'50', '20.00'))
loader.save(
    create_cal_event(242, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 37,
                     date(2015, 4, 2), None, None, None, None, u'appypdf',
                     courses_Course, 37, 4, None, u' 9', u'', u'30', 0, 9,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(243, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 37,
                     date(2015, 4, 16), None, None, None, None, u'appypdf',
                     courses_Course, 37, 4, None, u' 10', u'', u'30', 0, 10,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(244, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 38,
                     date(2014, 12, 11), None, None, None, None, u'appypdf',
                     courses_Course, 38, 5, None, u' 1', u'', u'30', 0, 1,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(245, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 38,
                     date(2014, 12, 26), None, None, None, None, u'appypdf',
                     courses_Course, 38, 5, None, u' 2', u'', u'30', 0, 2,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(246, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 38,
                     date(2015, 1, 9), None, None, None, None, u'appypdf',
                     courses_Course, 38, 5, None, u' 3', u'', u'30', 0, 3,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(247, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 38,
                     date(2015, 1, 23), None, None, None, None, u'appypdf',
                     courses_Course, 38, 5, None, u' 4', u'', u'30', 0, 4,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(248, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 38,
                     date(2015, 2, 6), None, None, None, None, u'appypdf',
                     courses_Course, 38, 5, None, u' 5', u'', u'30', 0, 5,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(249, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 38,
                     date(2015, 2, 20), None, None, None, None, u'appypdf',
                     courses_Course, 38, 5, None, u' 6', u'', u'30', 0, 6,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(250, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 38,
                     date(2015, 3, 6), None, None, None, None, u'appypdf',
                     courses_Course, 38, 5, None, u' 7', u'', u'30', 0, 7,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(251, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 38,
                     date(2015, 3, 20), None, None, None, None, u'appypdf',
                     courses_Course, 38, 5, None, u' 8', u'', u'30', 0, 8,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(252, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 38,
                     date(2015, 4, 4), None, None, None, None, u'appypdf',
                     courses_Course, 38, 5, None, u' 9', u'', u'30', 0, 9,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(253, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 4), 38,
                     date(2015, 4, 18), None, None, None, None, u'appypdf',
                     courses_Course, 38, 5, None, u' 10', u'', u'30', 0, 10,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(254, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 43,
                     date(2014, 12, 16), None, None, None, None, u'appypdf',
                     courses_Course, 43, 4, None, u' 1', u'', u'30', 0, 1,
                     u'30', 4, False, None, u'50', '5.00'))
loader.save(
    create_cal_event(255, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 43,
                     date(2014, 12, 30), None, None, None, None, u'appypdf',
                     courses_Course, 43, 4, None, u' 2', u'', u'30', 0, 2,
                     u'30', 4, False, None, u'60', None))
loader.save(
    create_cal_event(256, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 43,
                     date(2015, 1, 13), None, None, None, None, u'appypdf',
                     courses_Course, 43, 4, None, u' 3', u'', u'30', 0, 3,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(257, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 43,
                     date(2015, 1, 27), None, None, None, None, u'appypdf',
                     courses_Course, 43, 4, None, u' 4', u'', u'30', 0, 4,
                     u'30', 4, False, None, u'50', '15.00'))
loader.save(
    create_cal_event(258, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 43,
                     date(2015, 2, 10), None, None, None, None, u'appypdf',
                     courses_Course, 43, 4, None, u' 5', u'', u'30', 0, 5,
                     u'30', 4, False, None, u'50', '20.00'))
loader.save(
    create_cal_event(259, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 43,
                     date(2015, 2, 24), None, None, None, None, u'appypdf',
                     courses_Course, 43, 4, None, u' 6', u'', u'30', 0, 6,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(260, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 43,
                     date(2015, 3, 10), None, None, None, None, u'appypdf',
                     courses_Course, 43, 4, None, u' 7', u'', u'30', 0, 7,
                     u'30', 4, False, None, u'60', None))
loader.save(
    create_cal_event(261, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 43,
                     date(2015, 3, 24), None, None, None, None, u'appypdf',
                     courses_Course, 43, 4, None, u' 8', u'', u'30', 0, 8,
                     u'30', 4, False, None, u'50', '5.00'))
loader.save(
    create_cal_event(262, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 43,
                     date(2015, 4, 7), None, None, None, None, u'appypdf',
                     courses_Course, 43, 4, None, u' 9', u'', u'30', 0, 9,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(263, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 43,
                     date(2015, 4, 21), None, None, None, None, u'appypdf',
                     courses_Course, 43, 4, None, u' 10', u'', u'30', 0, 10,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(264, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 44,
                     date(2014, 12, 17), None, None, None, None, u'appypdf',
                     courses_Course, 44, 5, None, u' 1', u'', u'30', 0, 1,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(265, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 44,
                     date(2014, 12, 31), None, None, None, None, u'appypdf',
                     courses_Course, 44, 5, None, u' 2', u'', u'30', 0, 2,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(266, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 44,
                     date(2015, 1, 14), None, None, None, None, u'appypdf',
                     courses_Course, 44, 5, None, u' 3', u'', u'30', 0, 3,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(267, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 44,
                     date(2015, 1, 28), None, None, None, None, u'appypdf',
                     courses_Course, 44, 5, None, u' 4', u'', u'30', 0, 4,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(268, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 44,
                     date(2015, 2, 11), None, None, None, None, u'appypdf',
                     courses_Course, 44, 5, None, u' 5', u'', u'30', 0, 5,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(269, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 44,
                     date(2015, 2, 25), None, None, None, None, u'appypdf',
                     courses_Course, 44, 5, None, u' 6', u'', u'30', 0, 6,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(270, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 44,
                     date(2015, 3, 11), None, None, None, None, u'appypdf',
                     courses_Course, 44, 5, None, u' 7', u'', u'30', 0, 7,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(271, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 44,
                     date(2015, 3, 25), None, None, None, None, u'appypdf',
                     courses_Course, 44, 5, None, u' 8', u'', u'30', 0, 8,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(272, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 44,
                     date(2015, 4, 8), None, None, None, None, u'appypdf',
                     courses_Course, 44, 5, None, u' 9', u'', u'30', 0, 9,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(273, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 5), 44,
                     date(2015, 4, 22), None, None, None, None, u'appypdf',
                     courses_Course, 44, 5, None, u' 10', u'', u'30', 0, 10,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(274, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 6), 49,
                     date(2014, 11, 4), None, None, None, None, u'appypdf',
                     courses_Course, 49, 4, None, u' 1', u'', u'30', 0, 1,
                     u'30', 4, False, None, u'50', '15.00'))
loader.save(
    create_cal_event(275, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 6), 49,
                     date(2014, 11, 12), None, None, None, None, u'appypdf',
                     courses_Course, 49, 4, None, u' 2', u'', u'30', 0, 2,
                     u'30', 4, False, None, u'60', '20.00'))
loader.save(
    create_cal_event(276, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 6), 49,
                     date(2014, 11, 19), None, None, None, None, u'appypdf',
                     courses_Course, 49, 4, None, u' 3', u'', u'30', 0, 3,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(277, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 6), 49,
                     date(2014, 11, 26), None, None, None, None, u'appypdf',
                     courses_Course, 49, 4, None, u' 4', u'', u'30', 0, 4,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(278, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 6), 49,
                     date(2014, 12, 3), None, None, None, None, u'appypdf',
                     courses_Course, 49, 4, None, u' 5', u'', u'30', 0, 5,
                     u'30', 4, False, None, u'50', '5.00'))
loader.save(
    create_cal_event(279, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 6), 49,
                     date(2014, 12, 10), None, None, None, None, u'appypdf',
                     courses_Course, 49, 4, None, u' 6', u'', u'30', 0, 6,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(280, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 6), 49,
                     date(2014, 12, 17), None, None, None, None, u'appypdf',
                     courses_Course, 49, 4, None, u' 7', u'', u'30', 0, 7,
                     u'30', 4, False, None, u'60', None))
loader.save(
    create_cal_event(281, dt(2018, 12, 22, 12, 25,
                             12), dt(2018, 12, 22, 12, 25, 6), 49,
                     date(2014, 12, 24), None, None, None, None, u'appypdf',
                     courses_Course, 49, 4, None, u' 8', u'', u'30', 0, 8,
                     u'30', 4, False, None, u'50', '15.00'))
loader.save(
    create_cal_event(282, dt(2018, 12, 22, 12, 25,
                             13), dt(2018, 12, 22, 12, 25, 6), 49,
                     date(2014, 12, 31), None, None, None, None, u'appypdf',
                     courses_Course, 49, 4, None, u' 9', u'', u'30', 0, 9,
                     u'30', 4, False, None, u'50', '20.00'))
loader.save(
    create_cal_event(283, dt(2018, 12, 22, 12, 25,
                             13), dt(2018, 12, 22, 12, 25, 6), 49,
                     date(2015, 1, 7), None, None, None, None, u'appypdf',
                     courses_Course, 49, 4, None, u' 10', u'', u'30', 0, 10,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(284, dt(2018, 12, 22, 12, 25,
                             13), dt(2018, 12, 22, 12, 25, 7), 50,
                     date(2014, 11, 5), None, None, None, None, u'appypdf',
                     courses_Course, 50, 5, None, u' 1', u'', u'30', 0, 1,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(285, dt(2018, 12, 22, 12, 25,
                             13), dt(2018, 12, 22, 12, 25, 7), 50,
                     date(2014, 11, 12), None, None, None, None, u'appypdf',
                     courses_Course, 50, 5, None, u' 2', u'', u'30', 0, 2,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(286, dt(2018, 12, 22, 12, 25,
                             13), dt(2018, 12, 22, 12, 25, 7), 50,
                     date(2014, 11, 19), None, None, None, None, u'appypdf',
                     courses_Course, 50, 5, None, u' 3', u'', u'30', 0, 3,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(287, dt(2018, 12, 22, 12, 25,
                             13), dt(2018, 12, 22, 12, 25, 7), 50,
                     date(2014, 11, 26), None, None, None, None, u'appypdf',
                     courses_Course, 50, 5, None, u' 4', u'', u'30', 0, 4,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(288, dt(2018, 12, 22, 12, 25,
                             13), dt(2018, 12, 22, 12, 25, 7), 50,
                     date(2014, 12, 3), None, None, None, None, u'appypdf',
                     courses_Course, 50, 5, None, u' 5', u'', u'30', 0, 5,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(289, dt(2018, 12, 22, 12, 25,
                             13), dt(2018, 12, 22, 12, 25, 7), 50,
                     date(2014, 12, 10), None, None, None, None, u'appypdf',
                     courses_Course, 50, 5, None, u' 6', u'', u'30', 0, 6,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(290, dt(2018, 12, 22, 12, 25,
                             13), dt(2018, 12, 22, 12, 25, 7), 50,
                     date(2014, 12, 17), None, None, None, None, u'appypdf',
                     courses_Course, 50, 5, None, u' 7', u'', u'30', 0, 7,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(291, dt(2018, 12, 22, 12, 25,
                             13), dt(2018, 12, 22, 12, 25, 7), 50,
                     date(2014, 12, 24), None, None, None, None, u'appypdf',
                     courses_Course, 50, 5, None, u' 8', u'', u'30', 0, 8,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(292, dt(2018, 12, 22, 12, 25,
                             13), dt(2018, 12, 22, 12, 25, 7), 50,
                     date(2014, 12, 31), None, None, None, None, u'appypdf',
                     courses_Course, 50, 5, None, u' 9', u'', u'30', 0, 9,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(293, dt(2018, 12, 22, 12, 25,
                             13), dt(2018, 12, 22, 12, 25, 7), 50,
                     date(2015, 1, 7), None, None, None, None, u'appypdf',
                     courses_Course, 50, 5, None, u' 10', u'', u'30', 0, 10,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(294, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 3),
                     time(8, 30, 0), None, time(9, 30, 0), None, u'appypdf',
                     None, None, 3, None, u'Diner', u'', u'10', 0, None, u'30',
                     2, False, None, u'10', None))
loader.save(
    create_cal_event(295, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 4),
                     time(9, 40, 0), None, time(10, 55, 0), None, u'appypdf',
                     None, None, 2, None, u'Abendessen', u'', u'20', 0, None,
                     u'30', 3, False, None, u'20', None))
loader.save(
    create_cal_event(296, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 5),
                     time(10, 20, 0), None, time(11, 50, 0), None, u'appypdf',
                     None, None, 1, None, u'Breakfast', u'', u'30', 0, None,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(297, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 5),
                     time(11, 10, 0), None, time(12, 55, 0), None, u'appypdf',
                     None, None, 3, None, u'Rencontre', u'', u'10', 0, None,
                     u'30', 5, False, None, u'70', None))
loader.save(
    create_cal_event(298, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 6),
                     time(13, 30, 0), None, time(15, 30, 0), None, u'appypdf',
                     None, None, 2, None, u'Beratung', u'', u'20', 0, None,
                     u'30', 2, False, None, u'60', None))
loader.save(
    create_cal_event(299, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 7),
                     time(8, 30, 0), None, time(11, 0, 0), None, u'appypdf',
                     None, None, 1, None, u'Seminar', u'', u'30', 0, None,
                     u'30', 3, False, None, u'10', None))
loader.save(
    create_cal_event(300, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 7),
                     time(9, 40, 0), None, time(12, 40, 0), None, u'appypdf',
                     None, None, 3, None, u'Evaluation', u'', u'10', 0, None,
                     u'30', 4, False, None, u'20', None))
loader.save(
    create_cal_event(301, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 8),
                     time(10, 20, 0), None, time(11, 20, 0), None, u'appypdf',
                     None, None, 2, None, u'Erstgespr\xe4ch', u'', u'20', 0,
                     None, u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(302, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 9),
                     time(11, 10, 0), None, time(12, 25, 0), None, u'appypdf',
                     None, None, 1, None, u'Interview', u'', u'30', 0, None,
                     u'30', 2, False, None, u'70', None))
loader.save(
    create_cal_event(303, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 9),
                     time(13, 30, 0), None, time(15, 0, 0), None, u'appypdf',
                     None, None, 3, None, u'Diner', u'', u'10', 0, None, u'30',
                     3, False, None, u'60', None))
loader.save(
    create_cal_event(304, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 10),
                     time(8, 30, 0), None, time(10, 15, 0), None, u'appypdf',
                     None, None, 2, None, u'Abendessen', u'', u'20', 0, None,
                     u'30', 4, False, None, u'10', None))
loader.save(
    create_cal_event(305, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 11),
                     time(9, 40, 0), None, time(11, 40, 0), None, u'appypdf',
                     None, None, 1, None, u'Breakfast', u'', u'30', 0, None,
                     u'30', 5, False, None, u'20', None))
loader.save(
    create_cal_event(306, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 11),
                     time(10, 20, 0), None, time(12, 50, 0), None, u'appypdf',
                     None, None, 3, None, u'Rencontre', u'', u'10', 0, None,
                     u'30', 2, False, None, u'50', None))
loader.save(
    create_cal_event(307, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 12),
                     time(11, 10, 0), None, time(14, 10, 0), None, u'appypdf',
                     None, None, 2, None, u'Beratung', u'', u'20', 0, None,
                     u'30', 3, False, None, u'70', None))
loader.save(
    create_cal_event(308, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 13),
                     time(13, 30, 0), None, time(14, 30, 0), None, u'appypdf',
                     None, None, 1, None, u'Seminar', u'', u'30', 0, None,
                     u'30', 4, False, None, u'60', None))
loader.save(
    create_cal_event(309, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 13),
                     time(8, 30, 0), None, time(9, 45, 0), None, u'appypdf',
                     None, None, 3, None, u'Evaluation', u'', u'10', 0, None,
                     u'30', 5, False, None, u'10', None))
loader.save(
    create_cal_event(310, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 14),
                     time(9, 40, 0), None, time(11, 10, 0), None, u'appypdf',
                     None, None, 2, None, u'Erstgespr\xe4ch', u'', u'20', 0,
                     None, u'30', 2, False, None, u'20', None))
loader.save(
    create_cal_event(311, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 15),
                     time(10, 20, 0), None, time(12, 5, 0), None, u'appypdf',
                     None, None, 1, None, u'Interview', u'', u'30', 0, None,
                     u'30', 3, False, None, u'50', None))
loader.save(
    create_cal_event(312, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 15),
                     time(11, 10, 0), None, time(13, 10, 0), None, u'appypdf',
                     None, None, 3, None, u'Diner', u'', u'10', 0, None, u'30',
                     4, False, None, u'70', None))
loader.save(
    create_cal_event(313, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 16),
                     time(13, 30, 0), None, time(16, 0, 0), None, u'appypdf',
                     None, None, 2, None, u'Abendessen', u'', u'20', 0, None,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(314, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 17),
                     time(8, 30, 0), None, time(11, 30, 0), None, u'appypdf',
                     None, None, 1, None, u'Breakfast', u'', u'30', 0, None,
                     u'30', 2, False, None, u'10', None))
loader.save(
    create_cal_event(315, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 17),
                     time(9, 40, 0), None, time(10, 40, 0), None, u'appypdf',
                     None, None, 3, None, u'Rencontre', u'', u'10', 0, None,
                     u'30', 3, False, None, u'20', None))
loader.save(
    create_cal_event(316, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 18),
                     time(10, 20, 0), None, time(11, 35, 0), None, u'appypdf',
                     None, None, 2, None, u'Beratung', u'', u'20', 0, None,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(317, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 19),
                     time(11, 10, 0), None, time(12, 40, 0), None, u'appypdf',
                     None, None, 1, None, u'Seminar', u'', u'30', 0, None,
                     u'30', 5, False, None, u'70', None))
loader.save(
    create_cal_event(318, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 19),
                     time(13, 30, 0), None, time(15, 15, 0), None, u'appypdf',
                     None, None, 3, None, u'Evaluation', u'', u'10', 0, None,
                     u'30', 2, False, None, u'60', None))
loader.save(
    create_cal_event(319, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 20),
                     time(8, 30, 0), None, time(10, 30, 0), None, u'appypdf',
                     None, None, 2, None, u'Erstgespr\xe4ch', u'', u'20', 0,
                     None, u'30', 3, False, None, u'10', None))
loader.save(
    create_cal_event(320, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 21),
                     time(9, 40, 0), None, time(12, 10, 0), None, u'appypdf',
                     None, None, 1, None, u'Interview', u'', u'30', 0, None,
                     u'30', 4, False, None, u'20', None))
loader.save(
    create_cal_event(321, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 21),
                     time(10, 20, 0), None, time(13, 20, 0), None, u'appypdf',
                     None, None, 3, None, u'Diner', u'', u'10', 0, None, u'30',
                     5, False, None, u'50', None))
loader.save(
    create_cal_event(322, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 22),
                     time(11, 10, 0), None, time(12, 10, 0), None, u'appypdf',
                     None, None, 2, None, u'Abendessen', u'', u'20', 0, None,
                     u'30', 2, False, None, u'70', None))
loader.save(
    create_cal_event(323, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 23),
                     time(13, 30, 0), None, time(14, 45, 0), None, u'appypdf',
                     None, None, 1, None, u'Breakfast', u'', u'30', 0, None,
                     u'30', 3, False, None, u'60', None))
loader.save(
    create_cal_event(324, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 23),
                     time(8, 30, 0), None, time(10, 0, 0), None, u'appypdf',
                     None, None, 3, None, u'Rencontre', u'', u'10', 0, None,
                     u'30', 4, False, None, u'10', None))
loader.save(
    create_cal_event(325, dt(2018, 12, 22, 12, 25, 41),
                     dt(2018, 12, 22, 12, 25, 41), None, date(2015, 5, 24),
                     time(9, 40, 0), None, time(11, 25, 0), None, u'appypdf',
                     None, None, 2, None, u'Beratung', u'', u'20', 0, None,
                     u'30', 5, False, None, u'20', None))
loader.save(
    create_cal_event(326, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 5, 25),
                     time(10, 20, 0), None, time(12, 20, 0), None, u'appypdf',
                     None, None, 1, None, u'Seminar', u'', u'30', 0, None,
                     u'30', 2, False, None, u'50', None))
loader.save(
    create_cal_event(327, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 5, 25),
                     time(11, 10, 0), None, time(13, 40, 0), None, u'appypdf',
                     None, None, 3, None, u'Evaluation', u'', u'10', 0, None,
                     u'30', 3, False, None, u'70', None))
loader.save(
    create_cal_event(328, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 5, 26),
                     time(13, 30, 0), None, time(16, 30, 0), None, u'appypdf',
                     None, None, 2, None, u'Erstgespr\xe4ch', u'', u'20', 0,
                     None, u'30', 4, False, None, u'60', None))
loader.save(
    create_cal_event(329, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 5, 27),
                     time(8, 30, 0), None, time(9, 30, 0), None, u'appypdf',
                     None, None, 1, None, u'Interview', u'', u'30', 0, None,
                     u'30', 5, False, None, u'10', None))
loader.save(
    create_cal_event(330, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 5, 27),
                     time(9, 40, 0), None, time(10, 55, 0), None, u'appypdf',
                     None, None, 3, None, u'Diner', u'', u'10', 0, None, u'30',
                     2, False, None, u'20', None))
loader.save(
    create_cal_event(331, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 5, 28),
                     time(10, 20, 0), None, time(11, 50, 0), None, u'appypdf',
                     None, None, 2, None, u'Abendessen', u'', u'20', 0, None,
                     u'30', 3, False, None, u'50', None))
loader.save(
    create_cal_event(332, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 5, 29),
                     time(11, 10, 0), None, time(12, 55, 0), None, u'appypdf',
                     None, None, 1, None, u'Breakfast', u'', u'30', 0, None,
                     u'30', 4, False, None, u'70', None))
loader.save(
    create_cal_event(333, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 5, 29),
                     time(13, 30, 0), None, time(15, 30, 0), None, u'appypdf',
                     None, None, 3, None, u'Rencontre', u'', u'10', 0, None,
                     u'30', 5, False, None, u'60', None))
loader.save(
    create_cal_event(334, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 5, 30),
                     time(8, 30, 0), None, time(11, 0, 0), None, u'appypdf',
                     None, None, 2, None, u'Beratung', u'', u'20', 0, None,
                     u'30', 2, False, None, u'10', None))
loader.save(
    create_cal_event(335, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 5, 31),
                     time(9, 40, 0), None, time(12, 40, 0), None, u'appypdf',
                     None, None, 1, None, u'Seminar', u'', u'30', 0, None,
                     u'30', 3, False, None, u'20', None))
loader.save(
    create_cal_event(336, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 5, 31),
                     time(10, 20, 0), None, time(11, 20, 0), None, u'appypdf',
                     None, None, 3, None, u'Evaluation', u'', u'10', 0, None,
                     u'30', 4, False, None, u'50', None))
loader.save(
    create_cal_event(337, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 1),
                     time(11, 10, 0), None, time(12, 25, 0), None, u'appypdf',
                     None, None, 2, None, u'Erstgespr\xe4ch', u'', u'20', 0,
                     None, u'30', 5, False, None, u'70', None))
loader.save(
    create_cal_event(338, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 2),
                     time(13, 30, 0), None, time(15, 0, 0), None, u'appypdf',
                     None, None, 1, None, u'Interview', u'', u'30', 0, None,
                     u'30', 2, False, None, u'60', None))
loader.save(
    create_cal_event(339, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 2),
                     time(8, 30, 0), None, time(10, 15, 0), None, u'appypdf',
                     None, None, 3, None, u'Diner', u'', u'10', 0, None, u'30',
                     3, False, None, u'10', None))
loader.save(
    create_cal_event(340, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 3),
                     time(9, 40, 0), None, time(11, 40, 0), None, u'appypdf',
                     None, None, 2, None, u'Abendessen', u'', u'20', 0, None,
                     u'30', 4, False, None, u'20', None))
loader.save(
    create_cal_event(341, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 4),
                     time(10, 20, 0), None, time(12, 50, 0), None, u'appypdf',
                     None, None, 1, None, u'Breakfast', u'', u'30', 0, None,
                     u'30', 5, False, None, u'50', None))
loader.save(
    create_cal_event(342, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 4),
                     time(11, 10, 0), None, time(14, 10, 0), None, u'appypdf',
                     None, None, 3, None, u'Rencontre', u'', u'10', 0, None,
                     u'30', 2, False, None, u'70', None))
loader.save(
    create_cal_event(343, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 5),
                     time(13, 30, 0), None, time(14, 30, 0), None, u'appypdf',
                     None, None, 2, None, u'Beratung', u'', u'20', 0, None,
                     u'30', 3, False, None, u'60', None))
loader.save(
    create_cal_event(344, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 6),
                     time(8, 30, 0), None, time(9, 45, 0), None, u'appypdf',
                     None, None, 1, None, u'Seminar', u'', u'30', 0, None,
                     u'30', 4, False, None, u'10', None))
loader.save(
    create_cal_event(345, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 6),
                     time(9, 40, 0), None, time(11, 10, 0), None, u'appypdf',
                     None, None, 3, None, u'Evaluation', u'', u'10', 0, None,
                     u'30', 5, False, None, u'20', None))
loader.save(
    create_cal_event(346, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 7),
                     time(10, 20, 0), None, time(12, 5, 0), None, u'appypdf',
                     None, None, 2, None, u'Erstgespr\xe4ch', u'', u'20', 0,
                     None, u'30', 2, False, None, u'50', None))
loader.save(
    create_cal_event(347, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 8),
                     time(11, 10, 0), None, time(13, 10, 0), None, u'appypdf',
                     None, None, 1, None, u'Interview', u'', u'30', 0, None,
                     u'30', 3, False, None, u'70', None))
loader.save(
    create_cal_event(348, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 8),
                     time(13, 30, 0), None, time(16, 0, 0), None, u'appypdf',
                     None, None, 3, None, u'Diner', u'', u'10', 0, None, u'30',
                     4, False, None, u'60', None))
loader.save(
    create_cal_event(349, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 9),
                     time(8, 30, 0), None, time(11, 30, 0), None, u'appypdf',
                     None, None, 2, None, u'Abendessen', u'', u'20', 0, None,
                     u'30', 5, False, None, u'10', None))
loader.save(
    create_cal_event(350, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 10),
                     time(9, 40, 0), None, time(10, 40, 0), None, u'appypdf',
                     None, None, 1, None, u'Breakfast', u'', u'30', 0, None,
                     u'30', 2, False, None, u'20', None))
loader.save(
    create_cal_event(351, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 10),
                     time(10, 20, 0), None, time(11, 35, 0), None, u'appypdf',
                     None, None, 3, None, u'Rencontre', u'', u'10', 0, None,
                     u'30', 3, False, None, u'50', None))
loader.save(
    create_cal_event(352, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 11),
                     time(11, 10, 0), None, time(12, 40, 0), None, u'appypdf',
                     None, None, 2, None, u'Beratung', u'', u'20', 0, None,
                     u'30', 4, False, None, u'70', None))
loader.save(
    create_cal_event(353, dt(2018, 12, 22, 12, 25, 42),
                     dt(2018, 12, 22, 12, 25, 42), None, date(2015, 6, 12),
                     time(13, 30, 0), None, time(15, 15, 0), None, u'appypdf',
                     None, None, 1, None, u'Seminar', u'', u'30', 0, None,
                     u'30', 5, False, None, u'60', None))

loader.flush_deferred_objects()
