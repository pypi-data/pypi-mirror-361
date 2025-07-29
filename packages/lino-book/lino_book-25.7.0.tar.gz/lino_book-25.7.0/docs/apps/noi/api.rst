.. doctest docs/apps/noi/api.rst
.. _dg.specs.noi.api:

========================
The ``lino_noi`` package
========================


.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *


.. module:: lino_noi.lib.noi.settings

.. class:: Site

  .. attribute:: with_accounting

    Whether this site has **accounting** functionality installed.

    Accounting in Lino Noi means the following plugins:
    :mod:`products <lino_xl.lib.products>`,
    :mod:`trading <lino_xl.lib.trading>`,
    :mod:`periods <lino.modlib.periods>`,
    :mod:`accounting <lino_xl.lib.accounting>`,
    :mod:`storage <lino_xl.lib.storage>`,
    :mod:`invoicing <lino_xl.lib.invoicing>`,
    :mod:`vat <lino_xl.lib.vat>`.

  .. attribute:: with_cms

    Whether this site has **content management** functionality installed.

    Content management in Lino Noi means the following plugins:
    :mod:`publisher <lino.modlib.publisher>`,
    :mod:`blogs <lino_xl.lib.blogs>`,
    :mod:`albums <lino_xl.lib.albums>`,
    :mod:`sources <lino_xl.lib.sources>`,

  .. method:: get_plugin_configs

    >>> from lino_noi.lib.noi.settings import Site
    >>> SITE = Site(globals())
    >>> for s in SITE.get_plugin_configs():
    ...     print(repr(s))
    []
    ('linod', 'use_channels', True)
    ('topics', 'partner_model', 'users.User')
    ('help', 'make_help_pages', True)
    ('tickets', 'end_user_model', 'contacts.Person')
    ('working', 'ticket_model', 'tickets.Ticket')
    ('invoicing', 'order_model', 'subscriptions.Subscription')
    ('users', 'allow_online_registration', True)
    ('summaries', 'duration_max_length', 10)
    ('nicknames', 'named_model', 'tickets.Ticket')
    ('peppol', 'with_suppliers', True)


.. module:: lino_noi.lib.noi.user_types

  Defines a set of user roles and fills
  :class:`lino.modlib.users.choicelists.UserTypes`.

  Used as the :attr:`user_types_module <lino.core.site.Site.user_types_module>`
  for :ref:`noi`.


.. class:: UserTypes

  .. attribute:: anonymous

    A :term:`site user` who is not authenticated.

  .. attribute:: customer

    A :term:`site user` who uses our software and may report
    tickets, but won't work on them. Able to comment and view tickets on sites
    they are member of. Unable to see any contact data of other users or partners.

  .. attribute:: user

    Alias for :attr:`customer`.

  .. attribute:: contributor

    A :term:`site user` who works on tickets of sites they are team members of.

  .. attribute:: developer

    A :term:`site user` is a trusted user who has signed an NDA. Has access to
    client contacts. Is able to make service reports as well as manage tickets.

  .. attribute:: admin

    Can do everything.

.. class:: ProvisionStates

  .. attribute:: purchased
