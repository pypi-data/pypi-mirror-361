.. doctest docs/specs/warehouse.rst
.. _specs.stock:

=============================================
``warehouse`` : managing the goods you own
=============================================

.. note:: This document is not finished and the plugin is not yet implemented.

.. currentmodule:: lino_xl.lib.warehouse

The :mod:`lino_xl.lib.warehouse` plugin adds functionality for warehouse
management.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *


Overview
========

.. glossary::

  warehouse

    A building or room for storing :term:`products <product>`.

  storage slot

    An named location for storing an individual :term:`product` within a
    :term:`warehouse`.

  warehouse movement

    The fact that a given quantity of a given product has moved at a given
    moment out of or into a given warehouse.

  inventory

    A list of the goods stored in a warehouse at a given date.

  stock value

    The value of a :term:`product` in a :term:`warehouse`.

  purchase order

    A document stating that we order a number of products (each with a quantity
    and potentially a price) from a given provider.

  goods receipt

    The process of entering goods into a warehouse.

  goods receipt posting

    A document stating that a number of products (each with a quantity) entered
    a :term:`warehouse`.

  stock modification

    A document stating that a number of products (each with a quantity) has been
    lost or found.

  WMS

    Warehouse Management System

  SKU

    Stock Keeping Unit. The unique reference code you assigned to a
    :term:`product` in order to refer to it on internal documents.


This plugin provides four :term:`voucher types <voucher type>`:

- A :term:`purchase order` declares that we *expect* a :term:`goods receipt posting`
- A :term:`goods receipt posting` usually *satisfies* a :term:`purchase order`
- An :term:`inventory` declares that we have a given quantity on stock
- A :term:`stock modification` declares that some good has been lost or found (and where to book this)


Database models
===============

.. class:: Warehouse

  Django model representing a :term:`warehouse`.

  .. attribute:: designation


.. class:: Movement

  Django model representing a :term:`warehouse movement`.

  .. attribute:: designation



.. class:: PurchaseOrder

  Django model representing a :term:`purchase order`.

  Inherits from :class:`lino_xl.lib.trading.VatProductInvoice`.

.. class:: GoodsReceipt

  Django model representing a :term:`goods receipt posting`.

  Inherits from :class:`lino_xl.lib.trading.VatProductInvoice`.

  Adds a reference to the :term:`purchase order` being satisfied.

.. class:: Inventory

  Django model representing an :term:`inventory`.

  .. attribute:: value_date


Choicelists
===========

.. class:: ValueMethods

  The list of available methods for computing the value of an inventory line.


Model mixins
============
