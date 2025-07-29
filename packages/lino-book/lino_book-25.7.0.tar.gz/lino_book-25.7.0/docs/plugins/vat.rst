.. doctest docs/plugins/vat.rst
.. _xl.vat:

====================================================
``vat`` : Adding VAT (Value-added tax) functionality
====================================================

.. module:: lino_xl.lib.vat

The :mod:`lino_xl.lib.vat` plugin is used when the :term:`site operator`  has
sales and purchase operations that are subject to value-added tax (VAT).
Installing this plugin adds
a :attr:`vat_id <VatSubjectable.vat_id>` field to every :term:`business partner`.
It also adds a :term:`voucher type` for making :term:`VAT declarations <VAT
declaration>`.

See also the end-user docs about this plugin: :ref:`ug.plugins.vat`.

.. contents::
   :depth: 1
   :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi4.startup import *


National VAT modules
====================

When using this plugin, you will probably also install one of the
:term:`national VAT modules <national VAT module>`.

You activate such a :term:`national VAT module` by setting the
:setting:`vat.declaration_plugin` plugin attribute.

Currently we have three :term:`national VAT modules <national VAT module>`.
These are normal Lino plugins that implement the VAT declaration and rules for a
given country. They each have their own reference page:

- :doc:`bevat`
- :doc:`bevats`
- :doc:`eevat`


You don't need to select a national VAT module if you don't care about VAT.
In this case all your trading operations will use a VAT rate of 0%.

There is also a plugin :mod:`lino_xl.lib.vatless`, which might become
deprecated.  The modules :mod:`lino_xl.lib.vatless` and :mod:`lino_xl.lib.vat`
can theoretically both be installed though obviously this wouldn't make sense.


VAT regimes
===========

When there is no national VAT module, we have only one VAT regime:

>>> rt.show(vat.VatRegimes, language="en")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
======= ======== ======== ========== ============== ================ =============
 value   name     text     VAT area   Needs VAT id   Reverse charge   Send Peppol
------- -------- -------- ---------- -------------- ---------------- -------------
 10      normal   Normal              No             No               No
======= ======== ======== ========== ============== ================ =============
<BLANKLINE>


.. class:: VatRegime

    Base class for the items of :class:`VatRegimes`.  Each :term:`VAT regime` is
    an instance of this and has two properties:

    .. attribute:: vat_area

        In which :term:`VAT area` this regime is available.

    .. attribute:: item_vat

        No longer used. See :data:`item_vat` instead.

        .. Whether unit prices are VAT included or not.


    .. attribute:: needs_vat_id

        Whether this VAT regime requires that partner to have a :attr:`vat_id`.

    .. attribute:: reverse_charge

      Whether reverse charge applies for operations under this regime.

      Reverse charge means that the responsibility  of declaring and paying VAT
      delegated to the receiver of the invoice customer. Usually the supplier
      charges the VAT on their sales, i.e. they collect this tax from their
      customer and then remits it to their tax office. When reverse charge
      applies the supplier issues an invoice without VAT, and the buyer then
      calculates and pays any VAT due to their tax office.  The concept of
      reverse charge exists to avoid the obligation for sellers to register for
      VAT in the country of their customer.

.. class:: VatRegimes

    The global list of :term:`VAT regimes <VAT regime>`.  Each item of this list
    is an instance of :class:`VatRegime`.

    Three VAT regimes are considered standard minimum:

    .. attribute:: normal
    .. attribute:: subject
    .. attribute:: intracom

    Two additional regimes are defined in :mod:`lino_xl.lib.bevat`:

    .. attribute:: de
    .. attribute:: lu





VAT classes
===========

See also :ref:`ug.plugins.vat.classes`.

>>> rt.show(vat.VatClasses, language="en")
======= ============= ===========================
 value   name          text
