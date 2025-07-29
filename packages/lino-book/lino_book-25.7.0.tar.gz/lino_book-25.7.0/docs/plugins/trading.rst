.. doctest docs/plugins/trading.rst
.. _dg.plugins.trading:

===========================================================
``trading`` : Exchanging things with your business partners
===========================================================

See also :ref:`ug.plugins.trading`.


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi4.startup import *
>>> ses = rt.login('robin')


The plugin
==========

.. currentmodule:: lino_xl.lib.trading

Lino implements product invoices in the :mod:`lino_xl.lib.trading`
plugin.  The internal codename was "sales" until 20240325, we renamed it because you
might generate product invoices for other trade types as well.

The plugin needs and automatically installs the
:mod:`lino_xl.lib.products` plugin.

It also needs and installs :mod:`lino_xl.lib.vat` (and not
:mod:`lino_xl.lib.vatless`).  Which means that if you want product invoices, you
cannot *not* also install the VAT framework. If the :term:`site operator` is not
subject to VAT, you might add :mod:`lino_xl.lib.bevats`, which hides most of the
VAT functionality.

>>> dd.plugins.trading.needs_plugins
['lino.modlib.memo', 'lino_xl.lib.products', 'lino_xl.lib.vat']

This plugin may be combined with the :mod:`lino_xl.lib.invoicing` plugin, which
adds automatic generation of such product invoices.


Configuration settings
======================

.. data:: items_column_names

  The :attr:`column_names` to use for :class:`ItemsByInvoice`.

  >>> dd.plugins.trading.items_column_names
  'product title unit_price qty discount_rate amount invoiceable *'

.. data:: columns_to_print

  The site-wide default value, for :attr:`PaperType.columns_to_print`.

  This can also get specified as a space-separated string, which will be
  converted to a list at startup.

  Value in this demo site is:

  >>> dd.plugins.trading.columns_to_print
  'invoiceable title unit_price qty amount'


.. setting:: trading.print_items_table

  The name of a :term:`data table` to use when printing invoices using appypod
  print method.

  No longer used.



Product invoices
================

.. class:: VatProductInvoice

    The Django model representing a :term:`product invoice`.

    Inherits from :class:`lino_xl.lib.accounting.Voucher`,
    :class:`TradingVoucher`, :class:`Matching`,
    :class:`lino_xl.lib.invoicing.InvoicingTargetVoucher` and :class:`StorageTransferer`.

    Virtual fields:

    .. attribute:: balance_before

       The balance of payments or debts that existed already before this
       voucher.

       On a printed invoice, this amount should be mentioned and added to the
       invoice's amount in order to get the total amount to pay.

    .. attribute:: balance_to_pay

       The balance of all movements matching this invoice.

    Methods:

    .. method:: get_print_items(self, ar):

        For usage in an appy template::

            do text
            from table(obj.get_print_items(ar))


.. class:: InvoiceItem

  The Django model representing an *item* of a *product invoice*.

  .. attribute:: invoiceable

    The invoiceable object to which this line applies. Points to the invoice
    generator that generated this line.

    This is a generic foreign key, the compound field is not editable. The
    default type can optionally be defined in the journal (field
    :attr:`default_invoiceable_type
    <lino_xl.lib.accounting.Journal.default_invoiceable_type>`).


.. class:: InvoiceDetail

    The Lino layout representing the detail view of a *product invoice*.

.. class:: Invoices

.. class:: InvoicesByJournal

    Shows all invoices of a given journal.

    The master instance must be a journal having :class:`VatProductInvoice` as
    :attr:`lino_xl.lib.accounting.Journal.voucher_type`.

.. class:: DueInvoices

    Shows all due product invoices.


.. class:: TradingVoucherItem

  Model mixin for voucher items that potentially refer to a product.

  .. attribute:: product

    The :term:`product` that is being sold or purchased.

  .. attribute:: description

    A multi-line rich text to be printed in the resulting printable document.

  .. attribute:: discount

    The percentage to subtract from the unit price of this item.


.. class:: ItemsByInvoicePrint

    The table used to render items in a printable document.

    .. attribute:: description_print

        TODO: write more about it.

.. class:: ItemsByInvoicePrintNoQtyColumn

    Alternative column layout to be used when printing an invoice.

.. class:: TradingPrintable

  Inherits from :class:`PartnerPrintable` and :class:`Certifiable`.

  .. attribute:: subject

    A single-line text that describes this voucher.

  .. attribute:: paper_type

    The type of paper to use when printing this voucher.


