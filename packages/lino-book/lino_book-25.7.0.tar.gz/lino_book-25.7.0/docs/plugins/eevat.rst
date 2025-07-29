.. doctest docs/plugins/eevat.rst
.. _dg.plugins.eevat:

=====================================
``eevat`` : Estonian VAT declarations
=====================================

.. currentmodule:: lino_xl.lib.eevat

The :mod:`lino_xl.lib.eevat` plugin adds functionality for handling **Estonian
VAT declarations**.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi3.startup import *


Dependencies
============

Installing this plugin will automatically install :mod:`lino_xl.lib.vat`.

>>> dd.plugins.eevat.needs_plugins
['lino_xl.lib.vat']


VAT regimes
===========

>>> rt.show(vat.VatRegimes, language="en")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
======= ============== ================= =============== ============== ================ =============
 value   name           text              VAT area        Needs VAT id   Reverse charge   Send Peppol
------- -------------- ----------------- --------------- -------------- ---------------- -------------
 10      normal         Private person                    No             No               No
 20      subject        Subject to VAT    National        Yes            No               No
 25      cocontractor   Co-contractor     National        Yes            Yes              No
 30      intracom       Intra-community   EU              Yes            Yes              No
 40      tax_free       Tax-free                          No             No               No
 50      outside        Outside EU        International   No             No               No
 60      exempt         Exempt                            No             No               No
======= ============== ================= =============== ============== ================ =============
<BLANKLINE>


.. _VatClasses.ee:

Estonian VAT classes
====================

These are the :term:`VAT classes <VAT class>` used in Estonia:

>>> rt.show(vat.VatClasses, language="en")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
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



VAT rates
=========

The normal Estonian VAT rate is 22% since 2024-01-01.  The demo date is after
this date:

>>> settings.SITE.today()
datetime.date(2024, 6, 12)

Here is the rule that applied when selling a normal product to a private person
on 2024-06-12:

>>> rule = vat.VatRules.get_vat_rule(
... vat.VatAreas.national, accounting.TradeTypes.sales,
... vat.VatRegimes.normal, vat.VatClasses.goods)
>>> print(rule)
VAT rule 54: (from 01/01/2024)
if (Sales, Goods at normal VAT rate) then
apply 0.22 %
and book to VAT due

>>> rule.rate
Decimal('0.22')
>>> rule.vat_account
<accounting.CommonAccounts.vat_due:4510>
>>> rule.vat_account.get_object()
Account #7 ('(4510) VAT due')
>>> rule.vat_returnable_account is None
True

When an invoice is dated before 2024-01-01, you get the old VAT rate:

>>> rule = vat.VatRules.get_vat_rule(
... vat.VatAreas.national, accounting.TradeTypes.sales,
... vat.VatRegimes.normal, vat.VatClasses.goods, date=i2d(20230612))
>>> rule.rate
Decimal('0.20')


Or selling a normal product to a company outside of Europe:

>>> rule = vat.VatRules.get_vat_rule(
...    vat.VatAreas.international, accounting.TradeTypes.sales,
...    vat.VatRegimes.normal, vat.VatClasses.goods)
>>> rule.rate
Decimal('0.22')
>>> rule.vat_account
<accounting.CommonAccounts.vat_due:4510>
>>> rule.vat_returnable_account is None
True

Returnable VAT is used only in purchase invoices, not in sales.  In a sales
invoice to an intracom partner, there is simply no VAT to be generated. IOW even
for services and goods for which national customers must pay VAT (because their
VAT class is normal or reduced but not exempt), the VAT rule specifies a rate of
0.

Selling a product to a VAT-subjected company in another country of the European
Union (:attr:`VatRegimes.intracom`):

>>> rule = vat.VatRules.get_vat_rule(
... vat.VatAreas.eu, accounting.TradeTypes.sales,
... vat.VatRegimes.intracom, vat.VatClasses.goods)
>>> rule.rate
Decimal('0')
>>> rule.vat_account
>>> rule.vat_returnable_account

But when the buyer is not subjected (:attr:`VatRegimes.normal`), they must pay
the VAT (and you must declare it and pay it to the Estonian Tax office):

>>> rule = vat.VatRules.get_vat_rule(
... vat.VatAreas.eu, accounting.TradeTypes.sales,
... vat.VatRegimes.normal, vat.VatClasses.goods)
>>> rule.rate
Decimal('0.22')
>>> rule.vat_account
<accounting.CommonAccounts.vat_due:4510>
>>> rule.vat_returnable_account is None
True



When you buy services from a national provider who is subject to VAT, then you
will add 22% of VAT (and pay it to the provider, and you will get it back after
your declaration).

>>> rule = vat.VatRules.get_vat_rule(
...     vat.VatAreas.national, accounting.TradeTypes.purchases,
...     vat.VatRegimes.subject, vat.VatClasses.services)
>>> rule.rate
Decimal('0.22')
>>> rule.vat_returnable_account is None
True

When you buy services from a private person or some organization that is not
subject to VAT, then you don't talk about VAT in your invoice.

>>> rule = vat.VatRules.get_vat_rule(
...     vat.VatAreas.national, accounting.TradeTypes.purchases,
...     vat.VatRegimes.normal, vat.VatClasses.services)
>>> rule.rate
Decimal('0')



VAT rules
=========

When this plugin is used as the :term:`national VAT module`, we have the
following :term:`VAT rules <VAT rule>`.