------- ------------- ---------------------------
 010     goods         Goods at normal VAT rate
 020     reduced       Goods at reduced VAT rate
 030     exempt        Goods exempt from VAT
 100     services      Services
 200     investments   Investments
 210     real_estate   Real estate
 220     vehicles      Vehicles
 300     vatless       Without VAT
======= ============= ===========================
<BLANKLINE>



.. class:: VatClasses

    The global list of VAT classes.

    Default classes are:

    .. attribute:: exempt

    .. attribute:: reduced

    .. attribute:: normal


VAT rules
=========

When no :term:`national VAT module` is installed, we have only one default
:term:`VAT rule` with no condition and zero rate.

>>> rt.show(vat.VatRules, language="en")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
+-------+------------------+
| value | Description      |
+=======+==================+
| 1     | VAT rule 1:      |
|       | apply 0 %        |
|       | and book to None |
+-------+------------------+
<BLANKLINE>


.. class:: VatRule

    A rule that defines how VAT is to be handled for a given invoice item.

    Example data see :mod:`lino_xl.lib.vat.fixtures.euvatrates`.

    Database fields:

    .. attribute:: seqno

       The sequence number.

    .. attribute:: country
    .. attribute:: vat_class

    .. attribute:: vat_regime

        The regime for which this rule applies.

        Pointer to :class:`VatRegimes`.

    .. attribute:: rate

        The VAT rate to be applied. Note that a VAT rate of 20 percent is
        stored as `0.20` (not `20`).

    .. attribute:: vat_account

        The general account where VAT is to be booked.

    .. attribute:: vat_returnable

        Whether VAT is returnable. Returnable VAT does not increase the total
        amount of the voucher, it causes an additional movement into the
        :attr:`vat_returnable_account`. See `Returnable VAT`_.

    .. attribute:: vat_returnable_account

        Where to book returnable VAT. If this field is empty and
        :attr:`vat_returnable` is `True`, then VAT will be added to the base
        account. See `Returnable VAT`_.


.. class:: VatRules

    The table of all :class:`VatRule` objects.

    This table is accessible via :menuselection:`Explorer --> VAT --> VAT rules`.

    >>> show_menu_path(vat.VatRules, language='en')
    Explorer --> VAT --> VAT rules

    This table is filled by the :term:`national VAT module`.

    .. classmethod:: get_vat_rule(cls, vat_area, trade_type, vat_regime,
                     vat_class=None, country=None, date=None)

        Return the VAT rule to be applied for the given criteria.

        Lino loops through all rules (ordered by their :attr:`seqno`)
        and returns the first object that matches.

        If no rule matches, Lino raises an exception unless a keyword argument
        `default` is given.



VAT areas
=========

The :class:`VatAreas` choice list contains the list of available :term:`VAT
areas <VAT area>`.

>>> rt.show(vat.VatAreas, language="en")
======= =============== ===============
 value   name            text
------- --------------- ---------------
 10      national        National
 20      eu              EU
 30      international   International
======= =============== ===============
<BLANKLINE>


The plugin property :data:`lino_xl.lib.vat.eu_country_codes` defines which countries are
considered part of the EU.


Available VAT regimes
=====================

The declaration plugin controls which VAT regimes are available for selection
on a partner or on a voucher.

The available VAT regimes vary depending on which VAT declaration plugin is
installed.  When no declaration module is installed, we have only one default
regime.

The list of available VAT regimes for a partner depends on the :term:`VAT area`
and on whether the partner has a VAT id or not.

.. function:: get_vat_regime_choices(country=None, vat_id=None):

    Used for the choosers of the :attr:`vat_regime` field of a partner and a
    voucher.


.. class:: VatAreas

    The global list of :term:`VAT areas <VAT area>`.

    .. classmethod:: get_for_country(cls, country)

        Return the :term:`VAT area` for this country.

Why differentiate between VAT regimes and VAT classes?
======================================================

You might ask why we use two sets of categories for specifying the VAT rate.
Some other accounting programs do not have two different categories for the
subtle difference between "exempt from VAT" and "VAT 0%", they have just a
category "VAT rate" which you can set per invoice item (and a default value per
provider).