.. class:: TradingVoucher

    Common base class for :class:`lino_xl.lib.orders.Order` and
    :class:`VatProductInvoice`.

    Inherits from :class:`TradingPrintable` and :class:`VatVoucher
    <lino_xl.lib.vat.VatVoucher>`

    Subclasses must either add themselves a :attr:`date` field (as
    does :class:`Order <lino_xl.lib.orders.Order>`) or inherit it from
    Voucher (as does :class:`VatProductInvoice`).

    This model mixin sets :attr:`edit_totals
    <lino_xl.lib.vat.VatDocument.edit_totals>` to `False`.

    .. attribute:: intro

      An optional introduction text to be printed on the document.

    .. attribute:: default_discount

      Default value for :attr:`discount <TradingVoucherItem.discount>` fields in
      the items of this voucher.

    .. attribute:: print_items_table

        The table (column layout) to use in the printed document.

        :class:`ItemsByInvoicePrint`
        :class:`ItemsByInvoicePrintNoQtyColumn`


Paper types
===========

.. class:: PaperType

  Describes a paper type (document template) to be used when
  printing an invoice.

  A sample use case is to differentiate between invoices to get
  printed either on a company letterpaper for expedition via paper
  mail or into an email-friendly pdf file.

  Inherits from :class:`lino.utils.mldbc.mixins.BabelNamed`.


  .. attribute:: templates_group = 'trading/VatProductInvoice'

      A class attribute.

  .. attribute:: template

  .. attribute:: columns_to_print

    The list of columns to appear in the body a printed :term:`trade voucher`.

    The :xfile:`trading/VatProductInvoice/default.weasy.html` template currently
    supports the following columns: qty, title, unit_price, invoiceable, amount,
    total_incl and total_base.





Trade types
===========

The plugin updates your :attr:`lino_xl.lib.accounting.TradeTypes.sales`,
causing two additional database fields to be injected to
:class:`lino_xl.lib.products.Product`.

The first injected field is the sales price of a product:

>>> translation.activate('en')
>>> print(accounting.TradeTypes.sales.price_field_name)
sales_price
>>> print(accounting.TradeTypes.sales.price_field_label)
Sales price
>>> products.Product._meta.get_field('sales_price')
<lino.core.fields.PriceField: sales_price>

The other injected field is the sales base account of a product:

>>> print(accounting.TradeTypes.sales.base_account_field_name)
sales_account
>>> print(accounting.TradeTypes.sales.base_account_field_label)
Sales account
>>> products.Product._meta.get_field('sales_account')
<django.db.models.fields.related.ForeignKey: sales_account>



Trading rules
=============

Every :term:`business partner` can have a series of trading rules, one for each
trade type.

.. class:: TradingRule

    The Django model used to represent a *trading rule*.

    .. attribute:: partner

        The partner to which this trade rule applies.

    .. attribute:: payment_term

      The default payment terms to apply to new trading vouchers for this
      partner and trade type.

    .. attribute:: invoice_recipient

        The partner who should get the invoices caused by this partner.

    .. attribute:: paper_type

        The default paper type to be used for invoicing.


>>> fld = rt.models.trading.TradingRule._meta.get_field('invoice_recipient')
>>> print(fld.help_text)
The partner who should get the invoices caused by this partner.


.. class:: TradingRules

  Shows the list of trading rules.




The sales journal
=================

The cosi2 demo site has no VAT declarations, no purchase journals, no financial
journals, just a single sales journal.

>>> rt.show('accounting.Journals', column_names="ref name trade_type")
=========== ================ ==================== ============
 Reference   Designation      Designation (es)     Trade type
----------- ---------------- -------------------- ------------
 SLS         Sales invoices   Facturas de ventas   Sales
=========== ================ ==================== ============
<BLANKLINE>

Invoices are sorted by number and year.  The entry date should normally never
"go back".  Lino supports exceptional situations, e.g. starting to issue
invoices at a given number or entering a series of sales invoices from a legacy
system afterwards.

>>> jnl = rt.models.accounting.Journal.get_by_ref("SLS")
>>> rt.show('trading.InvoicesByJournal', jnl)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
==================== ============ ======= ======= =========================== ========= =============== ================
 No.                  Date         Date1   Date2   Partner                     Subject   TotIncl         Workflow
-------------------- ------------ ------- ------- --------------------------- --------- --------------- ----------------
 1/2024               07/01/2024                   Rumma & Ko OÜ                         2 999,85        **Registered**
 2/2024               08/01/2024                   Bäckerei Ausdemwald                   2 039,82        **Registered**
 3/2024               09/01/2024                   Bäckerei Mießen                       679,81          **Registered**
 4/2024               10/01/2024                   Bäckerei Schmitz                      280,00          **Registered**
 5/2024               11/01/2024                   Garage Mergelsberg                    535,00          **Registered**
 6/2024               07/02/2024                   Donderweer BV                         1 110,16        **Registered**
 7/2024               08/02/2024                   Van Achter NV                         1 499,85        **Registered**
 8/2024               09/02/2024                   Hans Flott & Co                       1 939,82        **Registered**
 9/2024               10/02/2024                   Bernd Brechts Bücherladen             815,96          **Registered**
 **Total (9 rows)**                                                                      **11 900,27**
