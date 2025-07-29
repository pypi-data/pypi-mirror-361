import datetime

from lino_avanti.lib.avanti.settings import *


class Site(Site):
    title = "avanti2"
    the_demo_date = datetime.date(2024, 12, 18)
    is_demo_site = True
    # languages = 'de fr en'
    languages = 'en de fr'
    # languages = "de fr"
    default_ui = "lino_react.react"
    # default_ui = "lino.modlib.extjs"
    # catch_layout_exceptions = True
    # log_each_action_request = True
    demo_fixtures = ["std", "all_languages", "demo", "demo2"]

    # workflows_module = "lino_book.projects.avanti2.workflows"
    # user_types_module = "lino_avanti.lib.avanti.user_types2"

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        yield ('cal', 'with_tasks', False)
        yield ('countries', 'full_data', True)
        # yield ('households', 'hidden', True)
        yield ('humanlinks', 'hidden', True)
        yield ('cv', 'hidden', True)
        yield ('courses', 'hidden', True)
        yield ('polls', 'hidden', True)
        yield ('avanti', 'with_asylum', True)
        yield ('avanti', 'with_immigration', False)
        yield ('clients', 'demo_coach', 'nathalie')
        # yield ('beid', 'simulate_eidreader_path',
        #     self.project_dir / 'simulate_eidreader')
        yield ('uploads', 'remove_orphaned_files', True)
        # yield ('contacts', 'show_birthdays', False)


SITE = Site(globals())

DEBUG = True

# the following line should not be active in a checked-in version
# ~ DATABASES['default']['NAME'] = ':memory:'

# SITE.eidreader_timeout = 25
