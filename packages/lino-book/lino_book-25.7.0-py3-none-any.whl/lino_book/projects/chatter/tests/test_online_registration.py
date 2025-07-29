# -*- coding: UTF-8 -*-
# Copyright 2021-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# pm test tests.test_online_registration

from lino import logger

import sys
import argparse
import unittest
import time
import json

from django.core.management.base import BaseCommand, CommandError
from datetime import timedelta
from django.conf import settings

from lino.api import dd, rt
from lino.utils.djangotest import RemoteAuthTestCase
from lino.utils import AttrDict


class TestCase(RemoteAuthTestCase):

    fixtures = ['std', 'demo']

    def my_post(self, url, **data):
        # data = {
        #     constants.URL_PARAM_FIELD_VALUES: [username, pwd],
        #     constants.URL_PARAM_ACTION_NAME: an
        # }
        # url = settings.SITE.kernel.editing_front_end.build_plain_url(url)
        # print(url)
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 200)
        content = res.content.decode()
        d = json.loads(content)
        return AttrDict(d)

    def test_it(self):

        url = "/api/about/About"
        data = dict(an="reset_password",
            email="andy@example.com", new1="123456", new2="123456")

        r = self.my_post(url, **data)
        self.assertEqual(r.message,
            "No active users having {'email': 'andy@example.com'}")

        data["new2"] = "654321"
        r = self.my_post(url, **data)
        self.assertEqual(r.message, "New passwords didn't match!")

        obj = rt.models.users.User.objects.get(username="andy")
        self.assertEqual(obj.verification_code, "")
        obj.email = "andy@example.com"
        obj.full_clean()
        obj.save()

        data["new2"] = "123456"
        r = self.my_post(url, **data)
        self.assertEqual(r.message,
            "Send verification link to Andreas Anderson <andy@example.com> ?")
        xcallback = r.xcallback['id']
        # self.assertEqual(xcallback, '')
        self.assertEqual(len(xcallback), 32)

        data["xcallback__" + xcallback] = "yes"
        r = self.my_post(url, **data)
        self.assertEqual(r.message,
            "Verification link has been sent to Andreas Anderson <andy@example.com>.")

        obj = rt.models.users.User.objects.get(username="andy")
        data = dict(an="verify_user",
            email="andy@example.com", verification_code=obj.verification_code)
        r = self.my_post(url, **data)
        self.assertEqual(r.message, "Your email address "
            "andy@example.com is now verified. Your new password has been "
            "activated. Please sign in.")
