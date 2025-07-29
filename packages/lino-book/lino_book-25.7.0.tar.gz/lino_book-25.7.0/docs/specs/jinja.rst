.. doctest docs/specs/jinja.rst
.. _specs.jinja:

===========================
``jinja`` : Jinja printing
===========================

.. currentmodule:: lino.modlib.jinja

This document describes the :mod:`lino.modlib.jinja` plugin

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.min1.settings')
>>> from lino.api.doctest import *


Build methods
===============

This module adds a build method for  :mod:`lino.modlib.printing`.

.. class:: JinjaBuildMethod

  Inherits from :class:`lino.modlib.printing.DjangoBuildMethod`.

Model mixins
============

.. class:: XMLMaker

  Usage example in :doc:`/topics/xml`

  .. attribute:: xml_file_name

      The name of the XML file to generate. This file will be overwritten
      without asking. The name formatted with one name ``self`` in the context.

  .. attribute:: xml_file_template

    The name of a Jinja template to render for generating the XML content.

    This must be either `None` or a :class:`Path` object.

  .. attribute:: xml_validator_file

    The name of a "validator" to use for validating the XML content.

    This must be either `None` or a :class:`Path` object.

    Lino choose the validation method from the file's suffix. It currently can
    handle suffixes ".xsd" and ".sch".

  .. method:: get_xml_file()

    Get the name of the XML file to be generated for this database row.

    Returns an instance of :class:`lino.utils.media.MediaFile`.

  .. method:: make_xml_file(ar)

    Make the XML file for this database row.


django-admin commands
=====================

This plugin defines two :cmd:`django-admin` commands.

.. management_command:: showsettings

Print to ``stdout`` all the Django settings that are active on this :term:`Lino
site`.

Usage example:

>>> from atelier.sheller import Sheller
>>> shell = Sheller("lino_book/projects/min1")
>>> shell("python manage.py showsettings | grep EMAIL")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
DEFAULT_FROM_EMAIL = webmaster@localhost
EMAIL_BACKEND = django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST = mail.example.com
EMAIL_HOST_PASSWORD =
EMAIL_HOST_USER =
EMAIL_PORT = 25
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_SUBJECT_PREFIX = [min1]
EMAIL_TIMEOUT = None
EMAIL_USE_LOCALTIME = False
EMAIL_USE_SSL = False
EMAIL_USE_TLS = False
SERVER_EMAIL = root@localhost


.. management_command:: status

Write a diagnostic status report about this :term:`Lino site`.

A functional replacement for the :manage:`diag` command.

>>> shell = Sheller("lino_book/projects/min1")
>>> shell("python manage.py status")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
Plugins
=======
<BLANKLINE>
- lino : lino
- about : lino.modlib.about
- jinja : lino.modlib.jinja(needed by lino.modlib.bootstrap3)
- bootstrap3 : lino.modlib.bootstrap3(needed by lino.modlib.extjs, needs ['lino.modlib.jinja'])
- extjs : lino.modlib.extjs(needs ['lino.modlib.bootstrap3'])
- printing : lino.modlib.printing(needed by lino.modlib.system)
- system : lino.modlib.system(needs ['lino.modlib.printing'])
- users : lino.modlib.users(needs ['lino.modlib.system'])
- office : lino.modlib.office(needed by lino_xl.lib.countries)
- xl : lino_xl.lib.xl(needed by lino_xl.lib.countries)
- countries : lino_xl.lib.countries(needed by lino_xl.lib.contacts, needs ['lino.modlib.office', 'lino_xl.lib.xl'])
- contacts : lino_xl.lib.contacts(needs ['lino_xl.lib.countries', 'lino.modlib.system'])
- staticfiles : django.contrib.staticfiles
- sessions : django.contrib.sessions
<BLANKLINE>
Config directories
==================
<BLANKLINE>
- .../lino_xl/lib/contacts/config
- .../lino/modlib/users/config
- .../lino/modlib/printing/config
- .../lino/modlib/extjs/config
- .../lino/modlib/bootstrap3/config
- .../lino/modlib/jinja/config
- .../lino/config

The output may be
customized by overriding the :xfile:`jinja/status.jinja.rst` template.

.. xfile:: jinja/status.jinja.rst

The template file used by the :manage:`status` command.
