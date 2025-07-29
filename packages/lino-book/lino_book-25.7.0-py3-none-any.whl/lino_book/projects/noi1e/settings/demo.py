# -*- coding: UTF-8 -*-
# Copyright 2014-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from ..settings import *

SITE = Site(globals())

# SITE.plugins.extjs6.configure(theme_name='theme-classic')
# SITE.plugins.extjs6.configure(theme_name='theme-classic-sandbox')
# SITE.plugins.extjs6.configure(theme_name='theme-aria')
# SITE.plugins.extjs6.configure(theme_name='theme-grey')
# SITE.plugins.extjs6.configure(theme_name='theme-crisp')
# SITE.plugins.extjs6.configure(theme_name='theme-crisp-touch')
# SITE.plugins.extjs6.configure(theme_name='theme-neptune')
# SITE.plugins.extjs6.configure(theme_name='theme-neptune-touch')
# SITE.plugins.extjs6.configure(theme_name='theme-triton')
# SITE.plugins.extjs6.configure(theme_name='ext-theme-neptune-lino')

#in etc/aliases
# comments: /home/tonis/mbox
#SITE.plugins.inbox.configure(mailbox_path='/home/tonis/mbox')
#SITE.plugins.inbox.configure(comment_reply_addr='comments@localhost')

# the following line should not be active in a checked-in version
#~ DATABASES['default']['NAME'] = ':memory:'

# SITE.update_settings(ALLOWED_HOSTS=["192.168.0.26","127.0.0.1"])

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
