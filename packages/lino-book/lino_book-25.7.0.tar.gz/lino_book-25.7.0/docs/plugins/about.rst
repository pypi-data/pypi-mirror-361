.. doctest docs/plugins/about.rst
.. _dg.plugins.about:

====================================
``about`` : Information about a site
====================================

.. currentmodule:: lino.modlib.about

The :mod:`lino.modlib.about` plugin is always installed.  It defines some
virtual tables and choicelists, but no database models.


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *

Which means that code snippets in this document are tested using the
:mod:`lino_book.projects.noi1e` demo project.

Information about the site
==========================

.. class:: About

    A dialog window which displays some information about the site.

    Versions of used third-party libraries.

    Time stamps of source code.

    Complexity factors: Some numbers that express the complexity of this site.
    These numbers may be used by a :term:`hosting provider` for computing the
    price of their services.


Time zones
==========

Every Lino site can define its own list of time zones.

>>> rt.show('about.TimeZones')
======= ========= =================
 value   name      text
------- --------- -----------------
 01      default   UTC
 02                Europe/Tallinn
 03                Europe/Brussels
 04                Africa/Tunis
======= ========= =================
<BLANKLINE>


This list is usually populated in the local :attr:`workflows_module
<lino.core.site.Site.workflows_module>` of a project.  For example::

    # don't forget to import the default workflows:
    from lino_noi.lib.noi.workflows import *

    from lino.modlib.about import TimeZones
    TimeZones.clear()
    add = TimeZones.add_item
    add('01', settings.TIME_ZONE or 'UTC', 'default')
    add('02', "Europe/Tallinn")
    add('03', "Europe/Brussels")
    add('04', "Africa/Tunis")


.. class:: TimeZones

    The list of time zones available on this site.

    This :term:`choicelist` always contains at least one choice named
    :attr:`default`.

    You can redefine this choicelist in your local
    :attr:`workflows_module <lino.core.site.Site.workflows_module>`.

    .. attribute:: default

        The default time zone on this server, corresponding to
        :setting:`TIME_ZONE`.  Unlike :setting:`TIME_ZONE` (which is a string),
        :attr:`default` is a :class:`Choice` object whose :attr:`text` is the
        same as the string and which has an attribute :attr:`tzinfo`, which
        contains the time zone info object.


Date formats
============

.. class:: DateFormats

  A list of date formats.

  This is currently used only by the :mod:`lino_xl.lib.google` plugin. Date
  formatting is configured site-wide in
  :attr:`lino.core.site.Site.date_format_strftime` & Co.

>>> rt.show('about.DateFormats')
======= ========= ==========
 value   name      text
------- --------- ----------
 010     default   dd.mm.y
 020               dd.mm.yy
 030               dd/mm/y
 040               dd/mm/yy
======= ========= ==========
<BLANKLINE>
