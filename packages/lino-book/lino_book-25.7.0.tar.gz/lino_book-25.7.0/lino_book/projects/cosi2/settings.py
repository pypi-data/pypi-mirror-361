# -*- coding: UTF-8 -*-
# Copyright 2014-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Default settings for a :ref:`cosi` site "à la Pierre".

"""

from lino_cosi.lib.cosi.settings import *
from lino_book.projects.noi1e.settings.data import suppliers

me = suppliers[1]
# print("20250618", me.names)
# assert me.names == "Number Two"


class Site(Site):
    languages = 'fr en'

    demo_fixtures = ['std', 'minimal_ledger',
                     'furniture', 'demo', 'demo_bookings', 'demo2', 'checkdata']

    # default_ui = "lino_react.react"

    default_ui = "lino_react.react"
    is_demo_site = True
    the_demo_date = 20250312

    # ignore_dates_after = datetime.date(2019, 05, 22)

    def get_installed_plugins(self):
        yield super().get_installed_plugins()
        yield 'lino_xl.lib.b2c'
        yield 'lino_xl.lib.cars'

    def get_plugin_modifiers(self, **kw):
        # disable invoicing
        kw = super().get_plugin_modifiers(**kw)
        kw.update(invoicing=None)
        return kw

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        # yield ('vat', 'declaration_plugin', 'lino_xl.lib.bevat')
        # yield ('invoicing', 'hidden', True)
        yield ('contacts', 'demo_region', 'BE')
        yield ('countries', 'hide_region', True)
        yield ('countries', 'country_code', 'BE')
        yield ('accounting', 'project_model', "cars.Car")
        yield ('accounting', 'use_pcmn', True)
        yield ('accounting', 'payer_model', 'contacts.Company')
        yield ('periods', 'start_year', 2023)
        yield ('vat', 'declaration_plugin', 'lino_xl.lib.bevat')
        yield ('vat', 'item_vat', True)

        yield ("trading", "items_column_names",
               "product qty amount discount_amount unit_price *")

        # yield ('vat', 'use_online_check', True)  # doctest docs/topics/vies.rst
        # yield ('accounting', 'payer_model', 'contacts.Person')
        # yield ("peppol", "simulate_endpoints", True)
        yield ("peppol", "supplier_id", me.supplier_id)
        yield ("contacts", "site_owner_lookup", dict(vat_id=me.vat_id))


SITE = Site(globals())
DEBUG = True
