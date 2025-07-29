# -*- coding: UTF-8 -*-
# Copyright 2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Add a `place` field to the `users.User` model.

"""

from lino.api import dd, _

from lino.modlib.users.models import *
# from lino.core.actors import qs2summary
from .ui import *


class User(User):

    class Meta(User.Meta):
        abstract = dd.is_abstract_model(__name__, 'User')
        verbose_name = _("Member")
        verbose_name_plural = _("Members")

    place = dd.ForeignKey('market.Place', blank=True, null=True)

    # @dd.displayfield("Offered products")
    # def offered_products(self, ar):
    #     return qs2summary(ar, self.offered_products.all())
    #
    # @dd.displayfield("Wanted products")
    # def wanted_products(self, ar):
    #     return qs2summary(ar, self.wanted_products.all())
