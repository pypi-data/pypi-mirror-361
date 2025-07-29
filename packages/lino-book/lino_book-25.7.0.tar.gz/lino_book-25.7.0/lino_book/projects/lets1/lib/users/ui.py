# -*- coding: UTF-8 -*-
# Copyright 2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""User interface (actors) for this plugin.

"""

from lino.api import dd, _

from lino.modlib.users.ui import *


class UserDetail(UserDetail):
    """Layout of User Detail in Lino LETS."""

    main = "general contact"

    general = dd.Panel("""
    box1
    remarks:40 users.AuthoritiesGiven:20
    """,
                       label=_("General"))

    box1 = """
    username user_type:20
    language time_zone
    id created modified
    """

    contact = dd.Panel("""
    first_name last_name initials
    place
    market.DemandsByCustomer market.OffersByProvider
    """,
                       label=_("Contact"))


# Users.detail_layout = UserDetail()

# Users.column_names = "first_name email place offered_products wanted_products"

Users.column_names = "first_name place market.OffersByProvider market.DemandsByCustomer"

# class Users(Users):
#
#     column_names = "first_name email place market.OffersByProvider market.DemandsByCustomer"
#
# class AllUsers(AllUsers, Users):
#
#     column_names = "first_name email place market.OffersByProvider market.DemandsByCustomer"
