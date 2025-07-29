# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""General demo data for Lino LETS.

"""

from lino.api import rt


def findbyname(model, name):
    """
    Utility function.
    """
    return model.objects.get(name=name)


def objects():
    """This will be called by the :ref:`dpy` deserializer during
    :cmd:`pm prep` and must yield a list of object instances to
    be saved.

    """
    Place = rt.models.market.Place
    User = rt.models.users.User
    Product = rt.models.market.Product

    def offer(what, who):
        return rt.models.market.Offer(
            product=findbyname(Product, what),
            provider=User.objects.get(first_name=who))

    def demand(what, who):
        return rt.models.market.Demand(
            product=findbyname(Product, what),
            customer=User.objects.get(first_name=who))

    def member(name, place, email=''):
        return User(username=name.lower(),
                    first_name=name,
                    email=email,
                    user_type="100",
                    place=findbyname(Place, place))

    yield Place(name="Tallinn")
    yield Place(name="Tartu")
    yield Place(name="Vigala")
    yield Place(name="Haapsalu")

    yield Product(name="Bread")
    yield Product(name="Buckwheat", delivery_unit="kg")
    yield Product(name="Eggs")
    yield Product(name="Sanitary repair work", delivery_unit="hour")
    yield Product(name="Building repair work", delivery_unit="hour")
    yield Product(name="Electricity repair work", delivery_unit="hour")

    yield member("Fred", "Tallinn", 'fred@example.com')
    yield member("Argo", "Haapsalu", 'argo@example.com')
    yield member("Peter", "Vigala", 'peter@example.com')
    yield member("Anne", "Tallinn", 'anne@example.com')
    yield member("Jaanika", "Tallinn", 'jaanika@example.com')

    yield member("Henri", "Tallinn", 'henri@example.com')
    yield member("Mari", "Tartu", 'mari@example.com')
    yield member("Katrin", "Vigala", 'katrin@example.com')

    yield offer("Bread", "Fred")
    yield offer("Buckwheat", "Fred")
    yield offer("Buckwheat", "Anne")
    yield offer("Electricity repair work", "Henri")
    yield offer("Electricity repair work", "Argo")

    yield demand("Buckwheat", "Henri")
    yield demand("Eggs", "Henri")
    yield demand("Eggs", "Mari")