>>> rt.show(vat.VatRules, language="en")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
+-------+--------------------------------------------------------------------------+
| value | Description                                                              |
+=======+==========================================================================+
| 1     | VAT rule 1:                                                              |
|       | if (Exempt) then                                                         |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 2     | VAT rule 2:                                                              |
|       | if (Outside EU) then                                                     |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 3     | VAT rule 3: (until 31/12/2023)                                           |
|       | if (Purchases, Intra-community, EU, Services) then                       |
|       | apply 0.20 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 4     | VAT rule 4: (until 31/12/2023)                                           |
|       | if (Sales, Intra-community, EU, Services) then                           |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 5     | VAT rule 5: (until 31/12/2023)                                           |
|       | if (Purchases, Co-contractor, National, Services) then                   |
|       | apply 0.20 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 6     | VAT rule 6: (until 31/12/2023)                                           |
|       | if (Sales, Co-contractor, National, Services) then                       |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 7     | VAT rule 7: (until 31/12/2023)                                           |
|       | if (Purchases, Intra-community, EU, Goods at normal VAT rate) then       |
|       | apply 0.20 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 8     | VAT rule 8: (until 31/12/2023)                                           |
|       | if (Sales, Intra-community, EU, Goods at normal VAT rate) then           |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 9     | VAT rule 9: (until 31/12/2023)                                           |
|       | if (Purchases, Co-contractor, National, Goods at normal VAT rate) then   |
|       | apply 0.20 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 10    | VAT rule 10: (until 31/12/2023)                                          |
|       | if (Sales, Co-contractor, National, Goods at normal VAT rate) then       |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 11    | VAT rule 11: (until 31/12/2023)                                          |
|       | if (Purchases, Intra-community, EU, Real estate) then                    |
|       | apply 0.20 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 12    | VAT rule 12: (until 31/12/2023)                                          |
|       | if (Sales, Intra-community, EU, Real estate) then                        |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 13    | VAT rule 13: (until 31/12/2023)                                          |
|       | if (Purchases, Co-contractor, National, Real estate) then                |
|       | apply 0.20 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 14    | VAT rule 14: (until 31/12/2023)                                          |
|       | if (Sales, Co-contractor, National, Real estate) then                    |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 15    | VAT rule 15: (until 31/12/2023)                                          |
|       | if (Purchases, Intra-community, EU, Vehicles) then                       |
|       | apply 0.20 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 16    | VAT rule 16: (until 31/12/2023)                                          |
|       | if (Sales, Intra-community, EU, Vehicles) then                           |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 17    | VAT rule 17: (until 31/12/2023)                                          |
|       | if (Purchases, Co-contractor, National, Vehicles) then                   |
|       | apply 0.20 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 18    | VAT rule 18: (until 31/12/2023)                                          |
|       | if (Sales, Co-contractor, National, Vehicles) then                       |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 19    | VAT rule 19: (until 31/12/2023)                                          |
|       | if (Purchases, Subject to VAT, National, Services) then                  |
|       | apply 0.20 %                                                             |
|       | and book to VAT deductible                                               |
+-------+--------------------------------------------------------------------------+
| 20    | VAT rule 20: (until 31/12/2023)                                          |
|       | if (Purchases, Subject to VAT, National, Goods at normal VAT rate) then  |
|       | apply 0.20 %                                                             |
|       | and book to VAT deductible                                               |
+-------+--------------------------------------------------------------------------+
| 21    | VAT rule 21: (until 31/12/2023)                                          |
|       | if (Purchases, Subject to VAT, National, Real estate) then               |
|       | apply 0.20 %                                                             |
|       | and book to VAT deductible                                               |
+-------+--------------------------------------------------------------------------+
| 22    | VAT rule 22: (until 31/12/2023)                                          |
|       | if (Purchases, Subject to VAT, National, Vehicles) then                  |
|       | apply 0.20 %                                                             |
|       | and book to VAT deductible                                               |
+-------+--------------------------------------------------------------------------+
| 23    | VAT rule 23: (until 31/12/2023)                                          |
|       | if (Sales, Services) then                                                |
|       | apply 0.20 %                                                             |
|       | and book to VAT due                                                      |
+-------+--------------------------------------------------------------------------+
| 24    | VAT rule 24: (until 31/12/2023)                                          |
|       | if (Sales, Goods at normal VAT rate) then                                |
|       | apply 0.20 %                                                             |
|       | and book to VAT due                                                      |
+-------+--------------------------------------------------------------------------+
| 25    | VAT rule 25: (until 31/12/2023)                                          |
|       | if (Sales, Real estate) then                                             |
|       | apply 0.20 %                                                             |
|       | and book to VAT due                                                      |
+-------+--------------------------------------------------------------------------+
| 26    | VAT rule 26: (until 31/12/2023)                                          |
|       | if (Sales, Vehicles) then                                                |
|       | apply 0.20 %                                                             |
|       | and book to VAT due                                                      |
+-------+--------------------------------------------------------------------------+
| 27    | VAT rule 27: (until 31/12/2024)                                          |
|       | if (Purchases, Intra-community, EU, Goods at reduced VAT rate) then      |
|       | apply 0.09 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 28    | VAT rule 28: (until 31/12/2024)                                          |
|       | if (Sales, Intra-community, EU, Goods at reduced VAT rate) then          |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 29    | VAT rule 29: (until 31/12/2024)                                          |
|       | if (Purchases, Co-contractor, National, Goods at reduced VAT rate) then  |
|       | apply 0.09 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 30    | VAT rule 30: (until 31/12/2024)                                          |
|       | if (Sales, Co-contractor, National, Goods at reduced VAT rate) then      |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 31    | VAT rule 31: (until 31/12/2024)                                          |
|       | if (Purchases, Subject to VAT, National, Goods at reduced VAT rate) then |
|       | apply 0.09 %                                                             |
|       | and book to VAT deductible                                               |
+-------+--------------------------------------------------------------------------+
| 32    | VAT rule 32: (until 31/12/2024)                                          |
|       | if (Sales, Goods at reduced VAT rate) then                               |
|       | apply 0.09 %                                                             |
|       | and book to VAT due                                                      |
+-------+--------------------------------------------------------------------------+
| 33    | VAT rule 33: (from 01/01/2024)                                           |
|       | if (Purchases, Intra-community, EU, Services) then                       |
|       | apply 0.22 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 34    | VAT rule 34: (from 01/01/2024)                                           |
|       | if (Sales, Intra-community, EU, Services) then                           |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 35    | VAT rule 35: (from 01/01/2024)                                           |
|       | if (Purchases, Co-contractor, National, Services) then                   |
|       | apply 0.22 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 36    | VAT rule 36: (from 01/01/2024)                                           |
|       | if (Sales, Co-contractor, National, Services) then                       |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 37    | VAT rule 37: (from 01/01/2024)                                           |
|       | if (Purchases, Intra-community, EU, Goods at normal VAT rate) then       |
|       | apply 0.22 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 38    | VAT rule 38: (from 01/01/2024)                                           |
|       | if (Sales, Intra-community, EU, Goods at normal VAT rate) then           |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 39    | VAT rule 39: (from 01/01/2024)                                           |
|       | if (Purchases, Co-contractor, National, Goods at normal VAT rate) then   |
|       | apply 0.22 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 40    | VAT rule 40: (from 01/01/2024)                                           |
|       | if (Sales, Co-contractor, National, Goods at normal VAT rate) then       |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 41    | VAT rule 41: (from 01/01/2024)                                           |
|       | if (Purchases, Intra-community, EU, Real estate) then                    |
|       | apply 0.22 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 42    | VAT rule 42: (from 01/01/2024)                                           |
|       | if (Sales, Intra-community, EU, Real estate) then                        |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 43    | VAT rule 43: (from 01/01/2024)                                           |
|       | if (Purchases, Co-contractor, National, Real estate) then                |
|       | apply 0.22 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 44    | VAT rule 44: (from 01/01/2024)                                           |
|       | if (Sales, Co-contractor, National, Real estate) then                    |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 45    | VAT rule 45: (from 01/01/2024)                                           |
|       | if (Purchases, Intra-community, EU, Vehicles) then                       |
|       | apply 0.22 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 46    | VAT rule 46: (from 01/01/2024)                                           |
|       | if (Sales, Intra-community, EU, Vehicles) then                           |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 47    | VAT rule 47: (from 01/01/2024)                                           |
|       | if (Purchases, Co-contractor, National, Vehicles) then                   |
|       | apply 0.22 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 48    | VAT rule 48: (from 01/01/2024)                                           |
|       | if (Sales, Co-contractor, National, Vehicles) then                       |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 49    | VAT rule 49: (from 01/01/2024)                                           |
|       | if (Purchases, Subject to VAT, National, Services) then                  |
|       | apply 0.22 %                                                             |
|       | and book to VAT deductible                                               |
+-------+--------------------------------------------------------------------------+
| 50    | VAT rule 50: (from 01/01/2024)                                           |
|       | if (Purchases, Subject to VAT, National, Goods at normal VAT rate) then  |
|       | apply 0.22 %                                                             |
|       | and book to VAT deductible                                               |
+-------+--------------------------------------------------------------------------+
| 51    | VAT rule 51: (from 01/01/2024)                                           |
|       | if (Purchases, Subject to VAT, National, Real estate) then               |
|       | apply 0.22 %                                                             |
|       | and book to VAT deductible                                               |
+-------+--------------------------------------------------------------------------+
| 52    | VAT rule 52: (from 01/01/2024)                                           |
|       | if (Purchases, Subject to VAT, National, Vehicles) then                  |
|       | apply 0.22 %                                                             |
|       | and book to VAT deductible                                               |
+-------+--------------------------------------------------------------------------+
| 53    | VAT rule 53: (from 01/01/2024)                                           |
|       | if (Sales, Services) then                                                |
|       | apply 0.22 %                                                             |
|       | and book to VAT due                                                      |
+-------+--------------------------------------------------------------------------+
| 54    | VAT rule 54: (from 01/01/2024)                                           |
|       | if (Sales, Goods at normal VAT rate) then                                |
|       | apply 0.22 %                                                             |
|       | and book to VAT due                                                      |
+-------+--------------------------------------------------------------------------+
| 55    | VAT rule 55: (from 01/01/2024)                                           |
|       | if (Sales, Real estate) then                                             |
|       | apply 0.22 %                                                             |
|       | and book to VAT due                                                      |
+-------+--------------------------------------------------------------------------+
| 56    | VAT rule 56: (from 01/01/2024)                                           |
|       | if (Sales, Vehicles) then                                                |
|       | apply 0.22 %                                                             |
|       | and book to VAT due                                                      |
+-------+--------------------------------------------------------------------------+
| 57    | VAT rule 57: (from 01/01/2025)                                           |
|       | if (Purchases, Intra-community, EU, Goods at reduced VAT rate) then      |
|       | apply 0.13 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 58    | VAT rule 58: (from 01/01/2025)                                           |
|       | if (Sales, Intra-community, EU, Goods at reduced VAT rate) then          |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 59    | VAT rule 59: (from 01/01/2025)                                           |
|       | if (Purchases, Co-contractor, National, Goods at reduced VAT rate) then  |
|       | apply 0.13 %                                                             |
|       | and book to VAT deductible                                               |
|       | (return to VAT returnable)                                               |
+-------+--------------------------------------------------------------------------+
| 60    | VAT rule 60: (from 01/01/2025)                                           |
|       | if (Sales, Co-contractor, National, Goods at reduced VAT rate) then      |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
| 61    | VAT rule 61: (from 01/01/2025)                                           |
|       | if (Purchases, Subject to VAT, National, Goods at reduced VAT rate) then |
|       | apply 0.13 %                                                             |
|       | and book to VAT deductible                                               |
+-------+--------------------------------------------------------------------------+
| 62    | VAT rule 62: (from 01/01/2025)                                           |
|       | if (Sales, Goods at reduced VAT rate) then                               |
|       | apply 0.13 %                                                             |
|       | and book to VAT due                                                      |
+-------+--------------------------------------------------------------------------+
| 63    | VAT rule 63:                                                             |
|       | apply 0 %                                                                |
|       | and book to None                                                         |
+-------+--------------------------------------------------------------------------+
<BLANKLINE>



