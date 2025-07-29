# -*- coding: utf-8 -*-
# Copyright 2014-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Test certain aspects of `lino_xl.lib.addresses`.

This module is part of the Lino test suite. You can test only this
module by issuing::

  $ go min9
  $ python manage.py test tests.test_addresses

This test unit has some tests that are now covered by `doctest
docs/specs/addresses.rst`.


"""

from django.conf import settings
from lino.core.gfks import gfk2lookup
from lino.api import rt, dd
from lino.modlib.gfks.mixins import Controllable
from lino.utils.djangotest import RemoteAuthTestCase
from lino.core.utils import full_model_name


def create(m, ar=None, **kw):
    obj = m(**kw)
    obj.full_clean()
    obj.save()
    obj.after_ui_save(ar, None)
    return obj


class QuickTest(RemoteAuthTestCase):

    fixtures = ['std', 'demo_users', 'few_countries', 'few_cities']

    def test_this(self):

        Company = rt.models.contacts.Company
        Person = rt.models.contacts.Person
        Address = rt.models.addresses.Address
        Place = rt.models.countries.Place
        Household = rt.models.households.Household
        Member = rt.models.households.Member
        checkdata_Message = rt.models.checkdata.Message

        def assert_check(obj, expected):
            qs = checkdata_Message.objects.filter(
                **gfk2lookup(checkdata_Message.owner, obj))
            got = '\n'.join([p.message for p in qs])
            self.assertEqual(got, expected)

        self.assertEqual(
            Address.ADDRESS_FIELDS,
            set([
                'city', 'street_prefix', 'street_box', 'region', 'street_no',
                'street', 'addr2', 'addr1', 'country', 'zip_code'
            ]))

        # en passant we reproduce #3745 (Lino says "partner: cannot be null"
        # when trying to create a person): (happened only when site_company was
        # filled)

        obj = Company(name="Minimal Corp", country_id="BE")
        obj.full_clean()
        obj.save()
        assert obj.pk == 1
        # settings.SITE.site_config.update(site_company=obj)
        url = "/api/contacts/Persons"
        data = dict(an='submit_insert',
                    first_name='Tom',
                    last_name='Test',
                    genderHidden='M',
                    gender='Male',
                    languageHidden='en',
                    language='English')
        resp = self.post_json_dict("robin", url, data)
        self.assertEqual(resp.message,
                         'Person "Mr Tom Test" has been created.')
        self.assertEqual(resp.success, True)
        # remove site_company:
        # settings.SITE.site_config.update(site_company=None)
        Address.objects.all().delete()
        obj.delete()

        eupen = Place.objects.get(name="Eupen")
        ar = rt.models.contacts.Companies.request()
        obj = create(Company, name="Owner with empty address")
        obj.check_data.run_from_code(ar, fix=False)
        assert_check(obj, '')
        obj.delete()

        self.assertEqual(Company.objects.count(), 0)
        self.assertEqual(Address.objects.count(), 0)

        doe = create(Company, name="Owner with address", city=eupen)

        self.assertEqual(Company.objects.count(), 1)
        self.assertEqual(Address.objects.count(), 1)

        # manually delete the primary address record
        Address.objects.all().delete()
        self.assertEqual(Address.objects.count(), 0)

        assert_check(doe, '')  # No problems yet since not checked
        doe.check_data.run_from_code(ar, fix=False)
        assert_check(doe, '(\u2605) Primary address is missing.')

        addr = doe.get_primary_address()
        self.assertEqual(addr, None)

        doe.check_data.run_from_code(ar, fix=True)
        assert_check(doe, '')  # problem has been fixed
        addr = doe.get_primary_address()
        self.assertEqual(Address.objects.count(), 1)
        self.assertEqual(addr.city, eupen)
        self.assertEqual(addr.primary, True)

        addr.primary = False
        addr.save()
        addr = doe.get_primary_address()
        self.assertEqual(addr, None)
        self.assertEqual(Address.objects.count(), 1)

        doe.check_data.run_from_code(ar, fix=False)
        assert_check(doe, '(\u2605) Unique address is not marked primary.')

        Address.objects.all().delete()
        self.assertEqual(Address.objects.count(), 0)
        addr = doe.get_primary_address()
        self.assertEqual(addr, None)

        doe.check_data.run_from_code(ar, fix=False)
        assert_check(doe, '(\u2605) Primary address is missing.')

        doe.check_data.run_from_code(ar, fix=True)
        assert_check(doe, '')  # problem has been fixed

        # next problem : owner differs from primary address
        doe.city = None
        doe.zip_code = ''
        doe.full_clean()
        self.assertEqual(doe.city, None)
        doe.save()
        doe.check_data.run_from_code(ar, fix=False)
        self.assertEqual(Address.objects.count(), 1)
        assert_check(doe, "(\u2605) Must sync address to owner.")
        doe.check_data.run_from_code(ar, fix=True)
        self.assertEqual(Address.objects.count(), 1)
        self.assertEqual(doe.city, eupen)
        addr = doe.get_primary_address()
        self.assertEqual(addr.city, eupen)
        self.assertEqual(addr.primary, True)

        # next problem: multiple primary address.
        # recover from previous test.
        doe.city = eupen
        doe.full_clean()
        doe.save()
        self.assertEqual(doe.city, eupen)
        self.assertEqual(doe.zip_code, '4700')
        addr = doe.get_primary_address()
        addr.id = None
        addr.save()
        self.assertEqual(Address.objects.count(), 2)
        doe.check_data.run_from_code(ar, fix=False)
        assert_check(doe, "Multiple primary addresses.")

        # tidy up the database

        Company.objects.all().delete()
        Address.objects.all().delete()
        self.assertEqual(Address.objects.count(), 0)
        self.assertEqual(Company.objects.count(), 0)

        # sync addresses of households and their members

        ses = rt.login("robin")
        # ses = None

        tess = create(Household, ses, name="Tom & Tina Tess", city=eupen)
        tom = create(Person,
                     ses,
                     first_name="Tom",
                     last_name="Tess",
                     city=eupen)

        self.assertEqual(tom.get_address_parent(), None)

        mem = create(Member, ses, person=tom, household=tess, primary=True)
        self.assertEqual(tom.get_address_parent(), tess)

        # both Tom and his family have an address and it's primary for both

        # s = rt.models.addresses.Addresses.request().to_rst()
        s = rt.shows(rt.models.addresses.Addresses)
        # print(s)
        self.assertEqual(
            s, """\
