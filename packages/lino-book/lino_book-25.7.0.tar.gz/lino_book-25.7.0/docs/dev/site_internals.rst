.. doctest docs/dev/site_internals.rst

===================================
More about the :class:`Site` class
===================================

.. contents::
    :depth: 1
    :local:


.. currentmodule:: lino.core.site


Additional local plugins
========================

An optional second positional argument can be specified by the  :term:`server
administrator` in order to specify additional *local plugins*. These will go
into the :setting:`INSTALLED_APPS` setting, together with any other plugins
needed by them.

>>> from lino_book.projects.min9.settings import Site
>>> pseudoglobals = {}
>>> Site(pseudoglobals, "lino_xl.lib.events")  #doctest: +ELLIPSIS
<lino_book.projects.min9.settings.Site object at ...>
>>> print('\n'.join(pseudoglobals['INSTALLED_APPS']))
... #doctest: +REPORT_UDIFF +NORMALIZE_WHITESPACE
lino
lino.modlib.about
lino.modlib.jinja
lino.modlib.bootstrap3
lino.modlib.extjs
lino.modlib.printing
lino.modlib.system
lino.modlib.help
lino.modlib.office
lino_xl.lib.xl
lino_xl.lib.countries
lino_book.projects.min9.modlib.contacts
django.contrib.contenttypes
lino.modlib.gfks
lino_xl.lib.excerpts
lino.modlib.users
lino.modlib.linod
lino.modlib.checkdata
lino_xl.lib.addresses
lino_xl.lib.phones
lino_xl.lib.cal
lino_xl.lib.reception
lino_xl.lib.courses
lino_xl.lib.sepa
lino.modlib.memo
lino_xl.lib.notes
lino_xl.lib.humanlinks
lino_xl.lib.households
lino_xl.lib.calview
lino.modlib.publisher
lino.modlib.export_excel
lino_xl.lib.dupable_partners
lino.modlib.tinymce
lino.modlib.weasyprint
lino_xl.lib.appypod
lino.modlib.notify
lino.modlib.changes
lino.modlib.comments
lino.modlib.uploads
lino_xl.lib.properties
lino.modlib.languages
lino_xl.lib.cv
lino_xl.lib.b2c
lino_xl.lib.products
lino.modlib.periods
lino_xl.lib.accounting
lino_xl.lib.vat
lino_xl.lib.trading
lino_xl.lib.finan
lino_xl.lib.shopping
lino_xl.lib.tickets
lino_xl.lib.agenda
django.contrib.staticfiles
lino_xl.lib.events
django.contrib.sessions

As an :term:`application developer` you won't specify this argument, you should
specify your installed plugins by overriding :meth:`get_installed_plugins
<lino.core.site.Site.get_installed_plugins>`.

Besides this you can override any class argument using a keyword
argment of same name:

- :attr:`lino.core.site.Site.title`
- :attr:`lino.core.site.Site.verbose_name`

You've maybe heard that it is not allowed to modify Django's settings
once it has started.  But there's nothing illegal with this here
because this happens before Django has seen your :xfile:`settings.py`.

Lino does more than this. It will for example read the `__file__
<http://docs.python.org/2/reference/datamodel.html#index-49>`__
attribute of this, to know where your :file:`settings.py` is in the
file system.



Technical details
=================

Here are the Django settings that :class:`Lino` writes into the global context
of a settings module:

>>> from lino_book.projects.min1.settings import Site
>>> SITE = Site()
>>> sorted(SITE.django_settings.keys())
... #doctest: +ELLIPSIS +REPORT_UDIFF +NORMALIZE_WHITESPACE
['AUTHENTICATION_BACKENDS', 'AUTH_USER_MODEL', 'DATABASES',
'DEFAULT_AUTO_FIELD', 'EMAIL_SUBJECT_PREFIX', 'FIXTURE_DIRS', 'INSTALLED_APPS',
'LANGUAGES', 'LANGUAGE_CODE', 'LOCALE_PATHS', 'LOGIN_REDIRECT_URL', 'LOGIN_URL',
'LOGOUT_REDIRECT_URL', 'MEDIA_ROOT', 'MEDIA_URL', 'MIDDLEWARE', 'ROOT_URLCONF',
'SERIALIZATION_MODULES', 'STATIC_ROOT', 'STATIC_URL', 'TEMPLATES', 'USE_TZ']

>>> from pprint import pprint
>>> pprint(SITE.django_settings)
... #doctest: +ELLIPSIS +REPORT_UDIFF +NORMALIZE_WHITESPACE
{'AUTHENTICATION_BACKENDS': ['lino.core.auth.backends.ModelBackend'],
 'AUTH_USER_MODEL': 'users.User',
 'DATABASES': {'default': {'ENGINE': 'django.db.backends.sqlite3',
                           'NAME': '.../book/default.db'}},
 'DEFAULT_AUTO_FIELD': 'django.db.models.BigAutoField',
 'EMAIL_SUBJECT_PREFIX': '[book] ',
 'FIXTURE_DIRS': (),
 'INSTALLED_APPS': ('lino',
                    'lino.modlib.about',
                    'lino.modlib.jinja',
                    'lino.modlib.bootstrap3',
                    'lino.modlib.extjs',
                    'lino.modlib.printing',
                    'lino.modlib.system',
                    'lino.modlib.users',
                    'lino.modlib.office',
                    'lino_xl.lib.xl',
                    'lino_xl.lib.countries',
                    'lino_xl.lib.contacts',
                    'django.contrib.staticfiles',
                    'django.contrib.sessions'),
 'LANGUAGES': [('de', 'German'), ('en', 'English'), ('fr', 'French')],
 'LANGUAGE_CODE': 'en',
 'LOCALE_PATHS': (),
 'LOGIN_REDIRECT_URL': '/',
 'LOGIN_URL': '/accounts/login/',
 'LOGOUT_REDIRECT_URL': None,
 'MEDIA_ROOT': '.../book/media',
 'MEDIA_URL': '/media/',
 'MIDDLEWARE': ('django.middleware.common.CommonMiddleware',
                'django.middleware.locale.LocaleMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'lino.core.auth.middleware.AuthenticationMiddleware',
                'lino.core.auth.middleware.WithUserMiddleware'),
 'ROOT_URLCONF': 'lino.core.urls',
 'SERIALIZATION_MODULES': {'py': 'lino.utils.dpy'},
 'STATIC_ROOT': '...static_root',
 'STATIC_URL': '/static/',
 'TEMPLATES': [{'APP_DIRS': True,
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [],
                'OPTIONS': {'context_processors': ['django.template.context_processors.debug',
                                                   'django.template.context_processors.i18n',
                                                   'django.template.context_processors.media',
                                                   'django.template.context_processors.static',
                                                   'django.template.context_processors.tz',
                                                   'django.contrib.messages.context_processors.messages']}},
               {'BACKEND': 'django.template.backends.jinja2.Jinja2',
                'DIRS': [],
                'OPTIONS': {'environment': 'lino.modlib.jinja.get_environment'}}],
 'USE_TZ': False}

Note that Lino writes to the global namespace of your settings module only while
the :class:`Site` class gets *instantiated*.  So if for some reason you want to
modify one of the settings, do it *after* your ``SITE=Site(globals())`` line.
