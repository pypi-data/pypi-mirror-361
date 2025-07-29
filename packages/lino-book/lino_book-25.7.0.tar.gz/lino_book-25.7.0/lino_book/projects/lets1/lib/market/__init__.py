# Copyright 2014-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import ad, _

class Plugin(ad.Plugin):
    verbose_name = _("Market")
    def setup_main_menu(self, site, user_type, m, ar=None):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('market.Products')
        m.add_action('market.Offers')
        m.add_action('market.Demands')

    def setup_config_menu(self, site, user_type, m, ar=None):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('market.Places')

    def setup_explorer_menu(self, site, user_type, m, ar=None):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('market.DeliveryUnits')

    def setup_quicklinks(self, tb):
        super().setup_quicklinks(tb)
        tb.add_action('market.Products')

    def get_dashboard_items(self, user):
        yield 'market.ActiveProducts'
        # yield self.models.market.ActiveProducts
