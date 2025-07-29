# -*- coding: utf-8 -*-
# Copyright 2013-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""This module contains tests that are run on a demo database without
any fixture.

You can run only these tests by issuing::

  $ cd lino_book/projects/cosi1
  $ python manage.py test tests.test_ledger

"""

from lino.api.shell import dd, periods, settings
from lino.utils.djangotest import RemoteAuthTestCase


class QuickTest(RemoteAuthTestCase):

    def test01(self):
        self.assertEqual(dd.plugins.periods.fix_y2k, False)
        self.assertEqual(settings.SITE.today().year, 2025)
        obj = periods.StoredYear.get_or_create_from_date(settings.SITE.today())
        self.assertEqual(obj.ref, '2025')

        obj = periods.StoredPeriod()
        obj.full_clean()
        self.assertEqual(
            str(obj), 'StoredPeriod(start_date=2025-03-01,'
            'state=<periods.PeriodStates.open:10>,year=1)')
