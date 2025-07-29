# -*- coding: utf-8 -*-
# Copyright 2016-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# pm test tests.test_vat

"""Runs some tests about the VAT plugin.

"""

from django.conf import settings

from lino.api import rt
from lino.utils.djangotest import TestCase
from lino.modlib.users.choicelists import UserTypes
from lino.utils.instantiator import create


# @unittest.skip("20210527")
class TestCase(TestCase):
    maxDiff = None

    def test_vat_id_changed(self):
        """Test what can happen when the VAT id of a partner changes.

        """
        Company = rt.models.contacts.Company
        Country = rt.models.countries.Country
        User = settings.SITE.user_model
        VatRegimes = rt.models.vat.VatRegimes
        self.robin = create(User,
                            username='robin',
                            first_name="Robin",
                            user_type=UserTypes.admin)
        be = create(Country, isocode="BE", name="Belgium")
        de = create(Country, isocode="DE", name="Germany")
        self.partner = create(Company,
                              name='Partner',
                              country=be)

        self.assertEqual(Company.objects.count(), 1)
        # self.assertEqual(VatRegimes.get_list_items(), [])

        regime = VatRegimes.normal

        ar = rt.login('robin', renderer=settings.SITE.kernel.default_renderer)
        # self.client.force_login(ar.user)

        obj = self.partner
        self.assertEqual(obj.country.isocode, "BE")

        url = "/api/contacts/Companies/{}".format(obj.pk)
        data = "an=submit_detail&vat_id=BE-123.456.7890"
        data += "&countryHidden=BE&country=Belgium"
        data += "&vat_regime=" + regime.text + "&vat_regimeHidden=" + regime.value
        self.client.force_login(self.robin)
        response = self.client.put(url,
                                   data,
                                   REMOTE_USER='robin',
                                   HTTP_ACCEPT_LANGUAGE='en')
        result = self.check_json_result(
            response, 'alert message success')

        self.assertEqual(result['success'], False)
        self.assertIn(result['message'],
                      "Modulo 97 check failed for VAT identification number in BE")
