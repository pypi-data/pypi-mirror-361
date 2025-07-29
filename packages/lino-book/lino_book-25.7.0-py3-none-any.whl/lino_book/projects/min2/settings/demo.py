# from lino_book.projects.min2.settings import *
from ..settings import *
from lino.utils import i2d


class Site(Site):
    languages = "en de fr"
    is_demo_site = True
    the_demo_date = i2d(20170819)
    # default_ui = "lino_react.react"


SITE = Site(globals())
DEBUG = True
