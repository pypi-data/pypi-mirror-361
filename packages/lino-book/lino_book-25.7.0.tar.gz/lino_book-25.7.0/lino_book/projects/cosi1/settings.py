# -*- coding: UTF-8 -*-
# Copyright 2014-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Default settings for a :ref:`cosi` "à la APC".

"""

from lino_cosi.lib.cosi.settings import *
from lino_book.projects.noi1e.settings.data import suppliers

me = suppliers[0]


class Site(Site):

    demo_fixtures = ['std', 'minimal_ledger', 'furniture',  'demo',
                     'demo_bookings', 'payments', 'demo2', 'demo3', 'checkdata']

    project_name = 'cosi1'
    is_demo_site = True
    the_demo_date = 20250312
    use_help = True
    languages = 'de fr en'
    # use_ipdict = True

    default_ui = "lino_react.react"
    user_types_module = "lino_book.projects.cosi1.user_types"
    # use_peppol = True

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        yield ('linod', 'use_channels', True)
        yield ('notify', 'use_push_api', True)
        yield ('vat', 'declaration_plugin', 'lino_xl.lib.bevat')
        yield ('countries', 'hide_region', True)
        yield ('countries', 'country_code', 'BE')
        yield ('excerpts', 'responsible_user', 'robin')
        yield ('accounting', 'use_pcmn', True)
        yield ('accounting', 'payer_model', 'contacts.Person')
        yield ('periods', 'start_year', 2023)
        # yield ('users', 'active_sessions_limit', 1)
        # yield ("peppol", "simulate_endpoints", True)
        yield ("peppol", "supplier_id", me.supplier_id)
        yield ("contacts", "site_owner_lookup", dict(vat_id=me.vat_id))
        # yield ("peppol", "inbound_journal", "INB")
        # yield ("peppol", "outbound_model", "trading.VatProductInvoice")
        # yield ("peppol", "inbound_model", "vat.VatAccountInvoice")
        yield ("trading", "columns_to_print", "qty title unit_price amount")
        yield ("trading", "items_column_names",
               "product qty title unit_price amount vat_class:3 invoiceable *")

    # def pre_site_startup(self, site):
    #     for vt in site.models.trading.VoucherTypes.get_list_items():
    #         if vt.model is site.models.trading.VatProductInvoice:
    #             vt.columns_to_print = "qty title unit_price amount".split()
    #     super().pre_site_startup(site)


SITE = Site(globals())

DEBUG = True
