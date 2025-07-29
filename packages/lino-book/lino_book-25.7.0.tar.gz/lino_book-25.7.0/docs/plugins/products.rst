.. doctest docs/specs/products.rst
.. _specs.products:

===================================================
``products`` : defining the things you sell and buy
===================================================

.. currentmodule:: lino_xl.lib.products

The :mod:`lino_xl.lib.products` plugin adds functionality for managing
"products".

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *


Overview
========

.. glossary::

  product

    Something you can trade (e.g. sell, buy, rent) in an item of a :term:`trade
    voucher`. Mostly a name and a price. It can be material (a good) or
    immaterial (a service).  Database model: :class:`Product`.

    Products can be grouped into :term:`categories <product category>`, and every
    product must be of a given :term:`product type`.

  product category

    A group of products that fit together.

    See `Product categories`_.

  product type

    A name for the nature or type of a set of products.

    Used for example to differentiate between "Services" and "Goods".

    The detail layout of a product can vary depending on its type, but not
    depending on its category.

    Every application has its specific list of product types.
    This list can be locally modified by the :term:`server administrator`.

    Rule of thumb: product **categories** can get edited by end users while
    product **types** are hard-coded by the application developer.

  price factor

    A property of a partner that may influence the price of certain products.

    The list of price factors is meant to be defined by the :term:`application
    developer`. Changing it locally would also require changes in the some
    layouts.  Changes to this list may require a database migration because
    every price factor causes a field to be injected to the
    :class:`lino_xl.lib.contacts.Partner` model.

  price rules

    A set of rules that specify which product to use for a given :term:`price
    selector` and a given set of price factors.

  price selector

    A database object used to specify "what is being sold" in price rules.

    In :ref:`voga` and :ref:`presto` we use  the :term:`calendar entry type` as
    price selector, in :ref:`noi` the :class:`lino_xl.lib.working.SessionType`.


Dependencies
============

The :mod:`lino_xl.lib.trading` plugins injects a :attr:`sales_price` field to
the product model.



Products
========


.. class:: Product

    Django model to represent a :term:`product`.

    .. attribute:: name

        A one-line designation for this product.

    .. attribute:: body

        The long description of this product.

        This is a BabelField, so there will be one field for every language
        defined in :attr:`lino.core.site.Site.languages`.

    .. attribute:: product_type

        The type of this product.

        This field may not be blank and must be an item of :class:`ProductTypes`.

        The default value is set by the actor used for creating the product.
        Some product actors don't have a default product type, in that case the
        default value is :attr:`ProductTypes.default`.

    .. attribute:: category

        The category of this product.

        This is a pointer to :class:`Category`. The selection list is limited to
        those categories having the same :attr:`product_type`.

    .. attribute:: delivery_unit

        Pointer to :class:`DeliveryUnits`

    .. attribute:: vat_class

        The VAT class.  Injected by :mod:`lino_xl.lib.vat`. If that plugin is
        not installed, :attr:`vat_class` is a dummy field.

    .. attribute:: body_short_preview

      See :attr:`lino.modlib.memo.Previewable.body_short_preview`.

    .. attribute:: body_full_preview

      See :attr:`lino.modlib.memo.Previewable.body_full_preview`.

    .. attribute:: barcode_svg

      A htmlbox showing the barcode of this product.

    .. method:: get_ruled_price(self, partner, selector)

        Return the product to use for this partner and this selector according
        to the :term:`price rules`.


.. class:: Products

  Base class for all tables of products.


>>> rt.show(products.Products)  #doctest: +REPORT_UDIFF
==== ================================================================ ================================================================ ================================================================ ================= ===============
 ID   Bezeichnung                                                      Bezeichnung (fr)                                                 Bezeichnung (en)                                                 Kategorie         Verkaufspreis
---- ---------------------------------------------------------------- ---------------------------------------------------------------- ---------------------------------------------------------------- ----------------- ---------------
 9    Bildbearbeitung und Unterhalt Website                            Traitement d'images et maintenance site existant                 Image processing and website content maintenance                 Website-Hosting   25,00
 10   Book                                                             Book                                                             Book                                                             Sonstige          29,90
 6    EDV Konsultierung & Unterhaltsarbeiten                           ICT Consultation & maintenance                                   IT consultation & maintenance                                    Website-Hosting   30,00
 8    Programmierung                                                   Programmation                                                    Programming                                                      Website-Hosting   40,00
 7    Server software installation, configuration and administration   Server software installation, configuration and administration   Server software installation, configuration and administration   Website-Hosting   35,00
 11   Stamp                                                            Stamp                                                            Stamp                                                            Sonstige          1,40
 2    Stuhl aus Holz                                                   Chaise en bois                                                   Wooden chair                                                     Möbel             99,99
 4    Stuhl aus Metall                                                 Chaise en métal                                                  Metal chair                                                      Möbel             79,99
 1    Tisch aus Holz                                                   Table en bois                                                    Wooden table                                                     Möbel             199,99
 3    Tisch aus Metall                                                 Table en métal                                                   Metal table                                                      Möbel             129,99
 5    Website-Hosting 1MB/Monat                                        Hébergement 1MB/mois                                             Website hosting 1MB/month                                        Website-Hosting   3,99
 12   Zwischensumme                                                    Total                                                            Subtotal
                                                                                                                                                                                                                           **675,25**