The problem with this simplified vision is that at least for Belgian VAT
declarations there is a big difference between having 0% of VAT because the
provider is a private person and having 0% of VAT because you are buying post
stamps or flight tickets (which are exempt from VAT).

Another thing to consider is that in Lino we want to be able to have partners
who are both a provider and a customer.  Their VAT regime remains the same for
both trade types (sales and purchase) while the default VAT class to use in
invoice items depends on the account or the product.

.. Consider e.g. an invoice from an airline company where you buy tickets (VAT 0%)
   and some additional service (VAT 20%). Or an invoice from some other company
   where you buy post stamps (0%), books (9%) and additional service (20%).


Account invoices
===================

The :mod:`lino_xl.lib.vat` plugin provides the :class:`VatAccountInvoice`
voucher type.  It is implemented in two database models:

.. class:: VatAccountInvoice

    Django model for storing :term:`account vouchers <account voucher>`.

    A VAT-capable of :term:`account voucher`. It is one of the most basic
    voucher types, which can be used even in accounting applications that don't
    have :mod:`lino_xl.lib.trading`.


.. class:: InvoiceItem

    Django model for representing items of an :term:`account voucher`.

There are several views:

.. class:: Invoices

    The table of all :class:`VatAccountInvoice` objects.

.. class:: InvoicesByJournal

    Shows all invoices of a given journal. Works only when the
    :attr:`voucher_type <lino_xl.lib.accounting.Journal.voucher_type>` of the
    specified :term:`master instance` is :class:`VatAccountInvoice`.

.. class:: PrintableInvoicesByJournal

    Purchase journal

.. class:: InvoiceDetail

    The detail layout used by :class:`Invoices`.

.. class:: ItemsByInvoice

.. class:: VouchersByPartner



Utilites
========

This plugin contains some utility functions.

.. function:: add_vat(base, rate)

  Add to the given base amount `base` the VAT of rate `rate`.

.. function:: remove_vat(incl, rate)

  Remove from the given amount `incl` the VAT of rate `rate`.

Code examples:

>>> from lino_xl.lib.vat.utils import add_vat, remove_vat

>>> add_vat(100, 21)
121.0

>>> remove_vat(121, 21)
100.0

>>> add_vat(10, 21)
12.1

>>> add_vat(1, 21)
1.21

>>> remove_vat(100, 20)
83.33333333333334




Showing the invoices covered by a VAT declaration
=================================================

The plugin defines two tables that show the invoices covered by a VAT
declaration, IOW the invoices that have contributed to the numbers in the
declaration.


.. class:: SalesByDeclaration

    Show a list of all sales invoices whose VAT regime is Intra-Community.

.. class:: PurchasesByDeclaration

    Show a list of all purchase invoices whose VAT regime is Intra-Community.

.. class:: VatInvoices

    Common base class for :class:`SalesByDeclaration` and
    :class:`PurchasesByDeclaration`



Intracom sales and purchases
============================

The plugin defines two reports accessible via the
:menuselection:`Reports --> Accounting` menu and integrated in the
printout of a VAT declaration:


.. class:: IntracomSales

    Show a list of all sales invoices having VAT regime is Intra-Community.

.. class:: IntracomPurchases

    Show a list of all purchase invoices having VAT regime is Intra-Community.

.. class:: IntracomInvoices

    Common base class for :class:`IntracomSales` and :class:`IntracomPurchases`.

These reports are empty when you have no :term:`national VAT module` installed:

>>> rt.show(vat.IntracomSales, language='en')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
No data to display

>>> rt.show(vat.IntracomPurchases, language='en')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
No data to display

See :doc:`/plugins/eevat` for a non-empty example.


A data table on an abstract database model
==========================================

