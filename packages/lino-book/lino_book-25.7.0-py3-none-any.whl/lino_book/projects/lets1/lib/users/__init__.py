# -*- coding: UTF-8 -*-
# Copyright 2020-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Lino LETS extension of :mod:`lino.modlib.users`.

"""

from lino.modlib.users import Plugin
from lino.ad import _


class Plugin(Plugin):

    extends_models = ['User']
    verbose_name = _("Members")

    def setup_main_menu(self, site, user_type, m, ar=None):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('users.AllUsers')
