.. doctest docs/plugins/nicknames.rst
.. _dg.plugins.nicknames:

==============================
``nicknames``: Nicknames
==============================

.. currentmodule:: lino_xl.lib.nicknames

The :mod:`lino_xl.lib.nicknames` plugin adds functionality for managing
:term:`nicknames <nickname>`.


Table of contents:

.. contents::
   :depth: 1
   :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *

>>> ses = rt.login("robin")
>>> translation.activate('en')


Usage
=====

When adding this plugin to your application, you must specify the
:setting:`nicknames.named_model`.

Plugin configuration
====================

.. setting:: nicknames.named_model

    The model that gets a nickname field.

    The :term:`application developer` defines this as a string referring to the
    model that should receive the :attr:`my_nickname` field. During startup.
    Lino resolves this into the actual model class.



Namings
=======


.. class:: Naming

  Django model used to represent a :term:`nicknaming`.

  That is, for storing the nickname used by a given user for a given database
  row.

  Inherits from UserAuthored

  .. attribute:: named

      The nameable object being named.

  .. attribute:: user

      The user who is using this niackname.

  .. attribute:: nickname

      The nickname given



Welcome messages
================

This plugin adds a :term:`welcome message` "Your nicknamed Tickets are X, Y,
..." that mentions all Tickets for which the requesting user has given a
:term:`nickname`. (Replace "Tickets" with the :attr:`verbose_name_plural` of
your :setting:`nicknames.named_model`).

Nameables
=========

.. class:: Nameable

  This model mixin adds the editable virtual field :attr:`my_nickname`

  .. attribute:: my_nickname

    The nickname given to this database row by the current user.

    Setting this to blank will remove the :term:`nicknaming`.
