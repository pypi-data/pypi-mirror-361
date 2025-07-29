.. doctest docs/specs/b2c.rst
.. _xl.specs.b2c:

============================
``b2c``: BankToCustomer SEPA
============================

.. currentmodule:: lino_xl.lib.b2c

This document describes the functionality implemented by the
:mod:`lino_xl.lib.b2c` module.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.min9.settings')
>>> from lino.api.doctest import *

See the specs of :ref:`welfare` for examples.

Dependencies
============

The plugin is inactive as long as :attr:`import_statements_path
<Plugin.import_statements_path>` is not set.

As a :term:`site manager` you can set this e.g. by specifying in your
:xfile:`settings.py`::

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        ...
        yield ('b2c', 'import_statements_path', '/var/sepa_incoming')

Lino does not connect directly with the bank, but assumes that SEPA
statement files are being downloaded to that directory.

and then to invoke the
:class:`lino_xl.lib.b2c.models.ImportStatements` action.



User interface
==============

>>> ses = rt.login('robin')

>>> ses.show_menu_path(system.SiteConfig.import_b2c)
Accounting --> Import SEPA


Database models
===============

.. class:: Account

    Django model used to represent an imported bank account.

.. class:: Statement

    Django model used to represent aa statement of an imported bank account.

.. class:: Transaction


    Django model used to represent a transaction of an imported bank account.



Views reference
===============

.. class:: Accounts
.. class:: Statements
.. class:: StatementsByAccount
.. class:: TransactionsByStatement

.. class:: ImportStatements
