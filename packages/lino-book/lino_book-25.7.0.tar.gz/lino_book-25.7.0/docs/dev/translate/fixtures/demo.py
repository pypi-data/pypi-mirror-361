# This is needed only if Lino does not yet have a default site
# administrator for your language.

from django.conf import settings
from lino.modlib.users.choicelists import UserTypes


def objects():
    yield settings.SITE.user_model(username="roberto",
                                   language="es",
                                   first_name="Roberto",
                                   last_name="Spanish",
                                   email=settings.SITE.demo_email,
                                   user_type=UserTypes.admin)
