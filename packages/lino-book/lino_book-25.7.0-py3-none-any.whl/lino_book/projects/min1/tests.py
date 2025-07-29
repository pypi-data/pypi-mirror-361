# -*- coding: utf-8 -*-
# Copyright 2008-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
This module contains some relatively quick tests that don't load any
fixtures.

To run only this test::

  $ go min1
  $ python manage.py test

"""

import subprocess
import os
import unittest

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import translation
from atelier.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from pathlib import Path

from lino.api import dd, rt
from lino.modlib.users.choicelists import UserTypes
from lino.utils.djangotest import RemoteAuthTestCase
from lino.utils.instantiator import create_and_get
from lino_xl.lib.contacts import models as contacts

Genders = dd.Genders


ROOT = Path(__file__).parent.parent.parent.parent.absolute()

# CYPRESS contains a deliberate typo (added "XXX") because the cypress test is
# broken and the test case is skipped when the path doesn't exist:

CYPRESS = ROOT / "node_modules/cypress/bin/cypressXXX"

print(f"20250126 ROOT is {ROOT}")
if CYPRESS.exists():
    print(f"20250126 {CYPRESS} found")
else:
    print(f"20250126 {CYPRESS} not found")


class QuickTest(RemoteAuthTestCase):

    def test01(self):
        """
        Tests some basic funtionality.
        """
        self.assertEqual(
            settings.MIDDLEWARE,
            ('django.middleware.common.CommonMiddleware',
             'django.middleware.locale.LocaleMiddleware',
             'django.contrib.sessions.middleware.SessionMiddleware',
             'lino.core.auth.middleware.AuthenticationMiddleware',
             'lino.core.auth.middleware.WithUserMiddleware'))
        # settings.MIDDLEWARE_CLASSES, (
        #     'django.middleware.common.CommonMiddleware',
        #     'django.middleware.locale.LocaleMiddleware',
        #     'lino.core.auth.RemoteUserMiddleware',
        #     'lino.utils.ajax.AjaxExceptionResponse'))

        Person = rt.models.contacts.Person
        Partner = rt.models.contacts.Partner
        Country = rt.models.countries.Country
        Place = rt.models.countries.Place
        PlaceTypes = rt.models.countries.PlaceTypes

        ee = create_and_get(Country,
                            isocode='EE',
                            **dd.babelkw(
                                'name',
                                de="Estland",
                                fr='Estonie',
                                en="Estonia",
                                nl='Estland',
                                et='Eesti',
                            ))
        be = create_and_get(Country,
                            isocode='BE',
                            **dd.babelkw(
                                'name',
                                de="Belgien",
                                fr='Belgique',
                                en="Belgium",
                                nl='Belgie',
                                et='Belgia',
                            ))

        eupen = create_and_get(Place,
                               name=u'Eupen',
                               country=be,
                               zip_code='4700')

        vigala = create_and_get(Place,
                                name='Vigala',
                                country=ee,
                                type=PlaceTypes.municipality)

        luc = create_and_get(Person,
                             id=contacts.PARTNER_NUMBERS_START_AT,
                             first_name='Luc',
                             last_name='Saffre',
                             gender=Genders.male,
                             country=ee,
                             street='Uus',
                             street_no='1',
                             addr2='Vana-Vigala küla',
                             city=vigala,
                             zip_code='78003')

        settings.SITE.uppercase_last_name = True
        """If the following tests raise a "DoesNotExist: Company matching
        query does not exist" then this may come because
        Site._site_config has been filled before the database switched
        from the real db to test db.  and not properly reset.

        """

        with translation.override('en'):
            self.assertEqual(
                luc.address, u'''\
Mr Luc SAFFRE
Uus 1
Vana-Vigala küla
78003 Vigala vald
Estonia''')

        with translation.override('de'):
            self.assertEqual(
                luc.address, u'''\
Herrn Luc SAFFRE
Uus 1
Vana-Vigala küla
78003 Vigala vald
Estland''')
            self.assertEqual(
                luc.address_html, '''\
<p>Herrn Luc SAFFRE<br/>Uus 1<br/>Vana-Vigala küla<br/>78003 Vigala vald<br/>Estland</p>'''
            )

        # "new" or "full" style is when the database knows the
        # geographic hierarchy. We then just select "Vana-Vigala" as
        # the "City".

        vana_vigala = create_and_get(Place,
                                     name='Vana-Vigala',
                                     country=ee,
                                     parent=vigala,
                                     type=PlaceTypes.village,
                                     zip_code='78003')

        meeli = create_and_get(Person,
                               first_name='Meeli',
                               last_name='Mets',
                               gender=Genders.female,
                               country=ee,
                               street='Hirvepargi',
                               street_no='123',
                               city=vana_vigala)

        with translation.override('en'):
            self.assertEqual(
                meeli.address, u'''\
Mrs Meeli METS
Hirvepargi 123
Vana-Vigala küla
78003 Vigala vald
Estonia''')

        root = create_and_get(settings.SITE.user_model,
                              username='root',
                              language='',
                              user_type=UserTypes.admin)
        """
        disable SITE.is_imported_partner() otherwise
        disabled_fields may contain more than just the 'id' field.
        """
        save_iip = settings.SITE.is_imported_partner

        def f(obj):
            return False

        settings.SITE.is_imported_partner = f
        """
        Note that we must specify the language both in the user
        and in HTTP_ACCEPT_LANGUAGE because...
        """

        luc = Person.objects.get(name__exact="Saffre Luc")
        self.assertEqual(luc.pk, contacts.PARTNER_NUMBERS_START_AT)

        url = settings.SITE.buildurl('api', 'contacts', 'Person',
                                     '%d?query=&an=detail&fmt=json' % luc.pk)
        # ~ url = '/api/contacts/Person/%d?query=&an=detail&fmt=json' % luc.pk
        if settings.SITE.get_language_info('en'):
            root.language = 'en'
            root.save()
            self.client.force_login(root)
            response = self.client.get(url,
                                       REMOTE_USER='root',
                                       HTTP_ACCEPT_LANGUAGE='en')
            result = self.check_json_result(
                response, 'data disable_delete id navinfo param_values title')
            self.assertEqual(result['data']['country'], "Estonia")
            self.assertEqual(result['data']['gender'], "Male")

        if settings.SITE.get_language_info('de'):
            root.language = 'de'
            root.save()
            response = self.client.get(url,
                                       REMOTE_USER='root',
                                       HTTP_ACCEPT_LANGUAGE='de')
            result = self.check_json_result(
                response, 'navinfo disable_delete data id param_values title')
            self.assertEqual(result['data']['country'], "Estland")
            self.assertEqual(result['data']['gender'], "Männlich")
            # ~ self.assertEqual(result['data']['disabled_fields'],['contact_ptr_id','id'])
            # ~ self.assertEqual(result['data']['disabled_fields'],['id'])
            df = result['data']['disabled_fields']
            self.assertEqual(df['id'], True)

        if settings.SITE.get_language_info('fr'):
            root.language = 'fr'
            root.save()
            response = self.client.get(url,
                                       REMOTE_USER='root',
                                       HTTP_ACCEPT_LANGUAGE='fr')
            result = self.check_json_result(
                response, 'navinfo disable_delete data id param_values title')
            self.assertEqual(result['data']['country'], "Estonie")
            self.assertEqual(result['data']['gender'], u"Masculin")

        # ~ root.language = lang
        # ~ root.save()
        # restore is_imported_partner method
        settings.SITE.is_imported_partner = save_iip

    def test02(self):
        # This case demonstrates that ordering does not ignore case, at
        # least in sqlite. we would prefer to have `['adams', 'Zybulka']`,
        # but we get `['Zybulka', 'adams']`.

        contacts = rt.models.contacts
        contacts.Partner(name="Zybulka").save()
        contacts.Partner(name="adams").save()
        ar = rt.login().spawn(contacts.Partners)
        names = [p.name for p in ar]
        expected = ['Zybulka', 'adams']
        self.assertEqual(names, expected)

    def test03(self):
        # Users with empty username field are allowed but inactive
        User = rt.models.users.User
        foo = User(last_name="Foo")
        foo.full_clean()
        self.assertEqual(foo.is_active, False)
        # try:
        #     self.fail("Expected ValidationError")
        # except ValidationError:
        #     pass


@unittest.skipIf(not CYPRESS.exists(), "Cypress is not installed")
class CypressTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command('prep', interactive=False, verbosity=0)

    def test_cypress(self):
        print(self.live_server_url)
        os.environ.update({
            # 'CYPRESS_HOST':self.live_server_url,
            # 'cypress_api_server':self.live_server_url,
            'cypress_baseUrl': self.live_server_url
        })
        command = f'{CYPRESS} run -C {ROOT}/cypress.json'
        command += f' -s {ROOT}/cypress/integration/min1/* --config video=false'
        print(f"20250126 command is {command}")
        p = subprocess.Popen(command.split())
        out, err = p.communicate()
