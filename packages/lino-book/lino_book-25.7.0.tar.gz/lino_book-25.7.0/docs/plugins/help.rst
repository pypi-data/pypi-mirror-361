.. doctest docs/plugins/help.rst
.. include:: /../docs/shared/include/defs.rst
.. _dg.plugins.help:

================================
``help`` : Make local help pages
================================

.. currentmodule:: lino.modlib.help

The :mod:`lino.modlib.help` plugin adds functionality for loading
:term:`extracted help texts <extracted help text>` at startup and optionally
adding a :guilabel:`Help` button to all :term:`data tables <data table>`. See
:doc:`/dev/help_texts` for a topic overview.

It defines some startup hooks and the :term:`django-admin command`
:manage:`makehelp`.

It also defines a database model for storing
:term:`site contacts <site contact>`.


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.cms1.settings')
>>> from django.utils import translation
>>> from lino.api.doctest import *
>>> from django.db.models import Q
>>> from atelier.sheller import Sheller
>>> shell = Sheller()

The help button
===============

The help button (:guilabel:`?`) is a button that opens a browser window on the
:term:`local help pages`.

As a :term:`server administrator` you can activate the :guilabel:`Help` button by
setting :setting:`help.make_help_pages` to `True`.

Having a :guilabel:`Help` button requires the site to generate :term:`local help
pages`. So when this is `True`, you should not forget to call :manage:`makehelp`
to generate the help pages.

Site contacts
=============

When :setting:`help.use_contacts` is set to `True`,
the :term:`server administrator`
can edit a table of :term:`site contacts <site contact>`.

>>> rt.show(help.SiteContacts)
====================== =============== ==================== ======================================== ======================================== ========================================
 Site contact type      Organization    Represented by       Remark                                   Remark (de)                              Remark (fr)
---------------------- --------------- -------------------- ---------------------------------------- ---------------------------------------- ----------------------------------------
 Site owner             Rumma & Ko OÜ   Mrs Erna Ärgerlich
 Server administrator   Van Achter NV
 Hotline                                Mrs Annette Arens    <p>Mon and Fri from 11:30 to 12:00</p>   <p>Mon and Fri from 11:30 to 12:00</p>   <p>Mon and Fri from 11:30 to 12:00</p>
====================== =============== ==================== ======================================== ======================================== ========================================
<BLANKLINE>




The :guilabel:`Site contact type` field of a site contact points to the
:class:`SiteContactTypes` choicelist, which can be modified by the
:term:`server administrator`.

>>> rt.show(help.SiteContactTypes)
======= ============= ======================
 value   name          text
------- ------------- ----------------------
 100     owner         Site owner
 200     serveradmin   Server administrator
 300     siteadmin     Site administrator
 400     hotline       Hotline
======= ============= ======================
<BLANKLINE>


Configuration options
=====================

This plugin defines the following :term:`plugin settings <plugin setting>`:

.. setting:: help.make_help_pages

  Whether to add a help button in every toolbar. See `The help button`_.

.. setting:: help.use_contacts

  Whether this :term:`Lino site` has a table of
  :term:`site contacts <site contact>`.

  See `Site contacts`_ below.


The ``makehelp`` command
========================

This plugin adds the following :term:`django-admin command`.

.. management_command:: makehelp

  Generate the :term:`local help pages` for this :term:`Lino site`.

>>> shell("django-admin makehelp --help")
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF +ELLIPSIS
usage: django-admin makehelp [-h] [-t TMPDIR] [-l LANGUAGE] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
                             [--skip-checks]
<BLANKLINE>
Generate the local help pages for this Lino site.
<BLANKLINE>
options:
  -h, --help            show this help message and exit
  -t TMPDIR, --tmpdir TMPDIR
                        Path for temporary files.
  -l LANGUAGE, --language LANGUAGE
                        Generate only the specified language.
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the DJANGO_SETTINGS_MODULE environment variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
  --traceback           Display a full stack trace on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.
