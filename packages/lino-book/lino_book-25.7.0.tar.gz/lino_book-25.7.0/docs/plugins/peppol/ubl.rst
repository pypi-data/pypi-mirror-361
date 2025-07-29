.. doctest docs/plugins/peppol/ubl.rst
.. _dg.plugins.ubl:

===========================
Generating Peppol XML files
===========================

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *

Lino has two database models that can become a :term:`Peppol document`:
:class:`VatProductInvoice <lino_xl.lib.trading.VatProductInvoice>` and
:class:`VatAccountInvoice <lino_xl.lib.vat.VatAccountInvoice>`. The former is
typically used for sales and the latter for purchase.  Both models inherit from
:class:`lino.modlib.jinja.XMLMaker`.

>>> for m in rt.models_by_base(jinja.XMLMaker):
...     if m.xml_file_template:
...         print(full_model_name(m), m.xml_file_template, m.xml_validator_file)
... #doctest: +ELLIPSIS
trading.VatProductInvoice vat/peppol-ubl.xml .../lino_xl/lib/vat/XSD/PEPPOL-EN16931-UBL.sch
vat.VatAccountInvoice vat/peppol-ubl.xml .../lino_xl/lib/vat/XSD/PEPPOL-EN16931-UBL.sch

In order to create the XML of a :term:`Peppol document`, Lino  uses a single
template :xfile:`vat/peppol-ubl.xml`.

.. xfile:: vat/peppol-ubl.xml

  The Jinja template file used to generate the XML from a :term:`Peppol
  document`.

This file contains quite some business logic.

This template file is derived from the :file:`base-example.xml` file at
https://github.com/OpenPEPPOL/peppol-bis-invoice-3/blob/master/rules/examples/base-example.xml

Lino supports the `UBL BIS 3.0 <https://docs.peppol.eu/poacc/billing/3.0/>`__
format for both inbound and outbound documents.
Peppol differentiates between
`invoice <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/tree/>`__
and
`creditnote <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-creditnote/tree/>`__.

Lino does not validate Peppol documents (see :doc:`/topics/schematron` for details)
because that's done by the Peppol network. During development it can be useful
to manually validate an XML file:

- https://www.ubl.be/validator
- https://ecosio.com/en/peppol-and-xml-document-validator (Select "OpenPeppol UBL invoice")


The parties of an invoice
=========================

- Seller : the partner who sells. Also called supplier, provider.
  See `cac:AccountingSupplierParty <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-AccountingSupplierParty/>`__

- Buyer : the partner who buys. Also called invoicee, recipient, customer.
  See `cac:AccountingCustomerParty <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-AccountingCustomerParty/>`__

- Payee : the partner who receives the payment.
  Shall be used when the Payee is different from the Seller.
  Lino currently doesn't use this element.
  See `cac:PayeeParty
  <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-PayeeParty/>`_.

- Tax representative :
  the legal person who represents the seller at the tax office.
  Lino currently doesn't use this element.
  See `cac:TaxRepresentativeParty <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-TaxRepresentativeParty/>`__.


Both the seller and the buyer of an invoice contain a single mandatory element
`cac:Party
<https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-AccountingSupplierParty/cac-Party/>`__,
which contains a mandatory element `cbc:EndpointID
<https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-AccountingSupplierParty/cac-Party/cbc-EndpointID/>`__,
which identifies the party's electronic address.

This ``cbc:EndpointID`` element contains the identification number as a textual
value, and must have an attribute ``schemeID``, which refers to the
Electronic Address Scheme (:term:`EAS`)
to use when looking up the identification number of a party.

In other places we need a element ``cbc:CompanyID``,


Electronic Address Scheme
=========================

One of the challenges of Peppol was how to identify your business partners
across national borders. Peppol suggests a standard for international
identification of legal persons.

Peppol does this in two steps: first you specify one of the recognized official
registries of identification codes. Peppol knows a few hundred of them.  These
are called "Electronic Address Schemes"
or . Let's call them :term:`EAS`.

.. glossary::

  EAS

    Abbreviation for "Electronic Address Scheme".
    A recognized official registry of identification codes.

    Some documents call them "Participant Identifier Schemes": `example
    <https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/Registry+of+supporting+artefacts+to+implement+EN16931?preview=/467108974/691830878/Electronic%20Address%20Scheme%20Code%20list%20-%20version%2012%20-%20published%20Sept2023.xlsx>`__)

Some examples of :term:`EAS` codes:

- 9925 : Belgium VAT number
- 0208 : Belgium Company number
- 9931 : Estonian VAT number

It seems that EAS 9925 is a subset of EAS 0208: every party subject to VAT in
Belgium also as a company number, which is the same as its VAT number. Hence
normal companies should be in both registers, while companies like insurances
and some non-profit organizations (who are not subject to VAT and hence have no
VAT number) will be only in EAS 0208.

