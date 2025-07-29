# -*- coding: UTF-8 -*-
# Copyright 2013-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino_book.projects.polly.settings import *


class Site(Site):
    title = Site.verbose_name + " demo"
    # The polly demo project has NOT demo date set because
    # the_demo_date = 20141023
    default_ui = 'lino_react.react'


SITE = Site(globals())

DEBUG = True
# the following line should always be commented out in a checked-in version
# DATABASES['default']['NAME'] = ':memory:'

USE_TZ = True
TIME_ZONE = "Europe/Tallinn"
