from lino_book.projects.belref.settings import *

SITE = Site(globals(), title=Site.verbose_name + " demo", is_demo_site=True)
DEBUG = True
# the following line should always be commented out in a checked-in version
#~ DATABASES['default']['NAME'] = ':memory:'