VAT declaration
===============

.. class:: DeclarationFields

    The list of fields in a VAT declaration.

>>> rt.show(eevat.DeclarationFields)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| value | name | text  | Description                                                                                                                                                                                        |
+=======+======+=======+====================================================================================================================================================================================================+
| 1a    | F1a  | [1a]  | 22% määraga maksustatavad müügid |br|                                                                                                                                                              |
|       |      |       | columns 10 |br|                                                                                                                                                                                    |
|       |      |       | regimes normal subject |br|                                                                                                                                                                        |
|       |      |       | classes goods services |br|                                                                                                                                                                        |
|       |      |       | MvtDeclarationField Credit |br|                                                                                                                                                                    |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 1b    | F1b  | [1b]  | 22% määraga maksustatavad ostud liikmesriigi maksukohustuslaselt |br|                                                                                                                              |
|       |      |       | columns 60 |br|                                                                                                                                                                                    |
|       |      |       | regimes intracom |br|                                                                                                                                                                              |
|       |      |       | classes goods services |br|                                                                                                                                                                        |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 1     | F1   | [1]   | 22% määraga maksustatavad toimingud ja tehingud |br|                                                                                                                                               |
|       |      |       | SumDeclarationField Credit |br|                                                                                                                                                                    |
|       |      |       | = 1a + 1b |br|                                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 2a    | F2a  | [2a]  | 9% määraga maksustatavad müügid |br|                                                                                                                                                               |
|       |      |       | columns 10 |br|                                                                                                                                                                                    |
|       |      |       | regimes normal subject |br|                                                                                                                                                                        |
|       |      |       | classes reduced |br|                                                                                                                                                                               |
|       |      |       | MvtDeclarationField Credit |br|                                                                                                                                                                    |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 2b    | F2b  | [2b]  | 9% määraga maksustatavad ostud liikmesriigi maksukohustuslaselt |br|                                                                                                                               |
|       |      |       | columns 60 |br|                                                                                                                                                                                    |
|       |      |       | regimes intracom |br|                                                                                                                                                                              |
|       |      |       | classes reduced |br|                                                                                                                                                                               |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 2     | F2   | [2]   | 9% määraga maksustatavad toimingud ja tehingud |br|                                                                                                                                                |
|       |      |       | SumDeclarationField Credit |br|                                                                                                                                                                    |
|       |      |       | = 2a + 2b |br|                                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 3     | F3   | [3]   | 0% määraga maksustatavad toimingud ja tehingud, sh |br|                                                                                                                                            |
|       |      |       | columns 10 |br|                                                                                                                                                                                    |
|       |      |       | regimes !normal !subject |br|                                                                                                                                                                      |
|       |      |       | MvtDeclarationField Credit |br|                                                                                                                                                                    |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 31    | F31  | [31]  | 1) kauba ühendusesisene käive ja teise liikmesriigi maksukohustuslasele / piiratud maksukohustuslasele osutatud teenuste käive kokku, sh |br|                                                      |
|       |      |       | columns 10 |br|                                                                                                                                                                                    |
|       |      |       | regimes cocontractor intracom |br|                                                                                                                                                                 |
|       |      |       | MvtDeclarationField Credit |br|                                                                                                                                                                    |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 311   | F311 | [311] | 1) kauba ühendusesisene käive |br|                                                                                                                                                                 |
|       |      |       | columns 10 |br|                                                                                                                                                                                    |
|       |      |       | regimes intracom |br|                                                                                                                                                                              |
|       |      |       | MvtDeclarationField Credit |br|                                                                                                                                                                    |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 32    | F32  | [32]  | 2) kauba eksport, sh |br|                                                                                                                                                                          |
|       |      |       | columns 10 |br|                                                                                                                                                                                    |
|       |      |       | regimes exempt tax_free |br|                                                                                                                                                                       |
|       |      |       | MvtDeclarationField Credit |br|                                                                                                                                                                    |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 321   | F321 | [321] | 1) käibemaksutagastusega müük reisijale |br|                                                                                                                                                       |
|       |      |       | columns 10 |br|                                                                                                                                                                                    |
|       |      |       | regimes tax_free |br|                                                                                                                                                                              |
|       |      |       | MvtDeclarationField Credit |br|                                                                                                                                                                    |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 4     | F4   | [4]   | Käibemaks kokku (22% lahtrist 1 + 9% lahtrist 2) |br|                                                                                                                                              |
|       |      |       | columns 40 |br|                                                                                                                                                                                    |
|       |      |       | MvtDeclarationField Credit |br|                                                                                                                                                                    |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 41    | F41  | [41]  | Impordilt tasumisele kuuluv käibemaks |br|                                                                                                                                                         |
|       |      |       | columns 41 |br|                                                                                                                                                                                    |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 5     | F5   | [5]   | Kokku sisendkäibemaksusumma, mis on seadusega lubatud maha arvata, sh |br|                                                                                                                         |
|       |      |       | columns 50 |br|                                                                                                                                                                                    |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 51    | F51  | [51]  | 1) impordilt tasutud või tasumisele kuuluv käibemaks |br|                                                                                                                                          |
|       |      |       | columns 50 |br|                                                                                                                                                                                    |
|       |      |       | regimes intracom |br|                                                                                                                                                                              |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 52    | F52  | [52]  | 2) põhivara soetamiselt tasutud või tasumisele kuuluv käibemaks |br|                                                                                                                               |
|       |      |       | columns 50 |br|                                                                                                                                                                                    |
|       |      |       | classes real_estate |br|                                                                                                                                                                           |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 53    | F53  | [53]  | 3) ettevõtluses (100%) kasutatava sõiduauto soetamiselt ja sellisesõiduauto tarbeks kaupade soetamiselt ja teenuste saamiselttasutud või tasumisele kuuluv käibemaks |br|                          |
|       |      |       | columns 50 |br|                                                                                                                                                                                    |
|       |      |       | classes vehicles |br|                                                                                                                                                                              |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 54    | F54  | [54]  | 4) osaliselt ettevõtluses kasutatava sõiduauto soetamiselt ja sellisesõiduauto tarbeks kaupade soetamiselt ja teenuste saamiselttasutud või tasumisele kuuluv käibemaks |br|                       |
|       |      |       | columns 50 |br|                                                                                                                                                                                    |
|       |      |       | classes vehicles |br|                                                                                                                                                                              |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 6     | F6   | [6]   | Kauba ühendusesisene soetamine ja teise liikmesriigi maksukohustuslaselt saadud teenused kokku, sh |br|                                                                                            |
|       |      |       | columns 60 |br|                                                                                                                                                                                    |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 61    | F61  | [61]  | 1) kauba ühendusesisene soetamine |br|                                                                                                                                                             |
|       |      |       | columns 60 |br|                                                                                                                                                                                    |
|       |      |       | regimes intracom |br|                                                                                                                                                                              |
|       |      |       | classes goods |br|                                                                                                                                                                                 |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 7     | F7   | [7]   | Muu kauba soetamine ja teenuse saamine, mida maksustatakse käibemaksuga, sh |br|                                                                                                                   |
|       |      |       | columns 60 |br|                                                                                                                                                                                    |
|       |      |       | regimes !intracom |br|                                                                                                                                                                             |
|       |      |       | classes !goods |br|                                                                                                                                                                                |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 71    | F71  | [71]  | 1) erikorra alusel maksustatava kinnisasja, metallijäätmete, väärismetalli ja metalltoodete soetamine (KMS § 41¹) |br|                                                                             |
|       |      |       | columns 60 |br|                                                                                                                                                                                    |
|       |      |       | regimes !intracom |br|                                                                                                                                                                             |
|       |      |       | classes !goods |br|                                                                                                                                                                                |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 8     | F8   | [8]   | Maksuvaba käive |br|                                                                                                                                                                               |
|       |      |       | columns 60 |br|                                                                                                                                                                                    |
|       |      |       | classes exempt |br|                                                                                                                                                                                |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 9     | F9   | [9]   | Erikorra alusel maksustatava kinnisasja, metallijäätmete, väärismetalli ja metalltoodete käive (KMS § 411) ning teises liikmesriigis paigaldatava või kokkupandava kauba maksustatav väärtus |br|  |
|       |      |       | columns 60 |br|                                                                                                                                                                                    |
|       |      |       | classes !goods !real_estate !services !vehicles |br|                                                                                                                                               |
|       |      |       | MvtDeclarationField Debit |br|                                                                                                                                                                     |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 10    | F10  | [10]  | Täpsustused (-) |br|                                                                                                                                                                               |
|       |      |       | WritableDeclarationField Credit |br|                                                                                                                                                               |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 11    | F11  | [11]  | Täpsustused (+) |br|                                                                                                                                                                               |
|       |      |       | WritableDeclarationField Debit |br|                                                                                                                                                                |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 13    | F13  | [13]  | Tasumisele kuuluv(+) või enammakstud (-) käibemaks (lahter 4 + lahter 41 - lahter 5 + lahter 10 - lahter 11) |br|                                                                                  |
|       |      |       | SumDeclarationField Credit |br|                                                                                                                                                                    |
|       |      |       | = 4 + 41 - 5 + 10 - 11 |br|                                                                                                                                                                        |
+-------+------+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
<BLANKLINE>


