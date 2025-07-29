.. doctest docs/specs/migrate.rst
.. _book.specs.migrate:

================================
Django migrations on a Lino site
================================

Lino applications don't deliver out-of-the-box Django migrations because the
database schema of a :term:`Lino site` may also depend on local settings. For
example the :setting:`languages` setting affects your database structure.  Or
you may locally disable a plugin.  Or some plugin options can cause the
structure to change.

Which just means that you must always run :manage:`makemigrations` before
running :manage:`migrate`.

The :xfile:`migrations` directory
=================================

.. xfile:: migrations

Django migrations are automatically enabled on a :term:`Lino site` when its
:attr:`site_dir <lino.core.site.Site.site_dir>` has a subdirectory named
:xfile:`migrations`. Lino then automatically sets the :attr:`migrations_package
<lino.core.site.Site.migrations_package>` to the corresponding Python package
name derived from the :setting:`DJANGO_SETTINGS_MODULE`.

Running :cmd:`pm prep` without Django migrations
================================================

Let's use the :mod:`lino_book.projects.migs` project to play with migrations.

>>> from pathlib import Path
>>> from atelier.sheller import Sheller
>>> from lino_book.projects import migs
>>> shell = Sheller(Path(migs.__file__).parent)
>>> # shell = Sheller("lino_book/projects/migs")

We begin with Django migrations disabled:

>>> shell("cat clean.sh")
#!/usr/bin/env bash
set -e
rm -rf migrations
rm -f default.db
echo "Removed migrations and database."

>>> shell("./clean.sh")
Removed migrations and database.

The :cmd:`pm prep` command works also when Django migrations are disabled. In
this context Django considers all Lino plugins as "unmigrated".  Only some
native Django plugins (contenttypes, sessions, staticfiles) are managed by
Django:

>>> shell("python manage.py prep --noinput")
... #doctest: +ELLIPSIS -REPORT_UDIFF +NORMALIZE_WHITESPACE
`initdb std minimal_ledger demo demo2 demo_bookings checksummaries checkdata` started on database .../default.db.
...
Operations to perform:
...
Synchronizing apps without migrations:
...
Running migrations:
...
Loading data from ...
...
Update summary data ...
...
Installed ... object(s) from ... fixture(s)


Tidy up:

>>> shell("./clean.sh")
Removed migrations and database.

Running :cmd:`pm prep` with Django migrations
=============================================

We enable Django migrations by creating an empty :xfile:`migrations` directory
(in the :attr:`lino.core.site.Site.site_dir`).

>>> shell("mkdir migrations") # same as settings.SITE.site_dir.mkdir("migrations")
<BLANKLINE>

When Django migrations are enabled, the :cmd:`pm prep` command does the same,
but in a different way.  Django now considers all Lino plugins as "migrated":

>>> shell("python manage.py prep --noinput")
... #doctest: +ELLIPSIS +REPORT_UDIFF +NORMALIZE_WHITESPACE
`initdb std minimal_ledger demo demo2 demo_bookings checksummaries checkdata` started on database .../default.db.
...
Installed ... object(s) from ... fixture(s)


>>> from lino import startup
>>> startup("lino_book.projects.migs.settings")
>>> from lino.api.doctest import *

The :term:`application developer` can see whether Django migrations are enabled
or not by looking at the
:class:`migrations_package <lino.core.site.Site.migrations_package>` site attribute.

>>> print(settings.SITE.migrations_package)
lino_book.projects.migs.migrations

When Django migrations are enabled, Lino automatically fills the
:xfile:`migrations` directory with many subdirectories (one for each installed
plugin) and sets the :setting:`MIGRATION_MODULES` setting.

>>> pprint(settings.MIGRATION_MODULES)
... #doctest: +ELLIPSIS +REPORT_UDIFF +NORMALIZE_WHITESPACE
{'about': 'lino_book.projects.migs.migrations.about',
 'accounting': 'lino_book.projects.migs.migrations.accounting',
 'appypod': 'lino_book.projects.migs.migrations.appypod',
 'bootstrap3': 'lino_book.projects.migs.migrations.bootstrap3',
 'cal': 'lino_book.projects.migs.migrations.cal',
 'calview': 'lino_book.projects.migs.migrations.calview',
 'changes': 'lino_book.projects.migs.migrations.changes',
 'channels': 'lino_book.projects.migs.migrations.channels',
 'checkdata': 'lino_book.projects.migs.migrations.checkdata',
 'comments': 'lino_book.projects.migs.migrations.comments',
 'contacts': 'lino_book.projects.migs.migrations.contacts',
 'countries': 'lino_book.projects.migs.migrations.countries',
 'daphne': 'lino_book.projects.migs.migrations.daphne',
 'dashboard': 'lino_book.projects.migs.migrations.dashboard',
 'excerpts': 'lino_book.projects.migs.migrations.excerpts',
 'export_excel': 'lino_book.projects.migs.migrations.export_excel',
 'extjs': 'lino_book.projects.migs.migrations.extjs',
 'gfks': 'lino_book.projects.migs.migrations.gfks',
 'groups': 'lino_book.projects.migs.migrations.groups',
 'help': 'lino_book.projects.migs.migrations.help',
 'inbox': 'lino_book.projects.migs.migrations.inbox',
 'invoicing': 'lino_book.projects.migs.migrations.invoicing',
 'jinja': 'lino_book.projects.migs.migrations.jinja',
 'lino': 'lino_book.projects.migs.migrations.lino',
 'linod': 'lino_book.projects.migs.migrations.linod',
 'lists': 'lino_book.projects.migs.migrations.lists',
 'memo': 'lino_book.projects.migs.migrations.memo',
 'nicknames': 'lino_book.projects.migs.migrations.nicknames',
 'noi': 'lino_book.projects.migs.migrations.noi',
 'notify': 'lino_book.projects.migs.migrations.notify',
 'office': 'lino_book.projects.migs.migrations.office',
 'peppol': 'lino_book.projects.migs.migrations.peppol',
 'periods': 'lino_book.projects.migs.migrations.periods',
 'printing': 'lino_book.projects.migs.migrations.printing',
 'products': 'lino_book.projects.migs.migrations.products',
 'rest_framework': 'lino_book.projects.migs.migrations.rest_framework',
 'restful': 'lino_book.projects.migs.migrations.restful',
 'sepa': 'lino_book.projects.migs.migrations.sepa',
 'smtpd': 'lino_book.projects.migs.migrations.smtpd',
 'storage': 'lino_book.projects.migs.migrations.storage',
 'subscriptions': 'lino_book.projects.migs.migrations.subscriptions',
 'summaries': 'lino_book.projects.migs.migrations.summaries',
 'system': 'lino_book.projects.migs.migrations.system',
 'tickets': 'lino_book.projects.migs.migrations.tickets',
 'tinymce': 'lino_book.projects.migs.migrations.tinymce',
 'topics': 'lino_book.projects.migs.migrations.topics',
 'trading': 'lino_book.projects.migs.migrations.trading',
 'uploads': 'lino_book.projects.migs.migrations.uploads',
 'users': 'lino_book.projects.migs.migrations.users',
 'userstats': 'lino_book.projects.migs.migrations.userstats',
 'vat': 'lino_book.projects.migs.migrations.vat',
 'weasyprint': 'lino_book.projects.migs.migrations.weasyprint',
 'working': 'lino_book.projects.migs.migrations.working',
 'xl': 'lino_book.projects.migs.migrations.xl'}


TODO: write tests to show a :term:`site upgrade` using Django migrations.

.. tidy up before leaving:

  >>> shell("./clean.sh")
  Removed migrations and database.
