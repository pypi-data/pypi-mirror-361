.. doctest docs/specs/shopping.rst
.. include:: /../docs/shared/include/defs.rst
.. _dg.plugins.shopping:

============================================
The ``lino_xl.lib.shopping`` plugin
============================================

Adds :term:`database models <database model>` for the :term:`shopping cart`,
:term:`delivery methods <delivery method>` and the :term:`shopping addresses
<shopping address>` of a user.

This document assumes you have read :ref:`ug.plugins.shopping`.

.. module:: lino_xl.lib.shopping


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.min9.settings')
>>> from django.utils import translation
>>> from lino.api.doctest import *
>>> from django.db.models import Q

Demo data
=========

The plugin does not yet add much demo data.

>>> rt.show('shopping.Addresses')
No data to display

>>> rt.show('shopping.DeliveryMethods')
==== ================ ================== ================== ================
 ID   Designation      Designation (de)   Designation (fr)   Product
---- ---------------- ------------------ ------------------ ----------------
 1    Parcel center    Parcel center      Parcel center      Parcel center
 2    Home using UPS   Home using UPS     Home using UPS     Home using UPS
 3    Take away        Take away          Take away          Take away
==== ================ ================== ================== ================
<BLANKLINE>


Reference
=========

.. class:: DeliveryMethod

  Django model used to represent a :term:`delivery method`.

  .. attribute:: product

    The product to invoice when using this :term:`delivery method`.

.. class:: Cart

  Django model used to represent a :term:`shopping cart`.

  Inherits from :class:`lino.modlib.users.UserPlan`.

  .. attribute:: user

    The :term:`end user` who created this cart.

  .. attribute:: date

    The date of last modification.

  .. attribute:: delivery_address

    The delivery address. A pointer to a :term:`shopping address` of this user.

  .. attribute:: invoicing_address

    The invoicing address. A pointer to a :term:`shopping address` of this user.

  .. attribute:: delivery_method

  .. attribute:: invoice

    The invoice that has been created from this shopping cart.  This field is
    empty as long as the user didn't yet run :attr:`start_order`.


.. class:: CartItem

  Django model used to represent an item of a :term:`shopping cart`.

  .. attribute:: product
  .. attribute:: qty




.. class:: StartOrder

  Action to create an order from a shopping cart.

.. class:: Address

  Django model used to represent a :term:`shopping address`.


.. class:: DeliverMethod

  Django model used to represent a :term:`delivery method`.