The `commondata.peppolcodes
<https://github.com/lsaffre/commondata/tree/master?tab=readme-ov-file#peppol-codes>`__
module defines a dict :data:`COUNTRY2SCHEME`, which maps country codes to the
:term:`EAS` number of the VAT office of that country. There are nations with
other identification schemes than the VAT office, but  :data:`COUNTRY2SCHEME`
does not contain them. The `Lino Peppol plugin
<https://using.lino-framework.org/plugins/peppol/index.html>`_ uses this when
generating a Peppol XML file for outbound documents.

>>> from commondata.peppolcodes import COUNTRY2SCHEME

>>> pprint(COUNTRY2SCHEME)  #doctest: +NORMALIZE_WHITESPACE
{'AD': '9922',
 'AL': '9923',
 'AT': '9914',
 'BA': '9924',
 'BE': '9925',
 'BG': '9926',
 'CH': '9927',
 'CY': '9928',
 'CZ': '9929',
 'DE': '9930',
 'EE': '9931',
 'ES': '9920',
 'FI': '0213',
 'FR': '9957',
 'GB': '9932',
 'GR': '9933',
 'HR': '9934',
 'HU': '9910',
 'IE': '9935',
 'IT': '9906',
 'LI': '9936',
 'LT': '9937',
 'LU': '9938',
 'LV': '9939',
 'MC': '9940',
 'ME': '9941',
 'MK': '9942',
 'MT': '9943',
 'NL': '9944',
 'NO': '9909',
 'PL': '9945',
 'PT': '9946',
 'RO': '9947',
 'RS': '9948',
 'SE': '9955',
 'SI': '9949',
 'SK': '9950',
 'SM': '9951',
 'TR': '9952',
 'VA': '9953',
 'international': '9912'}

>>> peppol_countries = set(COUNTRY2SCHEME.keys())

The list contains some countries that are not part of the European Union
(according to :data:`lino_xl.lib.vat.eu_country_codes`):

>>> sorted(peppol_countries - dd.plugins.vat.eu_country_codes)
['AD', 'AL', 'BA', 'CH', 'GB', 'LI', 'MC', 'ME', 'MK', 'NO', 'RS', 'SM', 'TR', 'VA', 'international']

Denmark is currently *not* in our list because it doesn't have a registry scheme
that ends with "VAT".

>>> dd.plugins.vat.eu_country_codes - peppol_countries
{'DK'}



.. _dg.topics.peppol.vatcat:

The VAT category
================

.. glossary::

  VAT category

    An alphabetic code defined as part of Peppol in the `UNCL5305 code list
    <https://docs.peppol.eu/poacc/billing/3.0/codelist/UNCL5305/>`__.

The ``<cac:ClassifiedTaxCategory>`` element contains "a group of business terms
providing information about the VAT applicable for the goods and services
invoiced on the invoice or the invoice line."

- ``<cbc:ID>`` : The :term:`VAT category` code for the invoiced item.

- ``<cbc:Percent>`` : The applied VAT rate. A number, potentially with decimal
  positions

- ``<cac:TaxScheme>`` : a mysterious but mandatory element. According to our
  sources it must contain exactly one child element ``<cbc:ID>VAT</cbc:ID>``,
  where the word "VAT" seems to mean that the seller is identified using their
  VAT identifier. We don't know whether it may contain other values.

A good introduction into why we have all these categories and rates is here:
`VAT Rates in Europe 2024
<https://www.globalvatcompliance.com/globalvatnews/vat-rates-in-europe-2021/>`__


You might think that this is a reliable definition because it mentions a "code
list" called "UNCL5305", That sounds impressive, doesn't it. But to make things
more fun, the Internet currently knows are at least two code lists called
"UNCL5305":

- https://docs.peppol.eu/pracc/catalogue/1.0/codelist/UNCL5305
- https://docs.peppol.eu/poacc/billing/3.0/codelist/UNCL5305

It seems that for :term:`Ibanity` we must use the latter one. This list
specifies the allowed VAT categories:

== =================== ================================================================================================
AE Vat Reverse Charge  VAT is levied from the buyer.
E  Exempt from Tax     Taxes are not applicable.
S  Standard rate       The standard rate is applicable.
Z  Zero rated goods    The goods are at a zero rate.
G  Free export item    VAT not charged
O  Outside scope       Services outside scope of tax
K  VAT exempt for EEA  VAT exempt due to an intra-community supply of goods and services in the European Economic Area
== =================== ================================================================================================

I don't know what G and O are used for, because none of our customers has ever
asked for this.

Lino has two functions to be used in the :xfile:`vat/peppol-ubl.xml` template:

- :meth:`VatItemBase.get_peppol_vat_category` returns the VAT category of a
  :term:`voucher item` by interpreting the :term:`VAT regime` and :term:`VAT
  class`. This is used for the ``<cac:ClassifiedTaxCategory>`` element.

- :meth:`linox_xl.lib.VatVoucher.get_vat_subtotals` returns an iterator of
  4-tuples `(categ, rate, total_base, total_vat)`. These are used for the
  ``<cac:TaxSubtotal>`` elements of the document.


