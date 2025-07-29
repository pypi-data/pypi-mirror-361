# -*- coding: utf-8 -*-
# Copyright 2013-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# how to run only this module:
# go min9
# python manage.py test tests.test_delete_veto

# import logging ; logger = logging.getLogger(__name__)

import json
from pprint import pprint
from urllib.parse import urlencode

from lino.utils import AttrDict
from lino.utils.instantiator import create_row as create
from lino.utils.djangotest import RemoteAuthTestCase
from lino.utils.jsgen import py2js
from lino.api.shell import *


class QuickTest(RemoteAuthTestCase):

    def test01(self):
        """
        Initialization.
        """
        # ~ print "20130321 test00 started"
        self.user_root = settings.SITE.user_model(username='root',
                                                  language='en',
                                                  user_type='900')
        self.user_root.full_clean()
        self.user_root.save()
        self.client.force_login(self.user_root)

        self.assertEqual(1 + 1, 2)
        o1 = contacts.Company(name="Example")
        o1.save()
        o2 = contacts.Company(name="Example")
        o2.save()

        p1 = contacts.Person(first_name="John", last_name="Doe")
        p1.full_clean()
        p1.save()
        p2 = contacts.Person(first_name="Johny", last_name="Doe")
        p2.full_clean()
        p2.save()

        contacts.Role(person=p1, company=o1).save()
        contacts.Role(person=p2, company=o2).save()

        evt = cal.Event()
        evt.full_clean()
        evt.save()
        guest = cal.Guest(event=evt, partner=p1)
        guest.full_clean()
        guest.save()

        # s = contacts.RolesByCompany.request(o1, user=self.user_root).to_rst()
        s = rt.shows(contacts.RolesByCompany, o1, user=self.user_root)
        # print('\n'+s)
        self.assertEqual(s, """\
`John Doe <…>`__, **New**
""")

        # s = contacts.RolesByCompany.request(o2, user=self.user_root).to_rst()
        s = rt.shows(contacts.RolesByCompany, o2, user=self.user_root)
        # print('\n'+s)
        self.assertEqual(s, """\
`Johny Doe <…>`__, **New**
""")
        # ba = contacts.Persons.get_action_by_name('merge_row')
        # self.assertEqual(ba, '')
        # utpl = "/api/contacts/Persons/{0}?fv={1}&fv=&fv=&fv=&fv=false&fv=fff&an=merge_row"
        utpl = "/api/contacts/Persons/{0}?fv={1}&fv=false&fv=false&fv=false&fv=false&fv=false&fv=false&fv=test&an=merge_row"
        url = utpl.format(p1.pk, p1.pk)
        res = self.client.get(url, REMOTE_USER='root')
        self.assertEqual(res.status_code, 200)
        res = AttrDict(json.loads(res.content))
        self.assertEqual(res.message, "Cannot merge an instance to itself.")
        self.assertEqual(res.success, False)

        url = utpl.format(p1.pk, '')
        res = self.client.get(url, REMOTE_USER='root')
        self.assertEqual(res.status_code, 200)
        res = AttrDict(json.loads(res.content))
        self.assertEqual(res.message, "You must specify a merge target.")
        self.assertEqual(res.success, False)

        url = utpl.format(p1.pk, p2.pk)
        res = self.client.get(url, REMOTE_USER='root')
        self.assertEqual(res.status_code, 200)
        res = AttrDict(json.loads(res.content))
        # print(res)
        expected = '<div class="htmlText"><p>Are you sure you want to merge John Doe into Johny Doe?</p><ul><li>1 Presences, 1 Contact persons <b>will get reassigned.</b></li><li>John Doe will be deleted</li></ul></div>'
        self.assertEqual(res.message, expected)
        self.assertEqual(res.success, True)
        self.assertEqual(res.close_window, True)
        self.assertEqual(res.xcallback['buttons'],
                         [['yes', 'Yes'], ['no', 'No']])
        self.assertEqual(res.xcallback['title'], "Confirmation")

        # pprint(res.xcallback)
        cbid = res.xcallback['id']
        # add callback uid adn choice into request and send again.
        url += "&" + urlencode({"xcallback__" + cbid: "yes"})

        res = self.client.get(url, REMOTE_USER='root')
        self.assertEqual(res.status_code, 200)
        res = AttrDict(json.loads(res.content))
        # print(res)
        self.assertEqual(
            res.message,
            'Merged John Doe (3) into Johny Doe (4). Updated 2 related rows.'
        )
        self.assertEqual(res.success, True)

        # s = contacts.Roles.request().to_rst()
        s = rt.shows(contacts.Roles)
        # print('\n'+s)
        self.assertEqual(
            s, """\
==== ========== =========== ==============
 ID   Function   Person      Organization
---- ---------- ----------- --------------
 1               Johny Doe   Example
 2               Johny Doe   Example
==== ========== =========== ==============

""")

        # s = cal.Guests.request().to_rst()
        s = rt.shows(cal.Guests)
        # print('\n'+s)
        self.assertEqual(
            s, """\
=========== ====== ============= ======== ================================
 Person      Role   Workflow      Remark   Calendar entry
----------- ------ ------------- -------- --------------------------------
 Johny Doe          **Invited**            Calendar entry #1 (23.10.2014)
=========== ====== ============= ======== ================================

""")

        # self.fail("TODO: execute a merge action using the web interface")

        # 20130418 server traceback caused when a pdf view of a table
        # was requested through the web interface.  TypeError:
        # get_handle() takes exactly 1 argument (2 given)
        url = settings.SITE.buildurl(
            'api/countries/Countries?cw=189&cw=45&cw=45&cw=36&ch=&ch=&ch=&ch=&ch=&ch=&ci=name&ci=isocode&ci=short_code&ci=iso3&name=0&an=as_pdf'
        )
        msg = 'Using remote authentication, but no user credentials found.'
        if False:  # not converted after 20170609
            try:
                response = self.client.get(url)
                self.fail("Expected '%s'" % msg)
            except Exception as e:
                self.assertEqual(str(e), msg)

        # response = self.client.get(url, REMOTE_USER='foo')
        # self.assertEqual(response.status_code, 403,
        #                  "Status code for anonymous on GET %s" % url)
        from appy.pod import PodError
        """
        If oood is running, we get a 302, otherwise a PodError
        """
        try:
            response = self.client.get(url, REMOTE_USER='root')
            # ~ self.assertEqual(response.status_code,200)
            result = self.check_json_result(response, 'success open_url')
            self.assertEqual(
                result['open_url'],
                "/media/cache/appypdf/127.0.0.1/countries.Countries.pdf")

        except PodError as e:
            pass
            # ~ self.assertEqual(str(e), PodError: Extension of result file is "pdf".
