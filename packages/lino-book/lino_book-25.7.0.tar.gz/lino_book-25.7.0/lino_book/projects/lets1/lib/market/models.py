# -*- coding: UTF-8 -*-
# Copyright 2020-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models
from lino.api import dd, _
from lino.utils import join_elems
from lino.utils.html import E
from lino.core.actors import qs2summary
from lino.utils.mldbc.mixins import BabelNamed
from .ui import *


class DeliveryUnits(dd.ChoiceList):
    verbose_name = _("Delivery unit")
    verbose_name_plural = _("Delivery units")


add = DeliveryUnits.add_item
add('10', _("Hours"), 'hour')
add('20', _("Pieces"), 'piece')
add('30', _("Kg"), 'kg')
add('40', _("Boxes"), 'box')


class Place(dd.Model):

    class Meta:
        verbose_name = _("Place")
        verbose_name_plural = _("Places")

    name = dd.CharField(_("Name"), max_length=200)

    def __str__(self):
        return self.name


class Product(dd.Model):

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    name = dd.CharField(_("Designation"), max_length=200)
    description = dd.RichTextField(_("Description"), blank=True)
    delivery_unit = DeliveryUnits.field(default='piece')

    def __str__(self):
        return self.name


class Offer(dd.Model):

    class Meta:
        verbose_name = _("Offer")
        verbose_name_plural = _("Offers")

    provider = dd.ForeignKey('users.User')
    product = dd.ForeignKey(Product)
    valid_until = models.DateField(blank=True, null=True)

    def __str__(self):
        return "%s offered by %s" % (self.product, self.provider)

    def on_create(self, ar):
        super().on_create(ar)
        self.provider = ar.get_user()

    def disabled_fields(self, ar):
        df = super().disabled_fields(ar)
        me = ar.get_user()
        if not me.user_type.has_required_roles([dd.SiteAdmin]):
            df.add("provider")
        return df

    def as_paragraph(self, ar, **kwargs):
        if ar is None:
            return str(self)
        if ar.is_obvious_field('provider'):
            return self.product.as_paragraph(ar, **kwargs)
        if ar.is_obvious_field('product'):
            return self.provider.as_paragraph(ar, **kwargs)
        return ar.obj2htmls(self)


class Demand(dd.Model):

    class Meta:
        verbose_name = _("Demand")
        verbose_name_plural = _("Demands")

    customer = dd.ForeignKey('users.User')
    product = dd.ForeignKey(Product)
    urgent = models.BooleanField(default=False)

    def on_create(self, ar):
        super().on_create(ar)
        self.customer = ar.get_user()

    def __str__(self):
        return "%s (%s)" % (self.product, self.customer)

    def as_paragraph(self, ar, **kwargs):
        if ar is None:
            return str(self)
        if ar.is_obvious_field('customer'):
            return self.product.as_paragraph(ar, **kwargs)
        if ar.is_obvious_field('product'):
            return self.customer.as_paragraph(ar, **kwargs)
        return ar.obj2htmls(self)
