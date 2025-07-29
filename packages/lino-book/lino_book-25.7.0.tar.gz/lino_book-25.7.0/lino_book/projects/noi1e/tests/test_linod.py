# -*- coding: utf-8 -*-
# Copyright 2023-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# pm test tests.test_linod
"""Tests the linod daemon.

"""

import sys
import logging
import unittest
from datetime import timedelta
from asgiref.sync import async_to_sync
from django.conf import settings
from atelier.utils import SubProcessParent

from lino.modlib.linod.choicelists import Procedures
from lino.modlib.linod.mixins import start_task_runner
from lino.utils.djangotest import RemoteAuthTestCase
from lino.api import rt


@unittest.skip("Not yet rewritten after 20250620")
class QuickTest(RemoteAuthTestCase, SubProcessParent):
    maxDiff = None
    skip = True

    # fixtures = ["std", "minimal_ledger", "demo", "checkdata"]
    # fixtures = ["std", "demo", "checkdata"]
    fixtures = ["std", "demo_users", "checkdata"]

    override_djangosite_settings = dict()

    # def run_admin_command(self, cmd, **kw):
    #     args = [ sys.executable ]
    #     #~ args += ["-Wall"]
    #     args += ["manage.py"]
    #     #~ args += ["--buffer"]
    #     args += [cmd]
    #     self.run_subprocess(args, **kw)

    def run_tasks(self,
                  ar,
                  expected=None,
                  debug=False,
                  log_level=logging.INFO):
        # from lino.modlib.linod.choicelists import Procedures
        # SystemTask = rt.models.linod.SystemTask
        # start_task_runner = rt.models.linod.start_task_runner
        with ar.capture_logger(level=log_level) as out:
            # TODO: Why do we need to call spawn_request()?
            async_to_sync(start_task_runner)(ar.spawn_request(), max_count=1)
            # async_to_sync(start_task_runner)(ar, max_count=1)

        output = out.getvalue()
        if debug:
            print("=" * 76)
            if expected is not None:
                import difflib
                print("".join(list(difflib.Differ().compare(
                    expected.splitlines(keepends=True), output.splitlines(keepends=True)))[1:]))
            else:
                print(output)
            print("=" * 76)
        if expected is not None:
            self.assertEquivalent(expected, output)

    def test01(self):

        SystemTask = rt.models.linod.SystemTask
        # from lino.core.requests import BaseRequest
        # u = await settings.SITE.user_model.objects.aget(
        #     username=settings.SITE.plugins.linod.daemon_user)
        # ar = BaseRequest(user=u)
        ar = rt.login(settings.SITE.plugins.linod.daemon_user)

        # self.assertEqual(SystemTask.objects.count(), 8)
        obj = SystemTask.objects.get(
            procedure=Procedures.send_pending_emails_often)
        self.assertEqual(obj.last_start_time, None)
        self.assertEqual(obj.last_end_time, None)

        self.run_tasks(ar,
                       """
Start task runner using <StringLogger lino~ (INFO)>...
Update summary data for Subscriptions ...
Update summary data for Tickets ...
Update summary data for User Statistics ...
Update summary data for Order summaries ...
Update summary data for User summaries ...
Run 1 data checkers on 0 Vouchers...
Run 1 data checkers on 0 Delivery notes...
Run 1 data checkers on 0 Subscriptions...
Run 1 data checkers on 0 Trading invoices...
Run 1 data checkers on 0 Ledger invoices...
Run 3 data checkers on 0 Partners...
Run 6 data checkers on 113 Calendar entries...
Run 3 data checkers on 0 Comments...
Run 1 data checkers on 0 Places...
Run 3 checkers on unbound data...
Run 2 data checkers on 0 Product Categories...
Run 2 data checkers on 0 Products...
Run 1 data checkers on 0 Ibanity suppliers...
Run 1 data checkers on 0 Excerpts...
Run 1 data checkers on 8 Payment terms...
Run 1 data checkers on 1 Calendars...
Run 1 data checkers on 4 Calendar entry types...
Run 1 data checkers on 15 Recurring events...
Run 1 data checkers on 0 Rooms...
Run 1 data checkers on 0 Tasks...
Run 1 data checkers on 0 Teams...
Run 2 data checkers on 0 Tickets...
Run 1 data checkers on 2 Text Field Templates...
Run 1 data checkers on 0 Interests...
Run 1 data checkers on 0 Trading invoice items...
Run 2 data checkers on 0 Working sessions...
Run 1 data checkers on 0 Upload files...
27 checks have been run. Found 0 and fixed 0 problems.
Send email '[noi1e] Week 20 activity report' from root@localhost to []
Ignoring email '[noi1e] Week 20 activity report' because there is no recipient
Stop after 1 loops.
""",
                       debug=True)

        obj = SystemTask.objects.get(
            procedure=Procedures.send_pending_emails_often)
        self.assertNotEqual(obj.last_start_time, None)
        self.assertNotEqual(obj.last_end_time, None)

        obj.last_start_time -= timedelta(hours=10)
        obj.last_end_time = None
        obj.full_clean()
        obj.save()

        # On the second loop it won't do much because every task has just been
        # run:

        self.run_tasks(ar,
                       """
Start task runner using <StringLogger lino~ (DEBUG)>...
Start next task runner loop.
Too early to start System task #1 (event_notification_scheduler)
Too early to start System task #2 (generate_calendar_entries)
Too early to start System task #3 (checksummaries)
Too early to start System task #4 (checkdata)
Too early to start System task #5 (send_weekly_report)
Too early to start System task #6 (delete_older_changes)
Killed System task #7 (send_pending_emails_often) because running more than 2 hours
Too early to start System task #8 (send_pending_emails_daily)
Too early to start System task #9 (clear_seen_messages)
Too early to start System task #10 (read_inbox)
Stop after 1 loops.
        """,
                       log_level=logging.DEBUG,
                       debug=False)

        obj = SystemTask.objects.get(
            procedure=Procedures.send_pending_emails_often)
        self.assertNotEqual(obj.last_end_time, None)
        self.assertEqual(
            obj.message,
            "Killed System task #7 (send_pending_emails_often) because "
            "running more than 2 hours"
        )

        # no output at all when log_level is WARNING:
        self.run_tasks(ar, "", log_level=logging.WARNING, debug=False)

        # self.run_admin_command("linod")

        # ses = rt.login('robin')
        # with ses.capture_logger(logging.DEBUG) as out:
        #     res = ses.run(obj.do_update_events)
        # self.assertEqual(res['success'], True)
        # s1 = out.getvalue()
        # if debug:
        #     print(s1)
        # ar = ses.spawn(cal.EntriesByController, master_instance=obj)
        # s2 = ar.to_rst(column_names=column_names, nosummary=True)
        # if debug:
        #     print(s2)
        # self.assertEquivalent(msg1.strip(), s1.strip())
