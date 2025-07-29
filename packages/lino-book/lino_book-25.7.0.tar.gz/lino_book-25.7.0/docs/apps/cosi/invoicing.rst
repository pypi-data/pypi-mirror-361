.. doctest docs/apps/cosi/invoicing.rst
.. _cosi.specs.invoicing:

================================
How Lino Così generates invoices
================================


In :ref:`cosi` every delivered item will get invoiced.

General functionality for automatically generating invoices is documented in
:doc:`/plugins/invoicing`.




.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.cosi5.settings')
>>> from lino.api.doctest import *


Overview
========

The **invoice generator** is is sales.InvoiceItem

>>> rt.models_by_base(rt.models.invoicing.InvoiceGenerator)
[<class 'lino_xl.lib.trading.models.InvoiceItem'>]

We must explain to Lino how a delivery note turns into an invoice  by extending
the models so that they inherit from :class:`InvoiceGenerator
<lino_xl.lib.invoicing.InvoiceGenerator>`.
