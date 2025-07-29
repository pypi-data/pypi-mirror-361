.. doctest docs/specs/groups.rst
.. _specs.groups:

=========================================
``groups`` : user groups
=========================================

We assume that you have read the :term:`end-user documentation` page in
:ref:`ug.plugins.groups`.

.. currentmodule:: lino_xl.lib.groups

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *
>>> from django.db.models import Q

Usage
=====

When you install this plugin, you will probably  add a panel "Memberships"
(:class:`MembershipsByUser`) to the :term:`detail layout` of your
:class:`lino.modlib.users.UserDetail`.

This plugin doesn't create its own top-level menu but adds its menu commands to
the same menu as :mod:`lino.modlib.system`.

>>> dd.plugins.groups.menu_group
'system'

In :ref:`noi` the verbose name of "Group" is changed to "Team".

>>> print(dd.plugins.groups.verbose_name)
Teams

>>> show_menu_path(groups.Groups)
Configure --> System --> Teams


Groups
======

>>> rt.login("robin").show(groups.Groups)
==================== ========= ==================================================================
 Team                 Private   Memberships
-------------------- --------- ------------------------------------------------------------------
 `Developers <…>`__   No        `Marc <…>`__, `Rolf Rompen <…>`__, **New** **?**
 `Managers <…>`__     Yes       `Jean <…>`__, `Mathieu <…>`__, `Robin Rood <…>`__, **New** **?**
 `Sales team <…>`__   No        `Luc <…>`__, `Romain Raffault <…>`__, **New** **?**
==================== ========= ==================================================================
<BLANKLINE>



Marc does not see the private group because he's not a member.

>>> rt.login("marc").show(groups.Groups)
==================== ========= ======================================
 Team                 Private   Memberships
-------------------- --------- --------------------------------------
 `Developers <…>`__   No        `Marc <…>`__, `Rolf Rompen <…>`__
 `Sales team <…>`__   No        `Luc <…>`__, `Romain Raffault <…>`__
==================== ========= ======================================
<BLANKLINE>


Anonymous doesn't see any groups:

>>> rt.show(groups.Groups)
No data to display

.. class:: Group

    Django model representing a :term:`user group`.

    .. attribute:: ref

        The reference. An optional alphanumeric identifier that, unlike the
        primary key, is editable.

        See :attr:`lino.mixins.ref.StructuredReferrable.ref`

    .. attribute:: name

        The designation in different languages.

    .. attribute:: user

        The owner of the group

    .. attribute:: private

        Whether this group is considered private.
        See :ref:`dg.plugins.comments.visibility`.

.. class:: Groups

  Shows all groups.

.. class:: Membership

    Django model representing a :term:`user membership`.

    .. attribute:: user
    .. attribute:: group
    .. attribute:: remark