Available VAT regimes
=====================

For example, when using :mod:`eevat <lino_xl.lib.eevat>` as declaration plugin,
a partner located in Estonia will be in the "national" area,
a partner located in the Netherlands will be in the "EU" area,
and a partner located in the United States will be in the "International" area.


.. >>> print(dd.plugins.countries.country_code)
   EE

>>> ee = countries.Country(isocode='EE')
>>> vat.VatAreas.get_for_country(ee)
<vat.VatAreas.national:10>

>>> list(vat.VatRegimes.get_choices_for_country(ee))
[<vat.VatRegimes.normal:10>, <vat.VatRegimes.subject:20>, <vat.VatRegimes.cocontractor:25>, <vat.VatRegimes.tax_free:40>, <vat.VatRegimes.exempt:60>]

>>> nl = countries.Country(isocode='NL')
>>> vat.VatAreas.get_for_country(nl)
<vat.VatAreas.eu:20>
>>> list(vat.VatRegimes.get_choices_for_country(nl))
[<vat.VatRegimes.normal:10>, <vat.VatRegimes.intracom:30>, <vat.VatRegimes.tax_free:40>, <vat.VatRegimes.exempt:60>]

>>> us = countries.Country(isocode='US')
>>> vat.VatAreas.get_for_country(countries.Country(isocode='US'))
<vat.VatAreas.international:30>
>>> list(vat.VatRegimes.get_choices_for_country(us))
[<vat.VatRegimes.normal:10>, <vat.VatRegimes.tax_free:40>, <vat.VatRegimes.outside:50>, <vat.VatRegimes.exempt:60>]


