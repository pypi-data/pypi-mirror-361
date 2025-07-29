.. doctest docs/plugins/storage.rst
.. _dg.plugins.storage:

=============================================
``storage`` : Storage, provisions and fillers
=============================================

.. currentmodule:: lino_xl.lib.storage

The :mod:`lino_xl.lib.storage` plugin adds functionality for managing
storage provisions and fillers.

For an end-user introduction read :ref:`ug.plugins.storage`.


Table of contents:

.. contents::
   :depth: 1
   :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *

Dependencies
============

>>> dd.plugins.storage
<lino_xl.lib.storage.Plugin lino_xl.lib.storage(needs ['lino_xl.lib.products', 'lino.modlib.summaries'])>


Models
======

.. class:: Movement

  .. attribute:: product
  .. attribute:: qty
  .. attribute:: amount
  .. attribute:: debit
  .. attribute:: credit

.. class:: Component

  .. attribute:: parent
  .. attribute:: child
  .. attribute:: qty


.. class:: Filler

  .. attribute:: partner
  .. attribute:: provision_product
  .. attribute:: provision_state

  .. attribute:: min_asset

    The minimum quantity to have in provision. When the partner has less than
    this quantity, the filler gets triggered, i.e. generates a wanted invoice
    item.

  .. attribute:: fill_asset

    The target quantity to have in provision when this filler has triggered.
