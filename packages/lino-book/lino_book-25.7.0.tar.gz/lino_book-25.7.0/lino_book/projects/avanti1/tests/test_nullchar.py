# -*- coding: utf-8 -*-
# Copyright 2017-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# $ python manage.py test tests.test_nullchar
"""
Tests some behaviour of the `Client.national_id` field.

Tests whether `national_id` is set to NULL (not empty string).

"""

import os
from urllib.parse import urlencode

from lino.utils.djangotest import RemoteAuthTestCase
from lino.api import dd, rt
from lino.utils.instantiator import create_row
from lino.core import constants
from lino.modlib.users.choicelists import UserTypes
from lino.api.shell import countries, users


class TestCase(RemoteAuthTestCase):
    maxDiff = None

    # override_djangosite_settings = dict(use_java=True)

    def test01(self):

        Client = rt.models.avanti.Client

        u = users.User(username='robin',
                       user_type=UserTypes.admin,
                       language="en")
        u.save()
        self.client.force_login(u)

        be = countries.Country(name="Belgium", isocode="BE")
        be.save()

        kw = dict()
        kw.update(national_id="680601 053-29")
        kw.update(first_name="Jean")
        kw.update(middle_name="Jacques")
        kw.update(last_name="Jeffin")
        jean = create_row(Client, **kw)

        kw.update(first_name="Jo")
        kw.update(national_id="680601 054-28")
        kw.update(last_name="Jeffin")
        jo = create_row(Client, **kw)

        def grid_put(username, url, **data):
            data[constants.URL_PARAM_ACTION_NAME] = 'grid_put'
            kwargs = dict(data=urlencode(data))
            kwargs['REMOTE_USER'] = username
            response = self.client.put(url, **kwargs)
            # print(response)
            return self.check_json_result(response,
                                          'rows success message editing_mode')

        url = '/api/avanti/Clients/' + str(jean.pk)
        result = grid_put('robin', url, national_id="")
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'],
                         'Client "JEFFIN Jean (1)" has been updated.')

        jean = Client.objects.get(pk=jean.pk)
        self.assertEqual(jean.national_id, None)

        url = '/api/avanti/Clients/' + str(jo.pk)
        result = grid_put('robin', url, national_id="")
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'],
                         'Client "JEFFIN Jo (2)" has been updated.')

        def detail_put(username, url, **kwargs):
            kwargs[constants.URL_PARAM_ACTION_NAME] = 'submit_detail'
            kwargs[constants.URL_PARAM_DISPLAY_MODE] = 'detail'
            # kwargs['REMOTE_USER'] = username
            response = self.client.put(url, urlencode(kwargs))
            # print(response)
            return self.check_json_result(response,
                                          'editing_mode data_record success message')

        url = '/api/avanti/Clients/' + str(jo.pk)
        result = detail_put('robin', url, financial_notes='bla\nbla\n')
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'],
                         'Client "JEFFIN Jo (2)" has been updated.')
        data_record = result['data_record']
        self.assertEqual(
            set(data_record.keys()),
            {'id', 'navinfo', 'param_values', 'data', 'title', 'disable_delete'})
        # self.assertEqual(
        #     set(data_record['data'].keys()),
        #     {''})
        self.assertEqual(
            data_record['data']['avanti.ResidencesByPerson'],
            {'delayed_value_url': 'values/avanti/Clients/2/avanti.ResidencesByPerson'})
        self.assertEqual(
            data_record['data']['clients.ContactsByClient'],
            '<table><tbody>No data to display</tbody></table>')
        # {'delayed_value_url': 'values/avanti/Clients/101/clients.ContactsByClient'})

        url = '/values/avanti/Clients/2/clients.ContactsByClient'
        response = self.client.get(url)
        content = response.content.decode()
        self.assertEqual(content, '{ "data": "<div class=\\"htmlText\\"></div>" }')
