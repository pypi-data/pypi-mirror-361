# -*- coding: UTF-8 -*-
# Copyright 2015-2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Settings for providing readonly public access to the site. This
does not use :mod:`lino.modlib.extjs` but :mod:`lino.modlib.bootstrap3`.

"""

import datetime

from ..settings import *


class Site(Site):
    is_demo_site = True
    the_demo_date = datetime.date(2015, 5, 23)
    languages = "en de fr"
    readonly = True
    # default_user = 'anonymous'
    master_site = SITE


SITE = Site(globals())

DEBUG = True
