# -*- coding: utf-8 -*-
# Copyright 2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Runs some tests about the periods plugin.

You can run only these tests by issuing::

  $ go cosi1
  $ python manage.py test tests.test_periods

"""

from lino.utils.djangotest import RemoteAuthTestCase
from lino.api import dd, rt
from lino.utils import i2d
from lino.modlib.periods.choicelists import PeriodTypes

class Tests(RemoteAuthTestCase):
    maxDiff = None

    def check_for_date(self, today, psd, ped, ysd, yed):
        P = rt.models.periods.StoredPeriod
        Y = rt.models.periods.StoredYear
        P.get_or_create_from_date(i2d(today))
        self.assertEqual(P.objects.count(), 1)
        self.assertEqual(Y.objects.count(), 1)
        p = P.objects.first()
        y = Y.objects.first()
        self.assertEqual(p.start_date, i2d(psd))
        self.assertEqual(p.end_date, i2d(ped))
        self.assertEqual(y.start_date, i2d(ysd))
        self.assertEqual(y.end_date, i2d(yed))
        P.objects.all().delete()
        Y.objects.all().delete()

    def test01(self):
        self.assertEqual(dd.plugins.periods.period_type, PeriodTypes.month)
        self.check_for_date(20241009, 20241001, 20241031, 20240101, 20241231)

        dd.plugins.periods.period_type = PeriodTypes.semester
        dd.plugins.periods.start_month = 9
        self.check_for_date(20241009, 20240901, 20250228, 20240901, 20250831)
