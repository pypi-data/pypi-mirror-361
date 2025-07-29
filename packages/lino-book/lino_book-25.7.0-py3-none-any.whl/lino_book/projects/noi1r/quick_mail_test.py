# -*- coding: UTF-8 -*-
# Copyright 2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""

Usage::

    pm run quick_mail_test.py


"""

from django.core.mail import mail_admins
from django.conf import settings
# from django.core.mail import get_connection
# from django.core.mail.backends.smtp import EmailBackend


# backend = get_connection(local_hostname="127.0.0.1")
# print(backend.connection.local_hostname)

for k in ("ADMINS", "EMAIL_HOST", "EMAIL_HOST_USER",
 "DEFAULT_FROM_EMAIL", "SERVER_EMAIL", "EMAIL_PORT", "EMAIL_USE_TLS",
 "EMAIL_USE_SSL"):
    print("{0} : {1}".format(k, getattr(settings, k)))

mail_admins(
    "A quick mail",
    "A short message body.",
    fail_silently=False)
    # fail_silently=False, connection=backend.connection)
