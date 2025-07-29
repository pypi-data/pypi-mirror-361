.. doctest docs/topics/logging.rst
.. _dg.topics.logging:

=================================
About logging
=================================

This document explains additional information about logging for developers.  We
assume that you have read :ref:`About logging in the Hoster's Guide
<host.logging>`.


.. contents::
    :depth: 1
    :local:


How Lino configures the logging system
======================================

When the :class:`Site` class gets instantiated, it calls the
:meth:`Site.setup_logging` method, which modifies the :data:`DEFAULT_LOGGING
<django.utils.log.DEFAULT_LOGGING>` setting.

This happens *before* any plugins are loaded because all this must happen
*before* Django passes the setting to the `logging.config.dictConfig
<https://docs.python.org/3/library/logging.config.html#logging.config.dictConfig>`__
function.

This approach is designed to work with the :setting:`LOGGING` and
:setting:`LOGGING_CONFIG` settings unmodified.


>>> from pprint import pprint
>>> from django.utils.log import DEFAULT_LOGGING
>>> pprint(DEFAULT_LOGGING)
{'disable_existing_loggers': False,
 'filters': {'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
             'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue'}},
 'formatters': {'django.server': {'()': 'django.utils.log.ServerFormatter',
                                  'format': '[{server_time}] {message}',
                                  'style': '{'}},
 'handlers': {'console': {'class': 'logging.StreamHandler',
                          'filters': ['require_debug_true'],
                          'level': 'INFO'},
              'django.server': {'class': 'logging.StreamHandler',
                                'formatter': 'django.server',
                                'level': 'INFO'},
              'mail_admins': {'class': 'django.utils.log.AdminEmailHandler',
                              'filters': ['require_debug_false'],
                              'level': 'ERROR'}},
 'loggers': {'django': {'handlers': ['console', 'mail_admins'],
                        'level': 'INFO'},
             'django.server': {'handlers': ['django.server'],
                               'level': 'INFO',
                               'propagate': False}},
 'version': 1}


>>> from lino_book.projects.noi1e.startup import *

>>> pprint(DEFAULT_LOGGING)
{'disable_existing_loggers': False,
 'filters': {'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
             'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue'}},
 'formatters': {'django.server': {'()': 'django.utils.log.ServerFormatter',
                                  'format': '[{server_time}] {message}',
                                  'style': '{'}},
 'handlers': {'console': {'class': 'logging.StreamHandler',
                          'level': 'INFO',
                          'stream': <doctest._SpoofOut object at ...>},
              'django.server': {'class': 'logging.StreamHandler',
                                'formatter': 'django.server',
                                'level': 'INFO'},
              'mail_admins': {'class': 'django.utils.log.AdminEmailHandler',
                              'filters': ['require_debug_false'],
                              'level': 'ERROR'}},
 'loggers': {'django': {'handlers': ['console', 'mail_admins'],
                        'level': 'INFO'},
             'django.server': {'handlers': ['django.server'],
                               'level': 'INFO',
                               'propagate': False},
             'lino': {'handlers': ['console', 'mail_admins'], 'level': 'INFO'},
             'lino_noi': {'handlers': ['console', 'mail_admins'],
                          'level': 'INFO'},
             'lino_xl': {'handlers': ['console', 'mail_admins'],
                         'level': 'INFO'}},
 'version': 1}


The :meth:`Site.setup_logging` method does does the following modifications:

- Define a *default logger configuration* that is initially the same as
  the one used by Django::

    {
        'handlers': ['console', 'mail_admins'],
        'level': 'INFO',
    }

- If the :attr:`site_dir` has a subdirectory named ``log``,
  and if :attr:`logger_filename` is not empty, add a handler
  named ``file`` and a formatter named ``verbose``, and add
  that handler to the default logger configuration.

- Add this default logger configuration for every logger named
  in :attr:`auto_configure_logger_names`.

It does nothing at all if :attr:`Site.auto_configure_logger_names` is set to
`None` or empty.



Logging to a file
=================

When you create a :xfile:`log` directory in your :term:`project directory`, Lino
will additionally log to a file :xfile:`lino.log` in that directory.

The :xfile:`log` directory may be a symbolic link to a directory
below :file:`/var/log/`.

.. xfile:: log

  A subdirectory of a Lino site's project directory that contains the
  :xfile:`lino.log` file.

.. xfile:: lino.log

  The name of Lino's logger file.

  Default value is :xfile:`lino.log`. You can change this name by setting the
  :attr:`logger_filename <lino.core.site.Site.logger_filename>` attribute of
  your :class:`Site <lino.core.site.Site>` class.

  Until 20160729 it was :xfile:`system.log`.

When a Lino process starts up, it checks whether there is a subdirectory named
:xfile:`log` in the :term:`local site directory`.  If such a directory exists,
Lino automatically activates file logging to a file named :xfile:`lino.log` in
that directory.

On a :term:`production site` you can have multiple processes running on a same
site at the same time, which can lead to conflicts when these processes write to
a same :xfile:`lino.log` file.  That's why you will prefer logging to the
:mod:`systemd` journal on a production site.


.. _dev.logging:

About logging in a development environment
==========================================

On my development machine I have a `runserver` script that does::

    set LINO_LOGLEVEL=DEBUG
    python manage.py runserver


Using the Lino logger
=====================

>>> from lino import logger
>>> logger.handlers
[<StreamHandler (INFO)>, <AdminEmailHandler (ERROR)>]
>>> logger.info("Hello, world!")
Hello, world!
>>> logger.debug("Foolish humans trying to understand me")


.. _history_aware_logging:

The "Started" and "Done" messages
==================================

