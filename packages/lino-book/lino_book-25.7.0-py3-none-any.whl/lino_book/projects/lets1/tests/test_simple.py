# -*- coding: utf-8 -*-
# Copyright 2011-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# python setup.py test -s tests.DemoTests.test_simple

from django.core.exceptions import ValidationError
from lino.utils.djangotest import RemoteAuthTestCase
from lino.api import rt


def create(m, **kwargs):
    obj = m(**kwargs)
    obj.full_clean()
    obj.save()
    return obj


class SimpleTests(RemoteAuthTestCase):
    maxDiff = None

    def test01(self):
        User = rt.models.users.User
        UserTypes = rt.models.users.UserTypes
        Product = rt.models.market.Product

        robin = create(User,
                       username='robin',
                       user_type=UserTypes.admin,
                       language="en")

        foo = create(Product, name='Foo')
