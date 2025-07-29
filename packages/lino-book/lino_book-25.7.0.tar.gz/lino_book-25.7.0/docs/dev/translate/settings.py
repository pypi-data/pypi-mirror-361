# -*- coding: UTF-8 -*-

from lino_book.projects.min9.settings import *


class Site(Site):
    title = "My Lino Mini site"
    languages = 'en es'


SITE = Site(globals())