Lino can log a message message:`Started %s (using %s) --> PID %s` at process
startup and a message :message:`Done PID %s` at termination.

These messages are interesting for the :term:`system administrator` of a
:term:`production site`, but they rather disturbing for development and testing.

That's why Lino emits them only when there is a logging handler named
``"file"``. Which is the case when a logger directory (:xfile:`log`) exists in
the project directory, or on a production site (when
:func:`lino.core.utils.is_devserver` returns `False`) and :mod:`systemd` is
installed.


Testing the ``log`` directory
=============================

When there is a :xfile:`log` directory, Lino will log to a :xfile:`lino.log`
file, and it logs two additional messages "Started" and "Done", which are useful
on a :term:`production site` to keep track of every admin command that has been
run on a site.

We are going to play in the `min1` demo project:

>>> from atelier.sheller import Sheller
>>> shell = Sheller('lino_book/projects/min1')

.. cleanup from previous runs:
  >>> shell("rm -rf log")
  <BLANKLINE>

The demo sites have no :xfile:`log` directory and hence no :xfile:`lino.log`
file.

>>> shell("ls log")
ls: cannot access 'log': No such file or directory

>>> shell("python manage.py prep --noinput")
... #doctest: +ELLIPSIS +REPORT_UDIFF +NORMALIZE_WHITESPACE
`initdb std demo demo2` started on database .../min1/default.db.
...
Installed ... object(s) from ... fixture(s)

Now we temporarily enable file logging in the min1 demo site by creating a
:xfile:`log` directory. And then we run the same command again to verify that
now we have the additional "Started" and "Done" messages logged:

>>> shell("mkdir log")
<BLANKLINE>

>>> shell("python manage.py prep --noinput")
... #doctest: +ELLIPSIS +REPORT_UDIFF +NORMALIZE_WHITESPACE
Started manage.py prep --noinput (using lino_book.projects.min1.settings) --> PID ...
`initdb std demo demo2` started on database .../min1/default.db.
...
Installed ... object(s) from ... fixture(s)
Done manage.py prep --noinput (PID ...)

Lino has created a :xfile:`lino.log` file and this file contains our messages:

>>> shell("ls log")
lino.log

>>> shell("cat log/lino.log")
... #doctest: +ELLIPSIS +REPORT_UDIFF +NORMALIZE_WHITESPACE
2... INFO [lino ...] : Started manage.py prep --noinput (using lino_book.projects.min1.settings) --> PID ...
2... INFO [lino ...] : `initdb std demo demo2` started on database .../min1/default.db.
2...
2... INFO [lino ...] : Done manage.py prep --noinput (PID ...)


.. Tidy up and remove all traces:
  >>> shell("rm log/lino.log")
  <BLANKLINE>
  >>> shell("rmdir log")
  <BLANKLINE>



Relation between *logging level* and *verbosity*
================================================

The relation between *logging level* and *verbosity* is not yet clear.

You can set :envvar:`LINO_LOGLEVEL` to ``"WARNING"`` in order to get rid of
quite some messages:

>>> import os
>>> env = dict()
>>> env.update(os.environ)
>>> env.update(LINO_LOGLEVEL="WARNING")
>>> shell("python manage.py prep --noinput", env=env)
... #doctest: +ELLIPSIS +REPORT_UDIFF +NORMALIZE_WHITESPACE
No changes detected
Operations to perform:
  Synchronize unmigrated apps: about, bootstrap3, contacts, countries, extjs, jinja, lino, office, printing, staticfiles, system, users, xl
  Apply all migrations: sessions
Synchronizing apps without migrations:
  Creating tables...
    Creating table system_siteconfig
    Creating table users_user
    Creating table users_authority
    Creating table countries_country
    Creating table countries_place
    Creating table contacts_partner
    Creating table contacts_person
    Creating table contacts_companytype
    Creating table contacts_company
    Creating table contacts_roletype
    Creating table contacts_role
    Running deferred SQL...
Running migrations:
  Applying sessions.0001_initial... OK
Installed ... object(s) from ... fixture(s)

Setting :envvar:`LINO_LOGLEVEL` to ``"WARNING"`` does not remove messages issued
by Django because Django does not use the logging system to print these
messages. To get rid of these messages as well, you can set verbosity to 0:

>>> shell("python manage.py prep --noinput -v0", env=env)
... #doctest: +ELLIPSIS +REPORT_UDIFF +NORMALIZE_WHITESPACE



Site attributes related to logging
==================================

.. class:: lino.core.site.Site
  :noindex:

  .. attribute:: default_loglevel

    The default logging level for all loggers configured by Lino.

    Default value is ``"INFO"``.

    See also :ref:`host.logging`.

  .. attribute:: log_each_action_request

    Whether Lino should log every incoming request for non :attr:`readonly
    <lino.core.actions.Action.readonly>` actions.

    This is experimental. Theoretically it is useless to ask Lino for logging
    every request since the web server does this. OTOH Lino can produce more
    readable logs.

    There is no warranty that actually *each* request is being logged.  It
    currently works only for requests that are being processed by the kernel's
    :meth:`run_action <lino.core.kernel.Kernel.run_action>` methods.

  .. attribute:: logger_filename

    The name of Lino's main log file, created in :meth:`setup_logging`.

    Default value is :xfile:`lino.log`.

  .. attribute:: logger_format

    The format template to use for logging to the :xfile:`lino.log` file.

  .. attribute:: auto_configure_logger_names

    A string with a space-separated list of logger names to be
    automatically configured. See :meth:`setup_logging`.

     = 'atelier lino'

  .. method:: setup_logging(self)

    See `How Lino configures the logging system`_
