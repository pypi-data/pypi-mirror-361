# -*- coding: UTF-8 -*-
# Copyright 2015-2016 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""The :xfile:`settings.py` modules for this variant.

.. autosummary::
   :toctree:

   demo
   doctests

"""

from lino_book.projects.noi1e.settings.demo import *


class Site(Site):

    default_ui = 'lino_noi.lib.public'
    default_user = 'anonymous'

    # def get_installed_plugins(self):
    #     yield super(Site, self).get_installed_plugins()
    #     yield 'lino.modlib.bootstrap3'
