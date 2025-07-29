# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""The :xfile:`settings.py` modules for this variant.

.. autosummary::
   :toctree:

   demo
   fixtures

"""

from lino_vilma.lib.vilma.settings import *


class Site(Site):
    languages = 'en et'
    title = "Lino Vilma"

    # def setup_plugins(self):
    #     super(Site, self).setup_plugins()
    #     self.plugins.tickets.configure(
    #         site_model='cal.Room')
