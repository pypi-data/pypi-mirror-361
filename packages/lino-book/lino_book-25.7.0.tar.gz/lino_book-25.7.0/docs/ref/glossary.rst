========
Glossary
========

.. glossary::
  :sorted:

  mod_wsgi
   :ref:`lino.admin.install`

  dummy module
    See :func:`lino.core.dbutils.resolve_app`.

  testing
    The version that is currently being tested.

  DavLink
    See :doc:`/davlink/index`

  tups
     The machine that served the `saffre-rumma.net`
     domain until 2010
     when it was replaced by :term:`mops`.

  mops
     The machine that is serving the `saffre-rumma.net` domain.

  jana
     An internal virtual Debian server on our LAN used for testing.

  DSBE
     "Dienst für Sozial-Berufliche Eingliederung"
     A public service in Eupen (Belgium),
     the first real user of a Lino application
     :mod:`lino.projects.pcsw`.

  dump
    "To dump" means to write the content of a database into a text file.
    This is used to backup data and for Data Migration.

  data migration

    Data Migration is when your database needs to be converted after
    an upgrade to a newer Lino version. See :ref:`admin.upgrade`.

  CSC
    Context-sensitive ComboBox.
    See :mod:`lino.utils.choices`.

  field lookups
    See https://docs.djangoproject.com/en/5.0/topics/db/queries/#field-lookups

  GC
    Grid Configuration.
    See :blogref:`20100809`,...

  disabled fields
    Fields that the user cannot edit (read-only fields).

  initdb

    See :manage:`initdb`.

  initdb_tim

    See :mod:`lino.projects.pcsw.management.commands.initdb_tim`

  watch_tim
    A daemon process that synchronizes data from TIM to Lino.
    See :mod:`lino_welfare.modlib.pcsw.management.commands.watch_tim`


  watch_calendars
    A daemon process that synchronizes remote calendars
    into the Lino database.
    See :mod:`lino_xl.lib.cal.management.commands.watch_calendars`

  loaddata

    One of Django's standard :term:`django-admin commands <django-admin command>`.
    See `Django docs <https://docs.djangoproject.com/en/5.0/ref/django-admin/#loaddata-fixture-fixture>`__.

  makeui
    A Lino-specific :term:`django-admin command` that
    writes local files needed for the front end.
    See :doc:`/topics/qooxdoo`.

  makedocs
    A Lino-specific :term:`django-admin command` that
    writes a Sphinx documentation tree about the models
    installed on this site.
    :mod:`lino.management.commands.makedocs`

  active fields

    See :attr:`dd.Model.active_fields`.

  GFK

    Generic ForeignKey. This is a ForeignKey that can point to
    different tables.

  minimal application

    See :doc:`/specs/projects/min`