Intracom
========


>>> rt.show(vat.IntracomSales)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF +ELLIPSIS
===================== =========================== =================== ================= =============== ===== ===============
 Invoice               Partner                     VAT id              VAT regime        TotExcl         VAT   TotIncl
--------------------- --------------------------- ------------------- ----------------- --------------- ----- ---------------
 `SLS 3/2023 <…>`__    Bäckerei Ausdemwald         BE 0322.862.421     Intra-community   1 434,00              1 434,00
 `SLS 4/2023 <…>`__    Bäckerei Mießen             BE 0966.980.726     Intra-community   4 716,79              4 716,79
 `SLS 5/2023 <…>`__    Bäckerei Schmitz            BE 0506.780.656     Intra-community   670,00                670,00
 `SLS 6/2023 <…>`__    Garage Mergelsberg          BE 1773.515.336     Intra-community   582,50                582,50
 `SLS 7/2023 <…>`__    Donderweer BV               NL 928.188.312B01   Intra-community   4 901,55              4 901,55
 `SLS 8/2023 <…>`__    Van Achter NV               NL 593.748.463B01   Intra-community   4 085,42              4 085,42
 `SLS 9/2023 <…>`__    Hans Flott & Co             DE 618.180.575      Intra-community   1 759,71              1 759,71
 `SLS 10/2023 <…>`__   Bernd Brechts Bücherladen   DE 810.753.741      Intra-community   400,00                400,00
 `SLS 11/2023 <…>`__   Reinhards Baumschule        DE 518.719.852      Intra-community   5 094,55              5 094,55
 `SLS 12/2023 <…>`__   Moulin Rouge                FR 40.268.455.901   Intra-community   2 853,73              2 853,73
 `SLS 13/2023 <…>`__   Auto École Verte            FR 75.938.744.403   Intra-community   11,20                 11,20
 **Total (11 rows)**                                                                     **26 509,45**         **26 509,45**