================= ================== ======== ============ ========= ==================
 Partner           Address type       Remark   Address      Primary   Data source
----------------- ------------------ -------- ------------ --------- ------------------
 Tom & Tina Tess   Official address            4700 Eupen   Yes       Manually entered
 Tess Tom          Official address            4700 Eupen   Yes       Manually entered
================= ================== ======== ============ ========= ==================

""")

        # This is a fixable checkdata problem for Tom (not for the family)

        tess.check_data.run_from_ui(ses, fix=False)
        assert_check(tess, "")
        # print("20231225b", tom.check_data.__class__)
        tom.check_data.run_from_ui(ses, fix=False)
        assert_check(tom, "(★) Same primary address as Tom & Tina Tess.")
        tom.check_data.run_from_ui(ses, fix=True)
        self.assertEqual(Address.objects.count(), 1)
        assert_check(tom, "")

        # Another situation is when the member has a primary address
        # and the family has no address. This is fixable by moving the address
        # from the member to the family.

        addr = Address.objects.get(partner=tess)
        addr.partner = tom
        addr.full_clean()
        addr.save()

        tom.check_data.run_from_ui(ses, fix=False)
        assert_check(tom, "(★) Primary address should be on Tom & Tina Tess.")
        tom.check_data.run_from_ui(ses, fix=True)
        self.assertEqual(Address.objects.count(), 1)
        assert_check(tom, "")
        self.assertEqual(Address.objects.count(), 1)

        # Another situation is when both member and household have a primary
        # address and these addresses differ. This is not automatically fixable.
        # The end user should either remove one of the addresses or mark the
        # membership as non primary.

        raeren = Place.objects.get(name="Raeren")
        addr = Address(partner=tom, city=raeren, primary=True)
        addr.full_clean()
        addr.save()
        tom.check_data.run_from_ui(ses, fix=False)
        assert_check(tom,
                     "Primary address differs from that of Tom & Tina Tess.")
