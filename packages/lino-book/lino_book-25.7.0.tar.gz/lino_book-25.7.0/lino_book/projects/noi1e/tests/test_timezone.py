# -*- coding: utf-8 -*-
# Copyright 2016-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# python manage.py test tests.test_timezone

"""Create calendar events and check that the start time is None.

TODO: Add tests about creating working sessions because that's where  the
user's timezone is important.

"""

import sys
import datetime
import time
import unittest

# from unittest.mock import patch

from django.conf import settings
from django.utils.timezone import make_aware
from asgiref.sync import async_to_sync

from lino.api import dd, rt
from lino.utils.djangotest import TestCase
from lino.core import constants

from lino.modlib.users.choicelists import UserTypes
from lino.modlib.about.choicelists import TimeZones

from lino.utils.instantiator import create

# from lino.modlib.notify.models import send_pending_emails_often
from lino.modlib.notify.choicelists import MailModes
from lino.modlib.linod.choicelists import Procedures
from lino.core.diff import ChangeWatcher

# from lino.utils import capture_stdout


TimeZones.clear()
add = TimeZones.add_item
add('01', 'UTC', 'default')
add('02', "Europe/Tallinn", "tallinn")
add('03', "Europe/Brussels", "brussels")

# @unittest.skip("20210527")
class TestCase(TestCase):
    maxDiff = None

    def test_timezone(self):
        # settings.SITE.clear_site_config()
        self.assertEqual(settings.SITE.site_config.simulate_today, None)
        self.assertEqual(str(settings.SITE.the_demo_date), "2015-05-22")
        self.assertEqual(settings.USE_TZ, True)
        self.assertEqual(str(settings.SITE.today()), "2015-05-22")

        Event = rt.models.cal.Event
        User = settings.SITE.user_model
        robin = create(User,
                       username='robin',
                       first_name="Robin",
                       user_type=UserTypes.admin)

        self.assertEqual(settings.TIME_ZONE, "UTC")
        self.assertEqual(robin.time_zone, TimeZones.default)
        robin.time_zone = TimeZones.tallinn
        robin.save()


        ar = rt.login('robin')
        # self.client.force_login(ar.user)
        url = "/api/cal/MyEntries"
        post_data = dict()
        post_data[constants.URL_PARAM_ACTION_NAME] = 'submit_insert'
        post_data.update(start_date=dd.today(10).strftime(settings.SITE.date_format_strftime))
        post_data.update(summary="Meeting with Peter")
        self.client.force_login(robin)
        response = self.client.post(url,
                                    post_data,
                                    REMOTE_USER='robin',
                                    HTTP_ACCEPT_LANGUAGE='en')
        result = self.check_json_result(
            response, 'rows success message close_window navinfo data_record detail_handler_name')
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'],
            'Calendar entry "Meeting with Peter (01.06.2015)" has been created.')

        rows = result['rows']
        self.assertEqual(len(rows), 1)

        e = Event.objects.first()
        self.assertEqual(e.user, robin)
        self.assertEqual(e.summary, "Meeting with Peter")
        self.assertEqual(e.start_time, None)