===================== =========================== =================== ================= =============== ===== ===============
<BLANKLINE>


>>> rt.show(vat.IntracomPurchases)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
===================== ===================== =================== ================= =============== ===== ===============
 Invoice               Partner               VAT id              VAT regime        TotExcl         VAT   TotIncl
--------------------- --------------------- ------------------- ----------------- --------------- ----- ---------------
 `PRC 3/2023 <…>`__    Bäckerei Ausdemwald   BE 0322.862.421     Intra-community   603,60                603,60
 `PRC 4/2023 <…>`__    Bäckerei Mießen       BE 0966.980.726     Intra-community   1 199,90              1 199,90
 `PRC 5/2023 <…>`__    Bäckerei Schmitz      BE 0506.780.656     Intra-community   3 241,68              3 241,68
 `PRC 6/2023 <…>`__    Garage Mergelsberg    BE 1773.515.336     Intra-community   143,40                143,40
 `PRC 7/2023 <…>`__    Donderweer BV         NL 928.188.312B01   Intra-community   199,90                199,90
 `PRC 10/2023 <…>`__   Bäckerei Ausdemwald   BE 0322.862.421     Intra-community   602,30                602,30
 ...
 `PRC 33/2024 <…>`__   Bäckerei Schmitz      BE 0506.780.656     Intra-community   3 274,78              3 274,78
 `PRC 34/2024 <…>`__   Garage Mergelsberg    BE 1773.515.336     Intra-community   143,50                143,50
 `PRC 35/2024 <…>`__   Donderweer BV         NL 928.188.312B01   Intra-community   202,50                202,50
 `PRC 38/2024 <…>`__   Bäckerei Ausdemwald   BE 0322.862.421     Intra-community   606,40                606,40
 `PRC 39/2024 <…>`__   Bäckerei Mießen       BE 0966.980.726     Intra-community   1 213,00              1 213,00
 `PRC 40/2024 <…>`__   Bäckerei Schmitz      BE 0506.780.656     Intra-community   3 276,18              3 276,18
 `PRC 41/2024 <…>`__   Garage Mergelsberg    BE 1773.515.336     Intra-community   141,60                141,60
 `PRC 42/2024 <…>`__   Donderweer BV         NL 928.188.312B01   Intra-community   203,00                203,00
 **Total (90 rows)**                                                               **97 305,14**         **97 305,14**
===================== ===================== =================== ================= =============== ===== ===============
<BLANKLINE>






External references
===================

- https://www.emta.ee/et/ariklient/tulu-kulu-kaive-kasum/kaibemaksuseaduse-selgitused/maksustamisperiood-ja
- https://www.riigiteataja.ee/aktilisa/1060/1201/7010/Lisa%201.pdf
- https://www.emta.ee/et/ariklient/tulu-kulu-kaive-kasum/kaibedeklaratsiooni-esitamine/kaibedeklaratsiooni-tehniline

Other languages
===============


>>> rt.show(vat.VatRegimes, language="de")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
====== ============== ======================= =============== =================== ================ ===================
 Wert   name           Text                    MWSt-Zone       Erfordert MwSt-Nr   Reverse charge   Via Peppol senden
------ -------------- ----------------------- --------------- ------------------- ---------------- -------------------
 10     normal         Privatperson                            Nein                Nein             Nein
 20     subject        MwSt.-pflichtig         National        Ja                  Nein             Nein
 25     cocontractor   Vertragspartner         National        Ja                  Ja               Nein
 30     intracom       Innergemeinschaftlich   EU              Ja                  Ja               Nein
 40     tax_free       Tax-free                                Nein                Nein             Nein
 50     outside        Außerhalb EU            International   Nein                Nein             Nein
 60     exempt         Befreit von MwSt.                       Nein                Nein             Nein
====== ============== ======================= =============== =================== ================ ===================
<BLANKLINE>



>>> rt.show(vat.VatClasses, language="et")
======= ============= ============================
 value   nimi          text
------- ------------- ----------------------------
 010     goods         Kaup tavalise KM määraga
 020     reduced       Kaup vähendatud KM määraga
 030     exempt        Kaup ilma käibemaksuta
 100     services      Teenused
 200     investments   Investeeringud
 210     real_estate   Kinnisvara
 220     vehicles      Sõidukid
 300     vatless       ilma käibemaksuta
======= ============= ============================
<BLANKLINE>


>>> rt.show(vat.VatAreas, language="et")
======= =============== ==============
 value   nimi            text
------- --------------- --------------
 10      national        Riiklik
 20      eu              Euroopa Liit
 30      international   Liiduväline
======= =============== ==============
<BLANKLINE>


Returnable VAT
==============

A purchases invoice with :term:`returnable VAT`:

>>> invoice = vat.VatAccountInvoice.objects.filter(vat_regime=vat.VatRegimes.intracom).first()
>>> print(invoice)
PRC 3/2023
>>> rt.show('vat.ItemsByInvoice', invoice)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
================================ ============= ============= ============ ============ =====
 Account                          Description   VCl           TotIncl      TotExcl      VAT
-------------------------------- ------------- ------------- ------------ ------------ -----
 (6010) Purchase of services                    Services      201,20       201,20
 (6020) Purchase of investments                 Investments   402,40       402,40
 **Total (2 rows)**                                           **603,60**   **603,60**
================================ ============= ============= ============ ============ =====
<BLANKLINE>


