# -*- coding: utf-8 -*-
# Copyright 2013-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Tests about generating automatic calendar entries of a course.  Look at the
source code!

To run just this test::

  $ go roger
  $ python manage.py test tests.test_faggio

"""

import logging

from lino.api.shell import cal
from lino.api.shell import courses
from lino.api.shell import users
from lino.api.shell import system
from lino.api import rt
from django.conf import settings

from lino.utils.djangotest import RemoteAuthTestCase
from lino.utils import i2d
from lino.modlib.users.choicelists import UserTypes
from lino.utils.instantiator import create_row as create


def update_row(obj, **kwargs):
    for k, v in kwargs.items():
        setattr(obj, k, v)
    obj.full_clean()
    obj.save()


class QuickTest(RemoteAuthTestCase):
    maxDiff = None

    def check_update(self,
                     obj,
                     msg1='',
                     msg2='',
                     debug=False,
                     column_names="when_text state summary"):
        # utility function that runs update_events and checks whether
        # info_message and output of cal.EntriesByController are as
        # expected:
        ses = rt.login('robin')
        with ses.capture_logger(logging.DEBUG) as out:
            res = ses.run(obj.do_update_events)
        self.assertEqual(res['success'], True)
        s1 = out.getvalue()
        if debug:
            print(s1)
        ar = ses.spawn(cal.EntriesByController, master_instance=obj)
        s2 = ar.to_rst(column_names=column_names, nosummary=True)
        if debug:
            print(s2)
        self.assertEquivalent(msg1.strip(), s1.strip())
        self.assertEquivalent(msg2.strip(), s2.strip())

    def test01(self):
        # Create a room, event type, series and a course

        room = create(cal.Room, name="First Room")
        lesson = create(cal.EventType, name="Lesson", event_label="Lesson")
        line = create(courses.Line, name="First Line", event_type=lesson)
        obj = create(courses.Course,
                     line=line,
                     room=room,
                     max_events=5,
                     monday=True,
                     state=courses.CourseStates.active,
                     start_date=i2d(20140110))
        self.assertEqual(str(obj), "Activity #1")

        # self.assertEqual(settings.SITE.kernel.site, settings.SITE)
        # self.assertEqual(settings.SITE, dd.site)
        # self.assertEqual(settings.SITE.plugins, dd.plugins)
        # self.assertEqual(settings.SITE.plugins.extjs, dd.plugins.extjs)

        # settings.SITE.verbose_client_info_message = True
        users.User(username="robin", user_type=UserTypes.admin,
                   language="en").save()
        ses = rt.login('robin')

        # Run do_update_events a first time
        self.check_update(
            obj, """
Run Update calendar for Activity #1...
Generating events between 2014-01-13 and 2020-05-22 (max. 5).
Update presences for Activity #1 Lesson 1 : 0 created, 0 unchanged, 0 deleted.
Update presences for Activity #1 Lesson 2 : 0 created, 0 unchanged, 0 deleted.
Update presences for Activity #1 Lesson 3 : 0 created, 0 unchanged, 0 deleted.
Update presences for Activity #1 Lesson 4 : 0 created, 0 unchanged, 0 deleted.
Update presences for Activity #1 Lesson 5 : 0 created, 0 unchanged, 0 deleted.
5 row(s) have been updated.
""", """
================ =========== ===================
 When             State       Short description
---------------- ----------- -------------------
 Mon 10/02/2014   Suggested   Lesson 5
 Mon 03/02/2014   Suggested   Lesson 4
 Mon 27/01/2014   Suggested   Lesson 3
 Mon 20/01/2014   Suggested   Lesson 2
 Mon 13/01/2014   Suggested   Lesson 1
================ =========== ===================
""")

        # Decrease max_events and check whether the superfluous events
        # get removed.

        obj.max_events = 3
        self.check_update(
            obj, """
Run Update calendar for Activity #1...
Generating events between 2014-01-13 and 2020-05-22 (max. 3).
2 row(s) have been updated.""", """
================ =========== ===================
 When             State       Short description
---------------- ----------- -------------------
 Mon 27/01/2014   Suggested   Lesson 3
 Mon 20/01/2014   Suggested   Lesson 2
 Mon 13/01/2014   Suggested   Lesson 1