==================== ============ ======= ======= =========================== ========= =============== ================
<BLANKLINE>


>>> mt = contenttypes.ContentType.objects.get_for_model(accounting.Journal).id
>>> obj = trading.VatProductInvoice.objects.get(journal__ref="SLS", number=9)

>>> url = '/api/trading/InvoicesByJournal/{0}'.format(obj.id)
>>> url += '?mt={0}&mk={1}&an=detail&fmt=json'.format(mt, obj.journal.id)
>>> test_client.force_login(ses.user)
>>> res = test_client.get(url, REMOTE_USER='robin')
>>> # res.content
>>> r = check_json_result(res, "navinfo data disable_delete id param_values title")
>>> print(r['title']) #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
<a ...>Sales invoices (SLS)</a> » SLS 9/2024



IllegalText: The <text:section> element does not allow text
===========================================================

The following reproduces a situation which caused above error
until :blogref:`20151111`.

TODO: it is currently disabled for different reasons: leaves dangling
temporary directories, does not reproduce the problem (probably
because we must clear the cache).

>> obj = rt.models.trading.VatProductInvoice.objects.all()[0]
>> obj
VatProductInvoice #1 ('SLS#1')
>> from lino.modlib.appypod.appy_renderer import AppyRenderer
>> tplfile = rt.find_config_file('trading/VatProductInvoice/Default.odt')
>> context = dict()
>> outfile = "tmp.odt"
>> renderer = AppyRenderer(ses, tplfile, context, outfile)
>> ar = rt.models.trading.ItemsByInvoicePrint.create_request(obj)
>> print(renderer.insert_table(ar))  #doctest: +ELLIPSIS
<table:table ...</table:table-rows></table:table>


>> item = obj.items.all()[0]
>> item.description = """
... <p>intro:</p><ol><li>first</li><li>second</li></ol>
... <p></p>
... """
>> item.save()
>> print(renderer.insert_table(ar))  #doctest: +ELLIPSIS
Traceback (most recent call last):
...
IllegalText: The <text:section> element does not allow text


The language of an invoice
==========================

The language of an invoice not necessary that of the user who enters
the invoice. It is either the partner's :attr:`language
<lino.modlib.contacts.models.Partner.language>` or (if this is empty)
the Site's :meth:`get_default_language
<lino.core.site.Site.get_default_language>`.

.. _dg.discount_unit_price:

Discount was applied on the unit price
======================================

Until 20250501 the discount of an invoice item
(:attr:`TradingVoucherItem.discount` was getting applied to the *unit price*,
not to the *total amount*.  This may lead to surprising situations. For example,
when the unit price was 0.01 and the quantity is 1000, the :attr:`total_base`
would remain 10.00 even with a discount of 40%, and it suddenly becomes 0.00
when you give more than 50% discount.


>>> vch = trading.VatProductInvoice.objects.last()
>>> prd = products.Product(name="Nail", sales_price="0.01")
>>> prd.full_clean()
>>> prd.save()
>>> i = vch.add_voucher_item(product=prd, qty=1000)
>>> i.full_clean()
>>> i.product_changed()
>>> print(i.total_base)
10.00
>>> i.discount_rate = 40
>>> i.discount_rate_changed()
>>> print(i.total_base)
6.00
>>> i.discount_rate = 51
>>> i.discount_rate_changed()
>>> print(i.total_base)
4.90
>>> prd.delete()


Some fields of a registered voucher can remain editable
=======================================================

The default behaviour is that a registered voucher is not editable.

>>> UserTypes = rt.models.users.UserTypes
>>> InvoicesByJournal = rt.models.trading.InvoicesByJournal

>>> obj = InvoicesByJournal.model.objects.first()
>>> obj.state
<accounting.VoucherStates.registered:20>

>>> actor = InvoicesByJournal
>>> actor.get_row_permission(
...     obj, ses, actor.get_row_state(obj), actor.update_action)
False

But if you set `accounting.VoucherState.is_editable` to True for the
:attr:`registered` state, then the record itself becomes editable.

>>> accounting.VoucherStates.registered.is_editable = True

>>> actor.get_row_permission(
...     obj, ses, actor.get_row_state(obj), actor.update_action)
True

>>> resp = obj.disabled_fields(obj.get_default_table().request(parent=ses))
>>> assert resp == {'clear_printed', 'send_now'}

Only the voucher state refuses editing, the actors don't disable editing for all
rows:

>>> rt.models.trading.InvoicesByJournal.editable
True
>>> InvoicesByJournal.hide_editing(UserTypes.admin)
False

TODO: Split `is_editable` of a :term:`voucher state` into two booleans:
fields_editable and row_editable.  For example the partner field of a registered
trading invoice must never be editable while the language field or some
narration might remain editable.

..
  >>> dbhash.check_virgin()
