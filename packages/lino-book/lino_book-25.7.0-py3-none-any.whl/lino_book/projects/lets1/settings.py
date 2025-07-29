from lino.projects.std.settings import *
from lino.ad import _


class Site(Site):

    title = "LETS v1"
    is_demo_site = True
    url = "https://dev.lino-framework.org/dev/lets"
    demo_fixtures = ['demo', 'demo2']

    default_ui = 'lino_react.react'

    def get_installed_plugins(self):
        yield super().get_installed_plugins()
        yield 'lino_book.projects.lets1.lib.users'
        yield 'lino_book.projects.lets1.lib.market'


SITE = Site(globals())

USE_TZ = True
TIME_ZONE = 'UTC'


# the_demo_date = datetime.date(2015, 5, 23)

# default_ui = 'lino_react.react'


DEBUG = True

# the following line should not be active in a checked-in version
# ~ DATABASES['default']['NAME'] = ':memory:'