================ =========== ===================
""")

        # Run do_update_events for 5 events a second time
        obj.max_events = 5
        self.check_update(
            obj, """
Run Update calendar for Activity #1...
Generating events between 2014-01-13 and 2020-05-22 (max. 5).
Update presences for Activity #1 Lesson 4 : 0 created, 0 unchanged, 0 deleted.
Update presences for Activity #1 Lesson 5 : 0 created, 0 unchanged, 0 deleted.
2 row(s) have been updated.""", """
================ =========== ===================
 When             State       Short description
---------------- ----------- -------------------
 Mon 10/02/2014   Suggested   Lesson 5
 Mon 03/02/2014   Suggested   Lesson 4
 Mon 27/01/2014   Suggested   Lesson 3
 Mon 20/01/2014   Suggested   Lesson 2
 Mon 13/01/2014   Suggested   Lesson 1
================ =========== ===================
""")

        # Now we want to skip the 2nd event.  We click on "Move next"
        # on this event. Lino then moves all subsequent events
        # accordingly.

        ar = cal.EntriesByController.request(
            master_instance=obj, known_values=dict(start_date=i2d(20140120)))
        e = ar.data_iterator[0]
        self.assertEqual(e.state, cal.EntryStates.suggested)
        #
        with ses.capture_logger(logging.DEBUG) as out:
            res = ses.run(e.move_next)
        # The event is now in state "draft" because it has been
        # modified by the user.
        output = out.getvalue().strip()

        self.assertEqual(e.state, cal.EntryStates.draft)

        self.assertEqual(res['success'], True)
        expected = """\
Run Move down for Activity #1 Lesson 2...
Generating events between 2014-01-13 and 2020-05-22 (max. 5).
Lesson 2 has been moved from 2014-01-20 to 2014-01-27.
1 row(s) have been updated."""
        self.assertEqual(output, expected)

        # e.full_clean()
        # e.save()

        self.check_update(
            obj, """
Run Update calendar for Activity #1...
Generating events between 2014-01-13 and 2020-05-22 (max. 5).
Lesson 2 has been moved from 2014-01-20 to 2014-01-27.
0 row(s) have been updated.
""", """
================ =========== ===================
 When             State       Short description
---------------- ----------- -------------------
 Mon 17/02/2014   Suggested   Lesson 5
 Mon 10/02/2014   Suggested   Lesson 4
 Mon 03/02/2014   Suggested   Lesson 3
 Mon 27/01/2014   Draft       Lesson 2
 Mon 13/01/2014   Suggested   Lesson 1
================ =========== ===================
""")

        # Now we imagine that February 3 is the National Day in our
        # country and that we create the rule for this only now.  So
        # we have a conflict because Lino created an appointment on
        # that date. Of course the National Day must *not* move to an
        # alternative date.

        et = create(cal.EventType, name="Holiday", all_rooms=True)
        national_day = create(cal.RecurrentEvent,
                              name="National Day",
                              event_type=et,
                              start_date=i2d(20140203),
                              every_unit=cal.Recurrences.yearly)

        with ses.capture_logger(logging.DEBUG) as out:
            res = ses.run(national_day.do_update_events)
        self.assertEqual(res['success'], True)
        output = out.getvalue().strip()  # s['info_message']
        expected = """\
Run Update calendar for National Day...
Generating events between 2014-02-03 and 2020-05-22 (max. 72).
Reached upper date limit 2020-05-22 for 7
Update presences for Recurring event #1 National Day : 0 created, 0 unchanged, 0 deleted.
Update presences for Recurring event #1 National Day : 0 created, 0 unchanged, 0 deleted.
Update presences for Recurring event #1 National Day : 0 created, 0 unchanged, 0 deleted.
Update presences for Recurring event #1 National Day : 0 created, 0 unchanged, 0 deleted.
Update presences for Recurring event #1 National Day : 0 created, 0 unchanged, 0 deleted.
Update presences for Recurring event #1 National Day : 0 created, 0 unchanged, 0 deleted.
Update presences for Recurring event #1 National Day : 0 created, 0 unchanged, 0 deleted.
7 row(s) have been updated."""
        self.assertEqual(output, expected)
        ar = ses.spawn(cal.EntriesByController, master_instance=national_day)
        s = ar.to_rst(column_names="when_text state", nosummary=True)
        # print s
        self.assertEqual(
            s, """\
