# -*- coding: utf-8 -*-
# Copyright 2020-2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""

  $ cd lino_book/projects/cosi1
  $ python manage.py test tests.test_invoices

"""

from django.conf import settings
from lino.utils.djangotest import RemoteAuthTestCase

from lino.utils import i2d
from lino_xl.lib.clients.choicelists import ClientStates
from lino.modlib.users.choicelists import UserTypes
from lino.modlib.system.choicelists import Genders
from lino.utils.instantiator import create_row as create
from lino.api import rt
from lino.api.shell import *


class QuickTest(RemoteAuthTestCase):
    maxDiff = None
    fixtures = ['std', 'minimal_ledger']

    def test01(self):
        # print("20180503 test_clients.test01()")
        # NoteType = rt.models.notes.NoteType
        # User = rt.models.users.User
        Journal = accounting.Journal
        Invoice = trading.VatProductInvoice

        self.assertEqual(Journal.objects.count(), 10)
        sls_jnl = Journal.objects.get(ref="SLS")
        self.assertEqual(Invoice.objects.count(), 0)

        robin = create(users.User,
                       username="robin",
                       user_type=UserTypes.admin,
                       language="en")

        self.client.force_login(robin)

        kw = dict()
        kw.update(first_name="Max")
        kw.update(last_name="Mustermann")
        kw.update(gender=Genders.male)
        obj = create(contacts.Person, **kw)

        # #3989 (After creating an invoice, Lino forgets the journal) : Lino
        # returned an eval_js instead of a data_record to the submit_insert
        # because it assumed that the detail view is another table:

        url = "/api/trading/InvoicesByJournal"
        data = dict(mk=sls_jnl.pk, mt=23, partnerHidden=obj.pk)
        data.update(an="submit_insert")
        data.update(entry_date="12.03.2025", subject="test")
        response = self.client.post(url, data, REMOTE_USER='robin')
        result = self.check_json_result(
            response,
            'message close_window success eval_js rows navinfo master_data'
        )

        # just while we are here:
        self.assertEqual(result['success'], True)
        expected = """Trading invoice "SLS 1/2025" has been created."""
        # print(expected)
        self.assertEqual(expected, result['message'])
        self.assertEqual(Invoice.objects.count(), 1)
