import datetime

from lino_avanti.lib.avanti.settings import *


class Site(Site):

    the_demo_date = datetime.date(2017, 2, 15)
    is_demo_site = True
    # languages = 'de fr en'
    languages = "en de fr"
    default_ui = "lino_react.react"
    # catch_layout_exceptions = False

    # default_ui = "lino.modlib.extjs"
    # use_linod = True
    # log_each_action_request = True

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        yield ('clients', 'demo_coach', 'nathalie')
        # yield ('beid', 'simulate_eidreader_path',
        #     self.project_dir / 'simulate_eidreader')
        yield ('uploads', 'remove_orphaned_files', True)
        # yield ('contacts', 'show_birthdays', False)


SITE = Site(globals())

DEBUG = True

# the following line should not be active in a checked-in version
#~ DATABASES['default']['NAME'] = ':memory:'

# SITE.eidreader_timeout = 25