================ ===========
 When             State
---------------- -----------
 Mon 03/02/2020   Suggested
 Sun 03/02/2019   Suggested
 Sat 03/02/2018   Suggested
 Fri 03/02/2017   Suggested
 Wed 03/02/2016   Suggested
 Tue 03/02/2015   Suggested
 Mon 03/02/2014   Suggested
================ ===========

""")

        # the national day 2014 is now conflicting with our Lesson 3:
        ce = ar[6]
        self.assertEqual(ce.summary, "National Day")
        self.assertEqual(ce.start_date.year, 2014)
        ar = ses.spawn(cal.ConflictingEvents, master_instance=ce)
        s = ar.to_rst(column_names="when_text state auto_type")
        # print(s)
        self.assertEquivalent(
            s, """\
================ =========== =====
 When             State       No.
---------------- ----------- -----
 Mon 03/02/2014   Suggested   3
================ =========== =====
""")

        # Delete all lessons and start again with a virgin series. Now Lino
        # won't put a lesson to February 3 because it is the national day.

        cal.Event.objects.filter(event_type=lesson).delete()

        self.check_update(
            obj, """
Run Update calendar for Activity #1...
Generating events between 2014-01-13 and 2020-05-22 (max. 5).
Lesson 4 wants 2014-02-03 but conflicts with <QuerySet [Event #8 ('Recurring event #1 National Day')]>, moving to 2014-02-10.
Update presences for Activity #1 Lesson 1 : 0 created, 0 unchanged, 0 deleted.
Update presences for Activity #1 Lesson 2 : 0 created, 0 unchanged, 0 deleted.
Update presences for Activity #1 Lesson 3 : 0 created, 0 unchanged, 0 deleted.
Update presences for Activity #1 Lesson 4 : 0 created, 0 unchanged, 0 deleted.
Update presences for Activity #1 Lesson 5 : 0 created, 0 unchanged, 0 deleted.
5 row(s) have been updated.
""", """
================ =========== ===================
 When             State       Short description
---------------- ----------- -------------------
 Mon 17/02/2014   Suggested   Lesson 5
 Mon 10/02/2014   Suggested   Lesson 4
 Mon 27/01/2014   Suggested   Lesson 3
 Mon 20/01/2014   Suggested   Lesson 2
 Mon 13/01/2014   Suggested   Lesson 1
================ =========== ===================
""")

        # We move the first lesson one week down (i.e. later) and check whether
        # remaining entries get adapted. We manually set the state to draft
        # (this is automatically done when using the web ui).

        e = cal.Event.objects.get(event_type=lesson, auto_type=1)
        e.start_date = i2d(20140120)
        e.state = cal.EntryStates.draft
        e.full_clean()
        e.save()

        self.check_update(
            obj, """
Run Update calendar for Activity #1...
Generating events between 2014-01-13 and 2020-05-22 (max. 5).
Lesson 1 has been moved from 2014-01-13 to 2014-01-20.
Lesson 3 wants 2014-02-03 but conflicts with <QuerySet [Event #8
('Recurring event #1 National Day')]>, moving to 2014-02-10.
0 row(s) have been updated.
        """, """
================ =========== ===================
 When             State       Short description
---------------- ----------- -------------------
 Mon 24/02/2014   Suggested   Lesson 5
 Mon 17/02/2014   Suggested   Lesson 4
 Mon 10/02/2014   Suggested   Lesson 3
 Mon 27/01/2014   Suggested   Lesson 2
 Mon 20/01/2014   Draft       Lesson 1
================ =========== ===================
""")

        # We cancel the third lesson, and Lino then adds a new one. The canceled
        # lesson is still linked to the activity, but no longer participates in
        # the series of generated events (because auto_type is empty). The
        # summary field becomes editable.

        e = cal.Event.objects.get(event_type=lesson, auto_type=3)
        # self.assertEqual(e.disabled_fields(ar), {'create_mail', 'do_clear_cache', 'summary', 'assign_to_me', 'take'})
        self.assertIn("summary", e.disabled_fields(ar))
        e.state = cal.EntryStates.cancelled
        e.auto_type = None
        e.full_clean()
        e.save()
        # self.assertEqual(e.disabled_fields(ar), {'move_next', 'take', 'reset_event',
        #     'do_clear_cache', 'create_mail', 'assign_to_me', 'update_events'})
        self.assertNotIn("summary", e.disabled_fields(ar))
        the_cancelled_lesson = e

        self.check_update(obj,
                          """
Run Update calendar for Activity #1...
Generating events between 2014-01-13 and 2020-05-22 (max. 5).
Lesson 1 has been moved from 2014-01-13 to 2014-01-20.
Lesson 3 wants 2014-02-03 but conflicts with <QuerySet [Event #8 ('Recurring event #1 National Day')]>, moving to 2014-02-10.
Lesson 3 wants 2014-02-10 but conflicts with <QuerySet [Event #17 ('Activity #1 Lesson 3')]>, moving to 2014-02-17.
Update presences for Activity #1 Lesson 3 : 0 created, 0 unchanged, 0 deleted.
1 row(s) have been updated.
""",
                          """
================ =========== ===================
 When             State       Short description
---------------- ----------- -------------------
 Mon 03/03/2014   Suggested   Lesson 5
 Mon 24/02/2014   Suggested   Lesson 4
 Mon 17/02/2014   Suggested   Lesson 3
 Mon 10/02/2014   Cancelled   Lesson 3
 Mon 27/01/2014   Suggested   Lesson 2
 Mon 20/01/2014   Draft       Lesson 1
================ =========== ===================
        """,
                          debug=False)

        e = cal.Event.objects.get(event_type=lesson, auto_type=3)
        self.assertEqual(e.start_date, i2d(20140217))
        e.state = cal.EntryStates.draft
        e.full_clean()
        e.save()

        the_cancelled_lesson.delete()

        self.check_update(obj,
                          """
Run Update calendar for Activity #1...
Generating events between 2014-01-13 and 2020-05-22 (max. 5).
Lesson 1 has been moved from 2014-01-13 to 2014-01-20.
Lesson 3 wants 2014-02-03 but conflicts with <QuerySet [Event #8 ('Recurring event #1 National Day')]>, moving to 2014-02-10.
Lesson 3 has been moved from 2014-02-10 to 2014-02-17.
0 row(s) have been updated.
""",
                          """
================ =========== ===================
 When             State       Short description
---------------- ----------- -------------------
 Mon 03/03/2014   Suggested   Lesson 5
 Mon 24/02/2014   Suggested   Lesson 4
 Mon 17/02/2014   Draft       Lesson 3
 Mon 27/01/2014   Suggested   Lesson 2
 Mon 20/01/2014   Draft       Lesson 1
================ =========== ===================
        """,
                          debug=False)

        # Next case: we have a series of events, only one of them is marked as
        # took_place, and then we change the weekday and start date.

        cal.Event.objects.all().delete()
        self.check_update(obj,
                          """
Run Update calendar for Activity #1...
Generating events between 2014-01-13 and 2020-05-22 (max. 5).
Update presences for Activity #1 Lesson 1 : 0 created, 0 unchanged, 0 deleted.
Update presences for Activity #1 Lesson 2 : 0 created, 0 unchanged, 0 deleted.
Update presences for Activity #1 Lesson 3 : 0 created, 0 unchanged, 0 deleted.
Update presences for Activity #1 Lesson 4 : 0 created, 0 unchanged, 0 deleted.
Update presences for Activity #1 Lesson 5 : 0 created, 0 unchanged, 0 deleted.
5 row(s) have been updated.
        """,
                          """
================ =========== ===================
 When             State       Short description
---------------- ----------- -------------------
 Mon 10/02/2014   Suggested   Lesson 5
 Mon 03/02/2014   Suggested   Lesson 4
 Mon 27/01/2014   Suggested   Lesson 3
 Mon 20/01/2014   Suggested   Lesson 2
 Mon 13/01/2014   Suggested   Lesson 1
================ =========== ===================
        """,
                          debug=False)

        ce = cal.Event.objects.get(event_type=lesson, auto_type=3)
        self.assertEqual(ce.start_date, i2d(20140127))
        update_row(ce, state=cal.EntryStates.took_place)

        # we change the activity's parameters

        update_row(obj, start_date=i2d(20150701), monday=False, tuesday=True)

        # and click update_events in the hope of getting rid of the old
        # suggestions.

        try:
            self.check_update(obj)
            self.fail("Failed to raise a Warning")
        except Warning as e:
            self.assertEqual(
                str(e), "Automatic entry 3 (2014-01-27) goes back in time.")

        # That was not enough because Lino sees the old event and thinks that we
        # want to align with it. We also need to explicitly disconnect the old
        # event by setting its auto_type to None:

        update_row(ce, state=cal.EntryStates.took_place, auto_type=None)

        self.check_update(obj,
                          """
Run Update calendar for Activity #1...
Generating events between 2015-07-07 and 2020-05-22 (max. 5).
Update presences for Activity #1 Lesson 3 : 0 created, 0 unchanged, 0 deleted.
1 row(s) have been updated.
        """,
                          """
================ ============ ===== ===================
 When             State        No.   Short description
---------------- ------------ ----- -------------------
 Tue 04/08/2015   Suggested    5     Lesson 5
 Tue 28/07/2015   Suggested    4     Lesson 4
 Tue 21/07/2015   Suggested    3     Lesson 3
 Tue 14/07/2015   Suggested    2     Lesson 2
 Tue 07/07/2015   Suggested    1     Lesson 1
 Mon 27/01/2014   Took place         Lesson 3
================ ============ ===== ===================
        """,
                          debug=False,
                          column_names="when_text state auto_type summary")

        # Another story: As a courses coordinator, I created a "placeholder"
        # course that serves just for grouping participants before they join a
        # real course. I accidentally clicked on the flash and Lino created me a
        # series of suggestions for this cours. How can I get rid of these
        # events?  Answer since 20231123: set every_unit to "never". Note that
        # any manually modified entry remains untouched.

        update_row(obj, every_unit=system.Recurrences.never)
        self.assertEqual(obj.weekdays_text, "Never")

        self.check_update(obj,
                          """
Run Update calendar for Activity #1...
No calendar entries because no start date
5 row(s) have been updated.
        """,
                          """
================ ============ ===== ===================
 When             State        No.   Short description
---------------- ------------ ----- -------------------
 Mon 27/01/2014   Took place         Lesson 3
================ ============ ===== ===================
        """,
                          debug=False,
                          column_names="when_text state auto_type summary")

        # Another case: We set recurrency to "once". Note that
        # start_date is still 2015-07-01 and "Tuesday" is still checked.

        update_row(obj, every_unit=system.Recurrences.once)
        self.assertEqual(obj.weekdays_text,
                         "Once starting on 01/07/2015 (only Tuesday)")

        self.check_update(obj,
                          """
Run Update calendar for Activity #1...
Generating events between 2015-07-07 and 2020-05-22 (max. 5).
No next date when recurrency is once.
Could not find next date after 2015-07-07 (1).
Update presences for Activity #1 Lesson 1 : 0 created, 0 unchanged, 0 deleted.
1 row(s) have been updated.
        """,
                          """
================ ============ ===== ===================
 When             State        No.   Short description
---------------- ------------ ----- -------------------
 Tue 07/07/2015   Suggested    1     Lesson 1
 Mon 27/01/2014   Took place         Lesson 3
================ ============ ===== ===================
        """,
                          debug=False,
                          column_names="when_text state auto_type summary")

        # We uncheck Tuesday because that was unintended.

        update_row(obj, tuesday="False")
        self.assertEqual(obj.weekdays_text, "On Wednesday, 1 July 2015")
        self.check_update(obj,
                          """
Run Update calendar for Activity #1...
Generating events between 2015-07-01 and 2020-05-22 (max. 5).
No next date when recurrency is once.
Could not find next date after 2015-07-01 (1).
0 row(s) have been updated.
        """,
                          """
================ ============ ===== ===================
 When             State        No.   Short description
---------------- ------------ ----- -------------------
 Wed 01/07/2015   Suggested    1     Lesson 1
 Mon 27/01/2014   Took place         Lesson 3
================ ============ ===== ===================
        """,
                          debug=False,
                          column_names="when_text state auto_type summary")