:class:`IntracomInvoices` is an example of a :term:`data table` on an abstract
database model. In :ref:`cosi` there are two :term:`database models <database model>`
that can contain intracom invoices: :class:`VatProductInvoice
<lino_xl.lib.trading.VatProductInvoice>` and :class:`VatAccountInvoice
<lino_xl.lib.vat.VatAccountInvoice>`.

>>> vat.IntracomPurchases.model
<class 'lino_xl.lib.vat.mixins.VatVoucher'>

>>> list(rt.models_by_base(vat.IntracomPurchases.model))
[<class 'lino_xl.lib.trading.models.VatProductInvoice'>, <class 'lino_xl.lib.vat.models.VatAccountInvoice'>]


Model mixins
============

.. class:: VatSubjectable

    Model mixin that defines the database fields :attr:`vat_regime` and
    :attr:`vat_id`, and adds related behaviour.

    This is inherited e.g. by :class:`lino_xl.lib.contacts.Partner`.

    This mixin does nothing when :mod:`lino_xl.lib.vat` is not installed.

    .. attribute:: vat_id

        The :term:`VAT id` used to identify this :term:`business partner`.

        Lino verifies validity based on the partner's :attr:`country` field.

    .. attribute:: vat_regime

        The default :term:`VAT regime` to use on invoices for this partner.


.. class:: VatTotal

    Model mixin that defines the database fields :attr:`total_incl`,
    :attr:`total_base` and :attr:`total_vat` and some related behaviour.

    Used for both the voucher (:class:`VatDocument`) and for each item of the
    voucher (:class:`VatItemBase`).

    .. attribute:: total_incl

        The amount VAT *included*.

    .. attribute:: total_base

        The amount VAT *excluded*.

    .. attribute:: total_vat

        The amount of VAT.

    .. attribute:: amount

      The amount VAT excluded *or* included, depending on :data:`item_vat`.



    All three total fields are :class:`lino.core.fields.PriceField`
    instances.

    The fields are editable by default, but implementing models can call
    :func:`lino.core.fields.update_field` to change this behaviour. A model that
    sets all fields to non-editable should also set the class attribute
    :attr:`edit_totals` to `False`.

    .. method:: get_trade_type

        Subclasses of VatTotal must implement this method.

    .. method:: get_vat_rule

        Return the VAT rule for this voucher or voucher item. Called
        when user edits a total field in the document header when
        :attr:`edit_totals` is `True`.

    .. method:: total_base_changed

        Called when user has edited the :attr:`total_base` field.  If
        total_base has been set to blank, then Lino fills it using
        :meth:`reset_totals`. If user has entered a value, compute
        :attr:`total_vat` and :attr:`total_incl` from this value using
        the vat rate. If there is no VatRule, :attr:`total_incl` and
        :attr:`total_vat` are set to None.

        If there are rounding differences, :attr:`total_vat` will get
        them.

    .. method:: total_vat_changed

        Called when user has edited the `total_vat` field.  If it has been
        set to blank, then Lino fills it using
        :meth:`reset_totals`. If user has entered a value, compute
        :attr:`total_incl`. If there is no VatRule, `total_incl` is
        set to None.

    .. method:: total_incl_changed

        Called when user has edited the `total_incl` field.  If total_incl
        has been set to blank, then Lino fills it using
        :meth:`reset_totals`. If user enters a value, compute
        :attr:`total_base` and :attr:`total_vat` from this value using
        the vat rate. If there is no VatRule, `total_incl` should be
        disabled, so this method will never be called.

        If there are rounding differences, `total_vat` will get them.


.. class:: VatVoucher

  Model mixin for vouchers that mention VAT.

  Inhertis from :class:`VatDocument`, :class:`PaymentRelated` and
  :class:`Payable`:

.. class:: VatDocument

    Abstract base class for invoices, offers and other vouchers.

    Inherited by :class:`VatAccountInvoice` as well as in other
    plugins (e.g. :class:`lino_xl.lib.trading.VatProductInvoice` and
    :class:`lino_xl.lib.ana.AnaAccountInvoice`).

    Models that inherit this mixin can set the following class
    attribute:

    .. attribute:: edit_totals

        Whether total amounts of the voucher are being edited by the end user.

        It this is `False`, Lino fills them as the sum of the vouchers items'
        amounts.

        The total fields of an invoice are not automatically updated each time
        an item is modified.  Users must click the :guilabel:`Σ` button
        ("Compute sums") or the :guilabel:`Save` or the :guilabel:`Register`
        button to update the invoice's totals.

    .. attribute:: xml_file_template

      The template to use for generating an :term:`XML file` from this voucher.

      Default value is ``"vat/peppol-ubl.xml"``.

    .. attribute:: xml_file_name

      The name of the XML file to generate from this voucher.

      This is a template for the string :meth:`format` method. The name ``self``
      refers to the database object for which the XML file is being generated.

      Default value is ``"{self.journal.ref}/{self.id}.xml"``.

    Inherits the following database fields from
    :class:`lino_xl.lib.contacts.PartnerRelated`:

    .. attribute:: partner

    Inherits the following database fields from :class:`VatTotal`:

    .. attribute:: total_base
    .. attribute:: total_vat
    .. attribute:: total_incl

    Adds the following database fields:

    .. attribute:: project

       Pointer to a :attr:`lino_xl.lib.accounting.Plugin.project_model`.

    .. attribute:: items_edited

       An automatically managed boolean field which says whether the
       user has manually edited the items of this document.  If this
       is False and :attr:`edit_totals` is True, Lino will
       automatically update the only invoice item according to
       :attr:`partner` and :attr:`vat_regime` and :attr:`total_incl`.

    .. attribute:: vat_regime

        The VAT regime to be used in this document.

        A pointer to :class:`VatRegimes`.


    Adds an action:

    .. attribute:: compute_sums

        Calls :class:`ComputeSums` for this document.

    Defines the following property:

    .. attribute:: vat_subtotals

      A list of `(category, rate, base, vat)` for every :term:`VAT category` and
      rate occurring in this voucher.

      This property is used by the
      :xfile:`vat/peppol-ubl.xml` and
      :xfile:`trading/VatProductInvoice/base.weasy.html`
      templates.

      Tested usage examples in :ref:`xl.bevat`, :ref:`xl.bevats` and
      :ref:`dg.plugins.eevat`.


.. class:: ComputeSums

    Compute the sum fields of a :class:`VatDocument` based on its
    items.

    Represented by a "Σ" button.


