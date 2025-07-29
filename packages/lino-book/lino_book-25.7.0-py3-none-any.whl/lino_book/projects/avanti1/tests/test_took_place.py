# -*- coding: utf-8 -*-
# Copyright 2020-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# $ pm test tests.test_took_place
"""Reproduce :ticket:`3637` (AjaxExceptionResponse TypeError: can only concatenate str (not "__proxy__") to str)

"""

import json
from lino.utils.instantiator import create_row as create
from lino.utils.djangotest import RemoteAuthTestCase
from lino.api.shell import *
from lino.utils import AttrDict


class QuickTest(RemoteAuthTestCase):

    def test01(self):
        """
        Initialization.
        """
        # ~ print "20130321 test00 started"
        self.user_root = settings.SITE.user_model(username='root',
                                                  language='en',
                                                  user_type='900')
        self.user_root.save()
        self.client.force_login(self.user_root)

        self.assertEqual(1 + 1, 2)
        # o1 = contacts.Company(name="Example")
        # o1.save()
        # o2 = contacts.Company(name="Example")
        # o2.save()

        p1 = avanti.Client(first_name="John", last_name="Doe")
        p1.full_clean()
        p1.save()
        # p2 = contacts.Person(first_name="Johny", last_name="Doe")
        # p2.full_clean()
        # p2.save()

        # contacts.Role(person=p1, company=o1).save()
        # contacts.Role(person=p2, company=o2).save()

        evt = cal.Event()
        evt.full_clean()
        evt.save()
        guest = cal.Guest(event=evt, partner=p1)
        guest.full_clean()
        guest.save()

        # s = cal.GuestsByEvent.request(evt).to_rst()
        s = rt.shows(cal.GuestsByEvent, evt)
        # print('\n'+s)
        self.assertEqual(
            s, """\
=============== ====== =============== ================ ========
 Participant     Role   Workflow        Absence reason   Remark
--------------- ------ --------------- ---------------- --------
 (1) from None          **? Invited**
=============== ====== =============== ================ ========

""")
        # ba = contacts.Persons.get_action_by_name('merge_row')
        # self.assertEqual(ba, '')
        utpl = "/api/cal/OneEvent/{0}?&an=wf3"
        url = utpl.format(evt.pk)
        res = self.client.get(url, REMOTE_USER='root')
        self.assertEqual(res.status_code, 200)
        res = AttrDict(json.loads(res.content))
        self.assertEqual(
            res.message,
            "Cannot mark as Took place because 1 participants are Invited.")
        self.assertEqual(res.success, False)
