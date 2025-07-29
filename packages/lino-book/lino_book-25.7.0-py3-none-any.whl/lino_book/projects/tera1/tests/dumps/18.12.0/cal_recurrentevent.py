# -*- coding: UTF-8 -*-
logger.info("Loading 15 objects to table cal_recurrentevent...")
# fields: id, start_date, start_time, end_date, end_time, name, user, every_unit, every, monday, tuesday, wednesday, thursday, friday, saturday, sunday, max_events, event_type, description
loader.save(
    create_cal_recurrentevent(1, date(2013, 1, 1), None, None, None,
                              ["New Year's Day", 'Neujahr', "Jour de l'an"],
                              None, u'Y', 1, True, True, True, True, True,
                              True, True, None, 1, u''))
loader.save(
    create_cal_recurrentevent(
        2, date(2013, 5, 1), None, None, None,
        ["International Workers' Day", 'Tag der Arbeit', 'Premier Mai'], None,
        u'Y', 1, True, True, True, True, True, True, True, None, 1, u''))
loader.save(
    create_cal_recurrentevent(
        3, date(2013, 7, 21), None, None, None,
        ['National Day', 'Nationalfeiertag', 'F\xeate nationale'], None, u'Y',
        1, True, True, True, True, True, True, True, None, 1, u''))
loader.save(
    create_cal_recurrentevent(
        4, date(2013, 8, 15), None, None, None,
        ['Assumption of Mary', 'Mari\xe4 Himmelfahrt', 'Assomption de Marie'],
        None, u'Y', 1, True, True, True, True, True, True, True, None, 1, u''))
loader.save(
    create_cal_recurrentevent(5, date(2013, 10, 31), None, None, None, [
        "All Souls' Day", 'Allerseelen',
        'Comm\xe9moration des fid\xe8les d\xe9funts'
    ], None, u'Y', 1, True, True, True, True, True, True, True, None, 1, u''))
loader.save(
    create_cal_recurrentevent(
        6, date(2013, 11, 1), None, None, None,
        ["All Saints' Day", 'Allerheiligen', 'Toussaint'], None, u'Y', 1, True,
        True, True, True, True, True, True, None, 1, u''))
loader.save(
    create_cal_recurrentevent(
        7, date(2013, 11, 11), None, None, None,
        ['Armistice with Germany', 'Waffenstillstand', 'Armistice'], None,
        u'Y', 1, True, True, True, True, True, True, True, None, 1, u''))
loader.save(
    create_cal_recurrentevent(8, date(2013, 12, 25), None, None, None,
                              ['Christmas', 'Weihnachten', 'No\xebl'], None,
                              u'Y', 1, True, True, True, True, True, True,
                              True, None, 1, u''))
loader.save(
    create_cal_recurrentevent(9, date(2013, 3, 31), None, None, None,
                              ['Easter sunday', 'Ostersonntag', 'P\xe2ques'],
                              None, u'E', 1, False, False, False, False, False,
                              False, False, None, 1, u''))
loader.save(
    create_cal_recurrentevent(
        10, date(2013, 4, 1), None, None, None,
        ['Easter monday', 'Ostermontag', 'Lundi de P\xe2ques'], None, u'E', 1,
        False, False, False, False, False, False, False, None, 1, u''))
loader.save(
    create_cal_recurrentevent(
        11, date(2013, 5, 9), None, None, None,
        ['Ascension of Jesus', 'Christi Himmelfahrt', 'Ascension'], None, u'E',
        1, False, False, False, False, False, False, False, None, 1, u''))
loader.save(
    create_cal_recurrentevent(12, date(2013, 5, 20), None, None, None,
                              ['Pentecost', 'Pfingsten', 'Pentec\xf4te'], None,
                              u'E', 1, False, False, False, False, False,
                              False, False, None, 1, u''))
loader.save(
    create_cal_recurrentevent(13, date(2013, 3, 29), None, None, None,
                              ['Good Friday', 'Karfreitag', 'Vendredi Saint'],
                              None, u'E', 1, False, False, False, False, False,
                              False, False, None, 1, u''))
loader.save(
    create_cal_recurrentevent(
        14, date(2013, 2, 13), None, None, None,
        ['Ash Wednesday', 'Aschermittwoch', 'Mercredi des Cendres'], None,
        u'E', 1, False, False, False, False, False, False, False, None, 1,
        u''))
loader.save(
    create_cal_recurrentevent(
        15, date(2013, 2, 11), None, None, None,
        ['Rosenmontag', 'Rosenmontag', 'Lundi de carnaval'], None, u'E', 1,
        False, False, False, False, False, False, False, None, 1, u''))

loader.flush_deferred_objects()