>>> rt.show('vat.MovementsByVoucher', invoice)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
================================ ===================== ============ ============ ============= ================ =========
 Account                          Partner               Debit        Credit       VAT class     Match            Cleared
-------------------------------- --------------------- ------------ ------------ ------------- ---------------- ---------
 (6010) Purchase of services                            201,20                    Services                       Yes
 (4530) VAT returnable                                               40,24        Services                       Yes
 (4520) VAT deductible                                  40,24                     Services                       Yes
 (6020) Purchase of investments                         402,40                    Investments                    Yes
 (4100) Suppliers                 Bäckerei Ausdemwald                603,60                     **PRC 3/2023**   Yes
                                                        **643,84**   **643,84**
================================ ===================== ============ ============ ============= ================ =========
<BLANKLINE>




>>> print(invoice.total_base)
603.60
>>> print(invoice.total_vat)
0.00
>>> print(invoice.total_incl)
603.60

Note that above is for purchases only. Intra-Community *sales* invoices have no
:term:`returnable VAT` because they don't have any VAT at all:

>>> invoice = rt.models.trading.VatProductInvoice.objects.get(number=4, accounting_period__year__ref='2023')
>>> invoice.vat_regime
<vat.VatRegimes.intracom:30>

>>> rt.show('vat.MovementsByVoucher', invoice)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
================== ================= ============== ============== ======================= ================ =========
 Account            Partner           Debit          Credit         VAT class               Match            Cleared
------------------ ----------------- -------------- -------------- ----------------------- ---------------- ---------
 (7000) Sales                                        11,20          Goods exempt from VAT                    Yes
 (7000) Sales                                        4 705,59       Services                                 Yes
 (4000) Customers   Bäckerei Mießen   4 716,79                                              **SLS 4/2023**   Yes
                                      **4 716,79**   **4 716,79**
================== ================= ============== ============== ======================= ================ =========
<BLANKLINE>



>>> print(invoice.total_base)
4716.79
>>> print(invoice.total_vat)
0.00
>>> print(invoice.total_incl)
4716.79


Invoices covered by a declaration
=================================

The detail view of a :term:`VAT declaration` has two slave tables that show the
invoices covered by this declaration.

>>> obj = eevat.Declaration.objects.get(accounting_period__ref="2024-05")
>>> print(obj)
VAT 5/2024

>>> rt.show(vat.PurchasesByDeclaration, master_instance=obj)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
===================== ===================== =================== ================= ============== =========== ==============
 Invoice               Partner               VAT id              VAT regime        TotExcl        VAT         TotIncl
--------------------- --------------------- ------------------- ----------------- -------------- ----------- --------------
 `PRC 29/2024 <…>`__   Bestbank              EE 255.383.620      Subject to VAT    37,61          3,39        41,00
 `PRC 30/2024 <…>`__   Rumma & Ko OÜ         EE 100.588.749      Subject to VAT    128,63         14,77       143,40
 `PRC 31/2024 <…>`__   Bäckerei Ausdemwald   BE 0322.862.421     Intra-community   608,30                     608,30
 `PRC 32/2024 <…>`__   Bäckerei Mießen       BE 0966.980.726     Intra-community   1 212,50                   1 212,50
 `PRC 33/2024 <…>`__   Bäckerei Schmitz      BE 0506.780.656     Intra-community   3 274,78                   3 274,78
 `PRC 34/2024 <…>`__   Garage Mergelsberg    BE 1773.515.336     Intra-community   143,50                     143,50
 `PRC 35/2024 <…>`__   Donderweer BV         NL 928.188.312B01   Intra-community   202,50                     202,50
 **Total (7 rows)**                                                                **5 607,82**   **18,16**   **5 625,98**
===================== ===================== =================== ================= ============== =========== ==============
<BLANKLINE>


>>> rt.show(vat.SalesByDeclaration, master_instance=obj)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
===================== =============== ======== ================ ============== ============== ===============
 Invoice               Partner         VAT id   VAT regime       TotExcl        VAT            TotIncl
--------------------- --------------- -------- ---------------- -------------- -------------- ---------------
 `SLS 21/2024 <…>`__   Hallik Heli              Private person   1 008,19       221,81         1 230,00
 `SLS 22/2024 <…>`__   Hansen Imre              Private person   4 372,31       932,16         5 304,47
 `SLS 23/2024 <…>`__   Hanson Indrek            Private person   1 515,96       297,85         1 813,81
 `SLS 24/2024 <…>`__   Hein Helju               Private person   1 896,29       414,72         2 311,01
 **Total (4 rows)**                                              **8 792,75**   **1 866,54**   **10 659,29**
===================== =============== ======== ================ ============== ============== ===============
<BLANKLINE>


Here is the content of the fields in the detail of that declaration:

>>> obj.print_declared_values()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
[1a] 22% määraga maksustatavad müügid : 8282.19
[1] 22% määraga maksustatavad toimingud ja tehingud : 8282.19
[2a] 9% määraga maksustatavad müügid : 493.76
[2] 9% määraga maksustatavad toimingud ja tehingud : 493.76
[4] Käibemaks kokku (22% lahtrist 1 + 9% lahtrist 2) : 1866.54
[41] Impordilt tasumisele kuuluv käibemaks : -1088.37
[5] Kokku sisendkäibemaksusumma, mis on seadusega lubatud maha arvata, sh : 1106.53
[51] 1) impordilt tasutud või tasumisele kuuluv käibemaks : 1088.37
[52] 2) põhivara soetamiselt tasutud või tasumisele kuuluv käibemaks : 88.86
[53] 3) ettevõtluses (100%) kasutatava sõiduauto soetamiselt ja sellisesõiduauto tarbeks kaupade soetamiselt ja teenuste saamiselttasutud või tasumisele kuuluv käibemaks : 266.75
[54] 4) osaliselt ettevõtluses kasutatava sõiduauto soetamiselt ja sellisesõiduauto tarbeks kaupade soetamiselt ja teenuste saamiselttasutud või tasumisele kuuluv käibemaks : 266.75
[6] Kauba ühendusesisene soetamine ja teise liikmesriigi maksukohustuslaselt saadud teenused kokku, sh : 1342.53
[7] Muu kauba soetamine ja teenuse saamine, mida maksustatakse käibemaksuga, sh : 67.13
[71] 1) erikorra alusel maksustatava kinnisasja, metallijäätmete, väärismetalli ja metalltoodete soetamine (KMS § 41¹) : 67.13
[8] Maksuvaba käive : 62.90
[9] Erikorra alusel maksustatava kinnisasja, metallijäätmete, väärismetalli ja metalltoodete käive (KMS § 411) ning teises liikmesriigis paigaldatava või kokkupandava kauba maksustatav väärtus : 62.90
[13] Tasumisele kuuluv(+) või enammakstud (-) käibemaks (lahter 4 + lahter 41 - lahter 5 + lahter 10 - lahter 11) : -328.36