==== ================================================================ ================================================================ ================================================================ ================= ===============
<BLANKLINE>


Product categories
==================

The list of available :term:`product categories <product category>` of a site
can be modified by :term:`end users <end user>` with appropriate permission via
:menuselection:`Configure --> Products --> Categories` or
:menuselection:`Configure --> Sales --> Categories`.

>>> show_menu_path(products.Categories, language="en")
Configure --> Sales --> Product Categories

>>> rt.show(products.Categories, language="en")
==== ======== ================= =============================== ================== ==============
 ID   Parent   Designation       Designation (fr)                Designation (en)   Product type
---- -------- ----------------- ------------------------------- ------------------ --------------
 1             Möbel             Meubles                         Furniture          Products
 2             Website-Hosting   Hébergement de sites Internet   Website Hosting    Products
 3             Sonstige          Autre                           Other              Products
==== ======== ================= =============================== ================== ==============
<BLANKLINE>



.. class:: Category

    Django model used to represent a :term:`product category`.

    .. attribute:: product_type

        The product type to apply to products of this category.





Product types
=============

Products can be differentiated by their "type".
Types cannot be edited by the
user.  But every product type can have a layout on its own.
Every product type has its own menu entry.


.. class:: ProductType

    .. attribute:: text

        The verbose name of this product type.

        This string is used for the menu entries in :menuselection:`Configure
        --> Products`.

    .. attribute:: table_name

        The name of the table to use for displaying a list of products with this type.

.. class:: ProductTypes

    The list of *product types*.

    It should contain at least one item whose name is :attr:`default`.

    For each item of this list the plugin adds one menu entry to the
    :menuselection:`Configure` menu.

    .. attribute:: default

    The product type to be set on new products when they are created in an
    actor that doesn't have a default product type.



    >>> rt.show(products.ProductTypes)
    ====== ========= ========== ===================
     Wert   name      Text       Table name
    ------ --------- ---------- -------------------
     100    default   Produkte   products.Products
    ====== ========= ========== ===================
    <BLANKLINE>




.. class:: DeliveryUnits

    The list of possible delivery units of a product.

    >>> rt.show(products.DeliveryUnits)
    ====== ========= ===============
     Wert   name      Text
    ------ --------- ---------------
     HUR    hour      Stunden
     MON    month     Monate
     XPP    piece     Stück
     XBX    box       Dosen
     XPK    package   Packages
     MTR    m         Metres
     MTQ    m³        Cubic metres
     MTK    m²        Square metres
     LTR    l         Litres
     MLT    ml        Millilitres
     GRM    g         Grams
     MGM    mg        Milligrams
     KGM    kg        Kilograms
    ====== ========= ===============
    <BLANKLINE>

    This is an arbitrary subset of the `UNECERec20
    <https://docs.peppol.eu/poacc/billing/3.0/2024-Q2/codelist/UNECERec20/>`_
    code list. As a :term:`server administrator` you may adapt it to your local
    needs. Lino relies on the :attr:`value` beging the code to specify in
    :term:`Peppol documents <Peppol document>`.


Price rules
===========

Price rules can be used to define which products are available for a given
partner, and optionally to find a default product for a given :term:`price
selector`.

.. class:: PriceFactors

    The choicelist of :term:`price factors <price factor>`.

    This list is empty by default.  See :ref:`tera` or :ref:`presto` for
    examples of applications that use price factors.

    >>> rt.show(products.PriceFactors)
    Keine Daten anzuzeigen

.. class:: PriceRule

  .. attribute:: seqno

    The sequence number of this rule. Lino loops over price rules in this order
    and returns the first one that applies.

  .. attribute:: product

    The product to use for getting the price when this rule applies.

  .. attribute:: selector

    Either `None` or an additional selector for this price rule.

    When given, this must be an instance of :attr:`lino_xl.lib.products.Plugin.price_selector`.

  Every price rule also has one automatic field for each price factor.


.. class:: PriceRules

    The list of price rules.

    >>> rt.show(products.PriceRules)
    Keine Daten anzuzeigen


Plugin settings
===============

.. setting:: products.barcodes_driver

Which barcode driver to use on this site.

Default is `None`. Allowed values: "ean13", "ean8".


This plugin requires  the `python-barcode
<https://python-barcode.readthedocs.io>`_ Python package when
:setting:`products.barcodes_driver` is not `None`.
