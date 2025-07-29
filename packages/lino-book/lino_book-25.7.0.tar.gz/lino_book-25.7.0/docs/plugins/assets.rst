.. doctest docs/plugins/assets.rst
.. _dg.plugins.assets:

================================
``assets`` : Partner assets
================================

.. module:: lino_xl.lib.assets

This is the developer reference about the :mod:`lino_xl.lib.assets` plugin,
which adds functionality for managing :term:`partner assets <partner asset>`.

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi3.startup import *
>>> ses = rt.login('robin')

The `assets` plugin is being used by the `cosi3` demo project.


Partner assets
==============

The :term:`partner asset` model is used as
:data:`lino_xl.lib.invoicing.order_model` in :mod:`lino_book.projects.cosi3`.

.. class:: PartnerAsset

  Django model used to represent a :term:`partner asset`.


Configuration options
=====================

In :ref:`cosi` you can activate this plugin by setting the
:attr:`lino_cosi.lib.cosi.settings.Site.with_assets` option. In other
applications you add it to your :meth:`get_installed_plugins` method.

>>> settings.SITE.with_assets
True

In cosi3 we also customize the verbose name of the :term:`partner asset`. The
end users of this site don't think about "Partner assets" but about "License
plates".

>>> dd.plugins.assets.asset_name
'License plate'
>>> dd.plugins.assets.asset_name_plural
'License plates'

Usage
=====

When this plugin is installed, the :attr:`lino_xl.lib.trading.InvoiceItem.asset`
field is no longer a dummy field but a :ref:`learning combo <learning_combos>`.
You can specify the partner asset for every line of an invoice.

As a :term:`site manager` you can see all partner assets by selecting
:menuselection:`Explorer --> Partner assets --> License plates`.

>>> show_menu_path(assets.PartnerAssets)
Explorer --> Partner assets --> License plates

>>> rt.show(assets.PartnerAssets)
===================== =============
 Partner               Designation
--------------------- -------------
 Bestbank              ABC123
 Rumma & Ko OÜ         ABC456
 Bäckerei Ausdemwald   DEF123
 Bäckerei Mießen       DEF789
===================== =============
<BLANKLINE>