And these are the :term:`ledger movements <ledger movement>` generated by our
declaration:

>>> rt.show('accounting.MovementsByVoucher', obj)
======================= ===================== ============== ============== ================ =========
 Account                 Partner               Debit          Credit         Match            Cleared
----------------------- --------------------- -------------- -------------- ---------------- ---------
 (4510) VAT due                                1 866,54                                       Yes
 (4520) VAT deductible                                        1 106,53                        Yes
 (4530) VAT returnable                         1 088,37                                       Yes
 (4500) Tax offices      Maksu- ja Tolliamet                  1 848,38       **VAT 5/2024**   Yes
                                               **2 954,91**   **2 954,91**
======================= ===================== ============== ============== ================ =========
<BLANKLINE>

The 2023-11 VAT declaration has values in both fields 1a and 1b:

>>> obj = eevat.Declaration.objects.get(accounting_period__ref="2023-11")
>>> obj.print_declared_values()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
[1a] 22% määraga maksustatavad müügid : 9400.07
[1b] 22% määraga maksustatavad ostud liikmesriigi maksukohustuslaselt : 1199.90
[1] 22% määraga maksustatavad toimingud ja tehingud : 10599.97
[2a] 9% määraga maksustatavad müügid : 493.76
[2] 9% määraga maksustatavad toimingud ja tehingud : 493.76
[4] Käibemaks kokku (22% lahtrist 1 + 9% lahtrist 2) : 1924.44
[41] Impordilt tasumisele kuuluv käibemaks : -312.98
[5] Kokku sisendkäibemaksusumma, mis on seadusega lubatud maha arvata, sh : 343.20
[51] 1) impordilt tasutud või tasumisele kuuluv käibemaks : 312.98
[52] 2) põhivara soetamiselt tasutud või tasumisele kuuluv käibemaks : 14.89
[53] 3) ettevõtluses (100%) kasutatava sõiduauto soetamiselt ja sellisesõiduauto tarbeks kaupade soetamiselt ja teenuste saamiselttasutud või tasumisele kuuluv käibemaks : 22.29
[54] 4) osaliselt ettevõtluses kasutatava sõiduauto soetamiselt ja sellisesõiduauto tarbeks kaupade soetamiselt ja teenuste saamiselttasutud või tasumisele kuuluv käibemaks : 22.29
[6] Kauba ühendusesisene soetamine ja teise liikmesriigi maksukohustuslaselt saadud teenused kokku, sh : 1328.42
[13] Tasumisele kuuluv(+) või enammakstud (-) käibemaks (lahter 4 + lahter 41 - lahter 5 + lahter 10 - lahter 11) : 1268.26


Here again the ledger movements generated by this declaration:

>>> rt.show('accounting.MovementsByVoucher', obj)
======================= ===================== ============== ============== ================= =========
 Account                 Partner               Debit          Credit         Match             Cleared
----------------------- --------------------- -------------- -------------- ----------------- ---------
 (4510) VAT due                                1 924,44                                        Yes
 (4520) VAT deductible                                        343,20                           Yes
 (4530) VAT returnable                         312,98                                          Yes
 (4500) Tax offices      Maksu- ja Tolliamet                  1 894,22       **VAT 11/2023**   Yes
                                               **2 237,42**   **2 237,42**
======================= ===================== ============== ============== ================= =========
<BLANKLINE>


e-Invoices and PEPPOL
=====================

The following snippet is to test the
:attr:`lino_xl.lib.trading.VatProductInvoice.vat_subtotals` property.

>>> regimes = set()
>>> for obj in trading.VatProductInvoice.objects.filter(journal__make_ledger_movements=True):
...     if obj.vat_regime in regimes: continue
...     regimes.add(obj.vat_regime)
...     print(obj.vat_regime, str(obj), ":")
...     for cat, rule, base, vat in obj.vat_subtotals:
...         print("-", cat, rule.rate, base, vat)
...     print("Total", obj.total_base, obj.total_vat)
Subject to VAT SLS 1/2023 :
- S 0.20 16.67 3.33
Total 16.67 3.33
Intra-community SLS 3/2023 :
- AE 0 1135.00 0.00
- AE 0 299.00 0.00
Total 1434.00 0.00
Private person SLS 14/2023 :
- S 0.20 3546.33 709.26
Total 3546.33 709.26


History
=======

This plugin covers Estonian VAT legislation since 2020 and supports the
following changes:

- Alates 01.01.2024 on Eestis käibemaksu standardmäär 22% senise 20% asemel.
  (`emta.ee <https://www.emta.ee/ariklient/maksud-ja-tasumine/kaibemaks#alates-01012024>`__)

- Alates 01.01.2025 on majutus ja majutus koos hommikusöögiga maksustatud 13%
  käibemaksumääraga senise 9% asemel ning ajakirjandusväljaannete käibemaksumäär
  tõuseb 5%-lt uuesti 9%-le. (`emta.ee
  <https://www.emta.ee/ariklient/maksud-ja-tasumine/kaibemaks#alates-01012025>`__)

..
  >>> dbhash.check_virgin()
