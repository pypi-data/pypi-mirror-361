# -*- coding: UTF-8 -*-
# Copyright 2020-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db.models import Q
from lino.api import dd


class Places(dd.Table):
    model = 'market.Place'


class Products(dd.Table):
    model = 'market.Product'
    order_by = ['name']

    detail_layout = """
    id name delivery_unit
    description
    market.OffersByProduct market.DemandsByProduct
    """

    insert_layout = """
    name
    delivery_unit
    """

    column_names = 'id name OffersByProduct DemandsByProduct'


class ActiveProducts(Products):

    label = "Active products"
    column_names = 'name OffersByProduct DemandsByProduct'
    insert_layout = None  # disable insert action

    @classmethod
    def get_request_queryset(cls, ar):
        # add filter condition to the queryset so that only active
        # products are shown, i.e. for which there is at least one
        # offer or one demand.
        qs = super().get_request_queryset(ar)
        qs = qs.filter(Q(offer__isnull=False) | Q(demand__isnull=False))
        qs = qs.distinct()
        return qs


class Offers(dd.Table):
    model = 'market.Offer'
    column_names = "id provider product valid_until *"


class OffersByProvider(Offers):
    master_key = 'provider'
    column_names = "id product valid_until *"
    insert_layout = """
    product
    valid_until
    """


class OffersByProduct(Offers):
    master_key = 'product'
    insert_layout = """
    provider
    valid_until
    """


class Demands(dd.Table):
    model = 'market.Demand'
    column_names = "id customer product urgent *"


class DemandsByCustomer(Demands):
    master_key = 'customer'
    column_names = "product urgent id *"
    insert_layout = """
    product
    urgent
    """


class DemandsByProduct(Demands):
    master_key = 'product'
    column_names = "customer urgent id *"
    insert_layout = """
    customer
    urgent
    """