.. class:: VatItemBase

    Model mixin for items of a :class:`VatDocument`.

    Abstract Base class for
    :class:`lino_xl.lib.accounting.InvoiceItem`, i.e. the lines of
    invoices *without* unit prices and quantities.

    Subclasses must define a field called "voucher" which must be a
    ForeignKey with related_name="items" to the "owning document",
    which in turn must be a subclass of :class:`VatDocument`).


    .. attribute:: vat_class

        The :term:`VAT class` to use on this :term:`voucher item`.

    .. method:: get_peppol_vat_category(self)

      Return the :ref:`VAT category code <dg.topics.peppol.vatcat>` to be
      applied for this voucher item in a Peppol document.

    .. method:: get_vat_rule(self, tt)

        Return the `VatRule` that applies for this item.

        `tt` is the trade type (which is the same for each item of a
        voucher, that's why we expect the caller to provide it).

        This basically calls the class method
        :meth:`VatRule.get_vat_rule` with
        appropriate arguments.

        When selling certain products ("automated digital services")
        in the EU, you have to pay VAT in the buyer's country at that
        country's VAT rate.  See e.g.  `How can I comply with VAT
        obligations?
        <https://ec.europa.eu/growth/tools-databases/dem/watify/selling-online/how-can-i-comply-vat-obligations>`_.

        TODO: Add a new attribute `VatClass.buyers_country` or a
        checkbox `Product.buyers_country` or some other way to specify
        this.


.. class:: QtyVatItemBase


    Model mixin for items of a :class:`VatTotal`.  Extends
    :class:`VatItemBase` by adding :attr:`unit_price` and :attr:`qty`.

    Abstract Base class for :class:`lino_xl.lib.trading.InvoiceItem` and
    :class:`lino_xl.lib.trading.OrderItem`, i.e. invoice items *with*
    unit prices and quantities.

    .. attribute:: unit_price

      The unit price for this item.

    .. attribute:: qty

      The quantity of units of the product for by this item.

    Changing the :attr:`unit_price` ot the :attr:`qty` will automatically reset
    the total amount of this item: the value `unit_price * qty` will be stored
    in :attr:`total_incl` if :data:`item_vat` is `True`, otherwise in
    :attr:`total_base`.



VAT columns
===========

.. class:: VatColumns

    The list of VAT columns available on this site.

    The VAT column of a ledger account indicates where the movements
    on this account are to be collected in VAT declarations.


VAT declarations
================


.. class:: VatDeclaration

    Abstract base class for models that represent a :term:`VAT declaration`.

    Inherits from
    :class:`lino_xl.lib.sepa.Payable`
    :class:`lino_xl.lib.accounting.Voucher`
    :class:`lino_xl.lib.excerpts.Certifiable`
    :class:`lino_xl.lib.accounting.PeriodRange`

    .. attribute:: accounting_period

    .. method:: intracom_statement_iterator

      Yield a list of :class:`lino_xl.lib.contacts.Partner` objects, annotated
      with a field :attr:`total_base` that contains the sum of intra-community
      sales operations with this partner during the declared period range.

      Usage example in :ref:`dg.plugins.bevat.intracom_statement_iterator`.

    .. method:: get_payable_sums_dict

        Implements
        :meth:`lino_xl.lib.sepa.Payable.get_payable_sums_dict`.

        As a side effect this updates values in the computed fields of
        this declaration.


Declaration fields
==================

Defining the declaration fields is responsibility of each  :term:`national VAT
module`. But every individual field in every VAT declaration of every country is
an instance of one of the following three classes:

.. class:: MvtDeclarationField

  A declaration field to be computed by analyzing the *ledger movements*.

.. class:: WritableDeclarationField

  A declaration field to be entered manually by the end user.

.. class:: SumDeclarationField

  A declaration field that computes the sum of its *observed fields*.


All these three declaration field classes have a common ancestor
:class:`DeclarationField`.

.. class:: DeclarationField

    Base class for all declaration fields.

    It is not instantiated directly but by using one of its subclasses

    .. attribute:: editable

      Whether the value of this field is to be manually entered by the end user.

      Most fields are not editable, i.e. computed.

    .. attribute:: both_dc

      Whether the value of this field is to be manually entered by the end user.

    .. attribute:: fieldnames

       An optional space-separated list of names of *observed fields*, i.e.
       other declaration fields to be observed by this field.   If a field name
       is prefixed by a "-", the observed field will additionally be *inverted*.

       This is used only by sum fields.  The values of all observed fields will
       be added, except inverted fields whose value will be subtracted.

       Note that the booking direction (D or C) of the observed fields is
       ignored when computing the sum.

    .. attribute:: vat_regimes
    .. attribute:: vat_classes
    .. attribute:: vat_columns

    .. attribute:: exclude_vat_regimes
    .. attribute:: exclude_vat_classes
    .. attribute:: exclude_vat_columns


    .. attribute:: is_payable

        Whether the value of this field represents an amount to be paid to the
        tax office.


.. class:: DeclarationFieldsBase

  .. method:: add_mvt_field
  .. method:: add_sum_field
  .. method:: add_writable_field


Returnable VAT
==============

The :attr:`vat_returnable_account <VatRule.vat_returnable_account>` attribute
tells Lino whether this is considered :term:`returnable VAT`.



The VAT columns checker
=======================

.. class:: VatColumnsChecker

  Check VAT columns configuration.

This is an unbound data checker
(:attr:`lino.modlib.checkdata.Checker.model` is `None`), i.e. the messages aren't bound to a particular
database object.


.. _vat.generate_id:

Generating fictive VAT numbers
==============================

Note about :ticket:`5542` (Two VAT doctests fail
because generated VAT numbers differ).

The ``demo`` fixture of the ``vat`` plugin assigns a fictive (but syntactically
valid) VAT number to each :term:`business partner`.

The :meth:`seed` method initializes the random number generator, and if you use
the same seed value twice you will get the same random number twice. The
following code verifies this. It  always passes on my machine. It will always
return the same sequence of numbers because we seed the random generator with a
hard-coded integer. Does it test pass on other machines as well? Yes (at least
on GitLab)

>>> import random
>>> random.seed(1)
>>> print([random.randint(111, 999) for i in range(10)])
[248, 693, 978, 932, 893, 175, 372, 231, 618, 890]



.. _dg.plugins.vat.eu_country_codes:

Who is member of the European Union?
====================================

The plugin attribute :data:`eu_country_codes` is a set of ISO codes that are to be
considered part of the EU. :

>>> pprint(dd.plugins.vat.eu_country_codes, compact=True)
{'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR',
 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI',
 'SK'}

This is used to define the :term:`VAT area` of a partner, which in turn
influences the available :term:`VAT regimes <VAT regime>`.  See
:class:`lino_xl.lib.vat.VatAreas`.

When a member state leaves or joins the EU (and you have partners there), you
can either update your Lino (we plan to keep this list up to date), or you can
change it locally. For example in your :attr:`layouts_module
<lino.core.site.Site.layouts_module>` you may write code like this::

    if dd.today() > datetime.date(2025, 4, 11):
        dd.plugins.vat.eu_country_codes.add("GB")

    if dd.today() > datetime.date(2025, 4, 11):
        dd.plugins.vat.eu_country_codes.remove("BE")

The :attr:`isocode <lino_xl.lib.countries.Country.isocode>` fields in your
:class:`countries.Countries <lino_xl.lib.countries.Countries>` table must
match the codes specified in the :attr:`eu_country_codes
<lino_xl.lib.vat.Plugin.eu_country_codes>` plugin attribute.



Plugin configuration settings
=============================

A :term:`Lino site` that uses this plugin will usually specify the
:term:`national VAT module` for their :term:`VAT declarations <VAT declaration>`
by setting the :setting:`vat.declaration_plugin` plugin attribute.

Here is a list of the :term:`plugin settings <plugin setting>` for this plugin.

.. data:: eu_country_codes

  A set of ISO codes that are to be considered part of the EU. See
  :ref:`dg.plugins.vat.eu_country_codes`.

.. setting:: vat.default_vat_regime

  The default :term:`VAT regime`. If this is specified as a string, Lino will
  resolve it at startup into an item of :class:`VatRegimes`.

.. setting:: vat.default_vat_class

  The default VAT class. If this is specified as a string, Lino will
  resolve it at startup into an item of :class:`VatClasses`.


.. setting:: vat.declaration_plugin

    The plugin to use as your :term:`national VAT module`.

    See `National VAT modules`_ for a list of available plugins.

    This may remain `None` in applications that don't care about general
    accounting functionality.

.. setting:: vat.use_online_check

    Whether to verify :term:`VAT numbers <VAT number>` online using
    the VIES service of the EU. See :doc:`/topics/vies`.

    If this is `True`, :manage:`install` will install `pyvat
    <https://pyvat.readthedocs.io/en/latest/>`__.

.. data:: item_vat

    Whether item prices in trade documents are meant VAT included.

.. data:: unit_price_decpos

    Number of decimal positions for price fields that don't need to be rounded
    to a cent.

    Default value is 4. 
