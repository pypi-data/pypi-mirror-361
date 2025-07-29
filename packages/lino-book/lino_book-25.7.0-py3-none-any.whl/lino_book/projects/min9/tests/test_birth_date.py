# -*- coding: utf-8 -*-
# Copyright 2015-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Test certain aspects of `birth_date`.

This module is part of the Lino test suite. You can test only this
module by issuing either::

  $ go min9
  $ python manage.py test tests.test_birth_date


"""

from lino.api import rt

from lino.utils import IncompleteDate
from lino.utils.html import tostring
from lino.utils.mti import insert_child, delete_child
from lino.utils.djangotest import RemoteAuthTestCase
from django.core.exceptions import ValidationError
from django.utils import translation


def create(m, **kw):
    obj = m(**kw)
    obj.full_clean()
    obj.save()
    obj.after_ui_save(None, None)
    return obj


class QuickTest(RemoteAuthTestCase):

    fixtures = ['std']

    def test_this(self):

        Person = rt.models.contacts.Person
        Link = rt.models.humanlinks.Link
        LinkTypes = rt.models.humanlinks.LinkTypes
        LinksByHuman = rt.models.humanlinks.LinksByHuman

        father = create(Person,
                        first_name="John",
                        last_name="Doe",
                        gender="M",
                        birth_date='1980-07-31')
        try:
            son = create(Person,
                         first_name="Joseph",
                         last_name="Doe",
                         gender="M",
                         birth_date=IncompleteDate(2009, 2, 30))
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError")
        son = create(Person,
                     first_name="Joseph",
                     last_name="Doe",
                     gender="M",
                     birth_date='2009-02-28')
        create(Link, parent=father, child=son, type=LinkTypes.parent)

        mary = create(Person,
                      first_name="Mary",
                      last_name="Doe",
                      gender="F",
                      birth_date='2010-01-30')
        create(Link, parent=father, child=mary, type=LinkTypes.parent)

        self.assertEqual(Person.objects.count(), 3)

        # ar = LinksByHuman.request(father)
        # s = ar.to_rst()
        s = rt.shows(LinksByHuman, father)
        # print(s)
        self.assertEquivalent(
            """

        John is Father of `Mary <…>`__ (4 years 8 months),
        `Joseph <…>`__ (5 years) """, s)

        # Create relationship as **Father**/**Son** **Adoptive
        # father**/**Adopted son** **Foster father**/**Foster son**
        # **Husband** **Partner** **Stepfather**/**Stepson** **Brother**
        # **Cousin** **Uncle**/**Nephew** **Relative** **Other** """, s)

        with translation.override('de'):
            # ar = LinksByHuman.request(father)
            # s = ar.to_rst()
            s = rt.shows(LinksByHuman, father)
            # print(s)
            self.assertEquivalent(
                """

            John ist Vater von `Mary <…>`__ (4 Jahre 8 Monate),
            `Joseph <…>`__ (5 Jahre) """, s)

            # Beziehung erstellen als **Vater**/**Sohn**
            # **Adoptivvater**/**Adoptivsohn**
            # **Pflegevater**/**Pflegesohn** **Ehemann** **Partner**
            # **Stiefvater**/**Stiefsohn** **Bruder** **Vetter**
            # **Onkel**/**Neffe** **Verwandter** **Sonstiger** """, s)

        with translation.override('fr'):
            # ar = LinksByHuman.request(father)
            # s = ar.to_rst()
            s = rt.shows(LinksByHuman, father)
            # print(s)
            self.assertEquivalent(
                """

            John est Père de `Mary <…>`__ (4 ans 8 mois), `Joseph <…>`__
            (5 ans) """, s)

            # Créer lien de parenté en tant que **Père**/**Fils** **Père
            # adoptif**/**Fils adoptif** **Père nourricier**/**Fils
            # nourricier** **Mari** **Partenaire**
            # **Beau-père**/**Beau-fils** **Frère** **Cousin**
            # **Oncle**/**Nephew** **Parent** **Autre** """, s)

        # Here we are just testing whether no exception is risen. The
        # ouptut itself is more thoroughly tested elsewhere.
        ar = rt.login()
        html = LinksByHuman.get_slave_summary(father, ar)
        s = tostring(html)
        self.assertEqual(s[:5], '<div ')

    def test_02(self):
        """Was written for :ticket:`488` (Kann Person nicht mehr von
        Organisation entfernen (delete mti child with siblings)).

        """
        Person = rt.models.contacts.Person
        Company = rt.models.contacts.Company
        Partner = rt.models.contacts.Partner

        # 1 : does delete_child work in normal situation?
        john = create(Person, first_name="John", last_name="Doe")
        as_partner = Partner.objects.get(pk=john.pk)
        delete_child(as_partner, Person)
        self.assertEqual(Person.objects.count(), 0)
        self.assertEqual(Partner.objects.count(), 1)
        as_partner.delete()

        # 2 : delete_child with an mti sibling
        john = create(Person, first_name="John", last_name="Doe")
        as_partner = Partner.objects.get(pk=john.pk)
        insert_child(as_partner, Company, full_clean=True)
        # this is the sitation:
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(Partner.objects.count(), 1)
        self.assertEqual(Company.objects.count(), 1)

        # the following failed before #488 was fixed:
        delete_child(as_partner, Company)
