# -*- coding: UTF-8 -*-
# Copyright 2014-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# Documentation:  https://dev.lino-framework.org/projects/cosi3.html

from django.utils.translation import gettext_lazy as _
from lino_cosi.lib.cosi.settings import *


class Site(Site):
    languages = 'en et'

    demo_fixtures = ['std', 'minimal_ledger',
                     'furniture', 'demo', 'demo_bookings', 'payments', 'demo2', 'checkdata']

    is_demo_site = True
    # ignore_dates_after = datetime.date(2019, 05, 22)
    the_demo_date = 20240612
    default_ui = 'lino_react.react'
    with_assets = True

    # def do_site_startup(self):
    #     # change the number of decimal places from 4 to 2:
    #     update_field = self.models.trading.InvoiceItem.update_field
    #     update_field('unit_price', decimal_places=2)
    #     update_field('total_base', decimal_places=2)
    #     super().do_site_startup()

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        yield ('contacts', 'demo_region', "EE")
        yield ('countries', 'hide_region', False)
        yield ('countries', 'country_code', 'EE')
        yield ('countries', 'full_data', True)
        yield ('excerpts', 'responsible_user', 'robin')
        yield ('accounting', 'use_pcmn', True)
        yield ('periods', 'start_year', 2023)
        yield ('help', 'make_help_pages', True)
        yield ('weasyprint', 'margin_left', 40)

        yield ('vat', 'declaration_plugin', 'lino_xl.lib.eevat')
        yield ('vat', 'unit_price_decpos', 2)
        yield ('vat', 'item_vat', True)

        yield ("trading", "items_column_names",
               "product invoiceable_id qty amount discount_amount unit_price *")
        yield ("trading", "subtotal_demo", True)
        yield ('invoicing', 'order_model', 'assets.PartnerAsset')
        yield ('invoicing', 'invoiceable_label', _("License plate"))
        yield ('invoicing', 'short_invoiceable_label', _("Plate"))
        yield ('assets', 'asset_name', _("License plate"))
        yield ('assets', 'asset_name_plural', _("License plates"))
        # yield ('assets', 'asset_name_short', _("Plate"))


SITE = Site(globals())
DEBUG = True
