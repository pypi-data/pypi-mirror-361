===============
Django settings
===============

This section describes Lino-specific considerations about certain
Django settings.


.. setting:: AUTHENTICATION_BACKENDS

    See https://docs.djangoproject.com/en/5.0/ref/settings/#authentication-backends

    See :doc:`/dev/socialauth/index`

    Unlike with plain Django applications, in Lino you do not need to set
    :setting:`AUTHENTICATION_BACKENDS` yourself, Lino will do that for
    you, based the following criteria:

    - :meth:`get_auth_method <lino.core.site.Site.get_auth_method>`

    - :attr:`social_auth_backends
      <lino.core.site.Site.social_auth_backends>`


.. setting:: DATABASES

    Lino sets this to `SQLite` on a file `default.db` in your
    :attr:`project_dir <lino.core.site.Site.project_dir>`.

    See https://docs.djangoproject.com/en/5.0/ref/settings/#databases

.. setting:: FIXTURE_DIRS

    See `Django docs
    <https://docs.djangoproject.com/en/5.0/ref/settings/#fixture-dirs>`_


.. setting:: LOGGING
.. setting:: LOGGING_CONFIG

Lino sets :setting:`LOGGING_CONFIG` to :func:`lino.utils.log.configure`
which is our suggetion for a lightweight flexible
logging configuration method. If you leave :setting:`LOGGING_CONFIG`
unchanged, you can configure your logging preferences using the
:setting:`LOGGING` setting. Some examples::

    LOGGING = dict(filename='/var/log/lino/system.log'), level='DEBUG')
    LOGGING = dict(filename=join(SITE.project_dir, 'log', 'system.log'), level='DEBUG')
    LOGGING = dict(filename=None, level='DEBUG')

You don't *need* to use Lino's logging config. In that case, refer to
https://docs.djangoproject.com/en/5.0/ref/settings/#logging-config


.. setting:: USE_L10N

Lino sets this automatically when
:attr:`lino.core.site.Site.languages` is not `None`.

See https://docs.djangoproject.com/en/5.0/ref/settings/#use-l10n

.. setting:: LANGUAGE_CODE

Lino sets this automatically when
:attr:`lino.core.site.Site.languages` is not `None`.

See https://docs.djangoproject.com/en/5.0/ref/settings/#language-code

.. setting:: MIDDLEWARE_CLASSES

    Lino still uses `MIDDLEWARE_CLASSES
    <https://docs.djangoproject.com/en/5.0/ref/settings/#middleware-classes>`__
    instead of :setting:`MIDDLEWARE`.  One day we will `upgrade all
    Lino middleware to the new middleware style
    <https://docs.djangoproject.com/en/5.0/topics/http/middleware/#upgrading-middleware>`_.

.. setting:: LANGUAGES

Lino sets this automatically when your :attr:`SITE.languages
<lino.core.site.Site.languages>` is not `None`.

Used by :class:`lino.modlib.fields.LanguageField`.

See https://docs.djangoproject.com/en/5.0/ref/settings/#languages

.. setting:: ROOT_URLCONF

This is set to the value of your :class:`Site <lino.core.site.Site>`\
's :attr:`root_urlconf <lino.core.site.Site.root_urlconf>` attribute
(which itself defaults to :mod:`lino.core.urls`).

See `URL dispatcher
<https://docs.djangoproject.com/en/5.0/topics/http/urls/>`_ section of
the Django documentation.


.. setting:: INSTALLED_APPS

The list of plugins that makes up this :term:`Lino application`. Django calls
them "apps" and expects them to be specified in the :setting:`INSTALLED_APPS`
setting. See `Django docs
<https://docs.djangoproject.com/en/5.0/ref/settings/#installed-apps>`__ for more
details.

In Lino you usually override the :meth:`Site.get_installed_plugins` method. See
:ref:`dg.site.get_installed_plugins`.

.. setting:: DEBUG

See :blogref:`20100716`

.. setting:: SERIALIZATION_MODULES

See `Django docs
<https://docs.djangoproject.com/en/5.0/ref/settings/#serialization-modules>`__.



.. setting:: USE_TZ
.. setting:: TIME_ZONE

    See :ref:`book.specs.dumps`
