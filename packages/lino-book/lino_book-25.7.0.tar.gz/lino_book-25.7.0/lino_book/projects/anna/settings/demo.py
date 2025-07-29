# import os ; print "20161219 %s (pid:%s)" % (__name__, os.getpid())

from ..settings import *


class Site(Site):
    """Defines and instantiates a demo version of Lino Care."""

    # default_ui = 'lino_extjs6.extjs6'
    # default_ui = 'lino_react.react'

    is_demo_site = True
    the_demo_date = 20150523

    languages = "en de fr"


SITE = Site(globals())
# print "20161219 b"
DEBUG = True

# the following line should not be active in a checked-in version
# DATABASES['default']['NAME'] = ':memory:'