>>> dd.plugins.vat.declaration_plugin
'lino_xl.lib.bevat'

>>> rows = []
>>> coll = collections.OrderedDict()
>>> for obj in trading.InvoiceItem.objects.all():
...     k = (obj.vat_class, obj.voucher.vat_regime, obj.get_peppol_vat_category())
...     if k not in coll:
...         coll[k] = obj
>>> for k, obj in coll.items():
...     vat_class, vat_regime, pc = k
...     rows.append([vat_class.name, vat_regime.name, pc, obj])
>>> headers = ["Class", "Regime", "Cat.", "Line"]
>>> print(rstgen.table(headers, rows))
========== ========== ====== ===============
 Class      Regime     Cat.   Line
---------- ---------- ------ ---------------
 services   subject    S      SLS 1/2023#1
 services   intracom   AE     SLS 2/2023#1
 reduced    subject    S      SLS 6/2023#1
 exempt     subject    Z      SLS 6/2023#2
 reduced    intracom   AE     SLS 11/2023#2
 exempt     intracom   AE     SLS 12/2023#1
 services   normal     S      SLS 14/2023#1
 reduced    normal     S      SLS 17/2023#1
 exempt     normal     Z      SLS 17/2023#2
========== ========== ====== ===============
<BLANKLINE>


The following snippet is to test the
:attr:`lino_xl.lib.trading.VatProductInvoice.vat_subtotals` property.

>>> obj = [o for o in trading.VatProductInvoice.objects.all() if len(o.vat_subtotals) > 1][-1]

>>> print(f"{obj} {obj.total_base} {obj.total_vat} {obj.total_incl}")
SLS 12/2025 719.60 140.35 859.95
>>> round(719.60 + 140.35, 2)
859.95
>>> headers = ['Cat', "Rate", "Base", "VAT"]
>>> rows = []
>>> for cat, rule, total_base, total_vat in obj.vat_subtotals:
...     rows.append([cat, rule.rate, total_base, total_vat])
>>> print(rstgen.table(headers, rows))
===== ====== ======== ========
 Cat   Rate   Base     VAT
----- ------ -------- --------
 S     0.21   600.00   126.00
 S     0.12   119.60   14.35
===== ====== ======== ========
<BLANKLINE>

>>> round(600+119.60, 2)
719.6
>>> round(126 + 14.35, 2)
140.35


Amounts
=======

Vocabulary:

- Line net amount: Invoiced quantity * Unit Gross Price
- Allowances : discount or similar amount to *subtract* from the net amount
- Charges : some fee, tax (other than VAT) or similar amount to *add* to the net
  amount
- Line extension amount : Net amount + Charges - Allowances.

An invoice must have exactly one `cac:LegalMonetaryTotal
<https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-LegalMonetaryTotal/>`__
element, which provides the monetary totals for the invoice. It can have the
following children (each child at most once):

- `cbc:LineExtensionAmount
  <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-LegalMonetaryTotal/cbc-LineExtensionAmount/>`__:
  Sum of all invoice line amounts in the invoice, net of tax and settlement
  discounts, but inclusive of any applicable rounding amount.

- `cbc:TaxExclusiveAmount
  <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-LegalMonetaryTotal/cbc-TaxExclusiveAmount/>`__:
  total amount of the invoice without VAT.

- `cbc:TaxInclusiveAmount
  <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-LegalMonetaryTotal/cbc-TaxInclusiveAmount/>`__:
  total amount of the invoice with VAT.

- `cbc:AllowanceTotalAmount
  <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-LegalMonetaryTotal/cbc-AllowanceTotalAmount/>`__

- `cbc:ChargeTotalAmount
  <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-LegalMonetaryTotal/cbc-ChargeTotalAmount/>`__:
  Sum of all charges in the invoice.

- `cbc:PrepaidAmount
  <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-LegalMonetaryTotal/cbc-PrepaidAmount/>`__:
  Sum of amounts that have been paid in advance.

- `cbc:PayableRoundingAmount <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-LegalMonetaryTotal/cbc-PayableRoundingAmount/>`__
  Amount to be added to the invoice total to round the amount to be paid.

- 'cbc:PayableAmount
  <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-LegalMonetaryTotal/cbc-PayableAmount/>`__:
  outstanding amount that is requested to be paid

Amounts must be rounded to maximum 2 decimals.
Each amount element has a mandatory attribute ``currencyID``.

Some Schematron rules and how we handle them
============================================

- A buyer reference or purchase order reference MUST be provided.

  The specs about `cbc:BuyerReference
  <https://docs.peppol.eu/poacc/billing/3.0/2024-Q2/syntax/ubl-invoice/cbc-BuyerReference/>`_
  say indeed that "An invoice must have buyer reference or purchase order
  reference (BT-13)."

  🡒 When :attr:`your_ref` is empty, Lino writes "not specified".
