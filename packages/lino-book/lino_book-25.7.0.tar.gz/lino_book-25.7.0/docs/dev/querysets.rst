.. _dev.querysets:

==========================
Customizing your querysets
==========================

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *

The :meth:`get_request_queryset` method
=======================================

Lino adds the :meth:`get_request_queryset` method for customizing the Django
queryset used by an action request.  The method exists both on the
:term:`database model` and on the :term:`data table`, and you can override either
or both, depending on your needs.

.. class:: lino.core.model.Model
  :no-index:

  .. classmethod:: get_request_queryset(cls, ar)

    Return the Django queryset to be used by action request ``ar`` for any
    :term:`data table` on this model.

.. class:: lino.core.actors.Actor
  :no-index:

  .. classmethod:: get_request_queryset(cls, ar)

    Return the Django queryset to be used by action request ``ar`` for this
    :term:`data table`.

As an application developer you may want to override this method

- if you have customized actor parameters, then this is the place to apply them
  to the queryset
- to add select_related()
- to add user-level filtering

.. This method may return a list rather than a queryset(?)

..
  The optional `filter` keyword arguments, if present, are applied as
  additional filter. This is used only in UNION tables on abstract model
  mixins where filtering cannot be done after the join.

The default implementation of the data table method calls the model's method,
which takes `cls.objects.all()` and applies the different filtering and ordering
options specified on the actor class using
:attr:`filter`,
:attr:`exclude`,
:attr:`known_values`,
:attr:`simple_parameters`,
:attr:`quick_search`,
:attr:`order_by`
:attr:`limit` and :attr:`offset`.

How to override this method::

  @classmethod
  def get_request_queryset(cls, ar):
      qs = super().get_request_queryset(ar)
      ...
      return qs

Customized examples :class:`lino.modlib.comments.Comment`,
:class:`lino_xl.lib.tickets.Site` and :class:`lino_xl.lib.tickets.Ticket`.

When the model is abstract, this method simulates a UNION and accepts keyword
arguments. This potentially unstable feature is used for
:class:`lino_xl.lib.vat.IntracomPurchases` and
:class:`lino_xl.lib.vat.IntracomSales`.
