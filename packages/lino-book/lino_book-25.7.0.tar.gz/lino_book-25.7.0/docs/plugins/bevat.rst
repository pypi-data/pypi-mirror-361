.. doctest docs/plugins/bevat.rst
.. _xl.bevat:

====================================
``bevat`` : Belgian VAT declarations
====================================

.. currentmodule:: lino_xl.lib.bevat

The :mod:`lino_xl.lib.bevat` plugin adds functionality for handling **Belgian
VAT declarations**.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *


Dependencies
============

Installing this plugin will automatically install :mod:`lino_xl.lib.vat`.

>>> dd.plugins.bevat.needs_plugins
['lino_xl.lib.vat']


.. _VatClasses.be:

Belgian VAT classes
===================

These are the :term:`VAT classes <VAT class>` used in Belgium:

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
 300     vatless       Without VAT
======= ============= ===========================
<BLANKLINE>

>>> rt.show(vat.VatClasses, language="de")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
====== ============= =================================
 Wert   name          Text
------ ------------- ---------------------------------
 010    goods         Waren mit normalem MWSt-Satz
 020    reduced       Waren mit ermäßigtem  MWSt-Satz
 030    exempt        MWSt-befreite Waren
 100    services      Dienstleistungen
 200    investments   Investierungen
 300    vatless       Ohne Mehrwertsteuer
====== ============= =================================
<BLANKLINE>

>>> rt.show(vat.VatClasses, language="fr")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
====== ============= ==========================
 Wert   name          Text
------ ------------- --------------------------
 010    goods         Biens au taux TVA normal
 020    reduced       Biens au taux TVA réduit
 030    exempt        Biens exemptés de TVA
 100    services      Services
 200    investments   Investissements
 300    vatless       Sans TVA
====== ============= ==========================
<BLANKLINE>



Models and actors reference
===========================

.. class:: Declaration

    Django model to represent a Belgian :term:`VAT declaration`.

    .. method:: write_intracom_statement

      Generate an XML file for the :term:`intra-community statement` attached to
      this VAT declaration.

VAT columns
===========

>>> rt.show(vat.VatColumns, language="en")
======= ========================= ========================= ================================
 value   text                      Common account            Account
------- ------------------------- ------------------------- --------------------------------
 00      Sales basis 0
 01      Sales basis 1
 02      Sales basis 2
 03      Sales basis 3             Sales                     (7000) Sales
 54      VAT due                   VAT due                   (4510) VAT due
 55      VAT returnable            VAT returnable            (4530) VAT returnable
 59      VAT deductible            VAT deductible            (4520) VAT deductible
 81      Purchase of goods         Purchase of goods         (6040) Purchase of goods
 82      Purchase of services      Purchase of services      (6010) Purchase of services
 83      Purchase of investments   Purchase of investments   (6020) Purchase of investments
======= ========================= ========================= ================================
<BLANKLINE>

>>> show_choices('robin', '/choices/accounting/Account/vat_column')
<BLANKLINE>
00 (Sales basis 0)
01 (Sales basis 1)
02 (Sales basis 2)
03 (Sales basis 3)
54 (VAT due)
55 (VAT returnable)
59 (VAT deductible)
81 (Purchase of goods)
82 (Purchase of services)
83 (Purchase of investments)


VAT rules
=========

>>> rt.show(vat.VatRules, language="en")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
+-------+--------------------------------------------------------------------------------+
| value | Description                                                                    |
+=======+================================================================================+
| 1     | VAT rule 1:                                                                    |
|       | if (Exempt) then                                                               |
|       | apply 0 %                                                                      |
|       | and book to None                                                               |
+-------+--------------------------------------------------------------------------------+
| 2     | VAT rule 2:                                                                    |
|       | if (Outside EU) then                                                           |
|       | apply 0 %                                                                      |
|       | and book to None                                                               |
+-------+--------------------------------------------------------------------------------+
| 3     | VAT rule 3:                                                                    |
|       | if (Profit margin regime) then                                                 |
|       | apply 0 %                                                                      |
|       | and book to None                                                               |
+-------+--------------------------------------------------------------------------------+
| 4     | VAT rule 4:                                                                    |
|       | if (Purchases, Intra-community, EU, 010 (Goods at normal VAT rate)) then       |
|       | apply 0.21 %                                                                   |
|       | and book to VAT deductible                                                     |
|       | (return to VAT returnable)                                                     |
+-------+--------------------------------------------------------------------------------+
| 5     | VAT rule 5:                                                                    |
|       | if (Sales, Intra-community, EU, 010 (Goods at normal VAT rate)) then           |
|       | apply 0 %                                                                      |
|       | and book to None                                                               |
+-------+--------------------------------------------------------------------------------+
| 6     | VAT rule 6:                                                                    |
|       | if (Purchases, Co-contractor, National, 010 (Goods at normal VAT rate)) then   |
|       | apply 0.21 %                                                                   |
|       | and book to VAT deductible                                                     |
|       | (return to VAT returnable)                                                     |
+-------+--------------------------------------------------------------------------------+
| 7     | VAT rule 7:                                                                    |
|       | if (Sales, Co-contractor, National, 010 (Goods at normal VAT rate)) then       |
|       | apply 0 %                                                                      |
|       | and book to None                                                               |
+-------+--------------------------------------------------------------------------------+
| 8     | VAT rule 8:                                                                    |
|       | if (Purchases, Intra-community, EU, 020 (Goods at reduced VAT rate)) then      |
|       | apply 0.12 %                                                                   |
|       | and book to VAT deductible                                                     |
|       | (return to VAT returnable)                                                     |
+-------+--------------------------------------------------------------------------------+
| 9     | VAT rule 9:                                                                    |
|       | if (Sales, Intra-community, EU, 020 (Goods at reduced VAT rate)) then          |
|       | apply 0 %                                                                      |
|       | and book to None                                                               |
+-------+--------------------------------------------------------------------------------+
| 10    | VAT rule 10:                                                                   |
|       | if (Purchases, Co-contractor, National, 020 (Goods at reduced VAT rate)) then  |
|       | apply 0.12 %                                                                   |
|       | and book to VAT deductible                                                     |
|       | (return to VAT returnable)                                                     |
+-------+--------------------------------------------------------------------------------+
| 11    | VAT rule 11:                                                                   |
|       | if (Sales, Co-contractor, National, 020 (Goods at reduced VAT rate)) then      |
|       | apply 0 %                                                                      |
|       | and book to None                                                               |
+-------+--------------------------------------------------------------------------------+
| 12    | VAT rule 12:                                                                   |
|       | if (Purchases, Intra-community, EU, 100 (Services)) then                       |
|       | apply 0.21 %                                                                   |
|       | and book to VAT deductible                                                     |
|       | (return to VAT returnable)                                                     |
+-------+--------------------------------------------------------------------------------+
| 13    | VAT rule 13:                                                                   |
|       | if (Sales, Intra-community, EU, 100 (Services)) then                           |
|       | apply 0 %                                                                      |
|       | and book to None                                                               |
+-------+--------------------------------------------------------------------------------+
| 14    | VAT rule 14:                                                                   |
|       | if (Purchases, Co-contractor, National, 100 (Services)) then                   |
|       | apply 0.21 %                                                                   |
|       | and book to VAT deductible                                                     |
|       | (return to VAT returnable)                                                     |
+-------+--------------------------------------------------------------------------------+
| 15    | VAT rule 15:                                                                   |
|       | if (Sales, Co-contractor, National, 100 (Services)) then                       |
|       | apply 0 %                                                                      |
|       | and book to None                                                               |
+-------+--------------------------------------------------------------------------------+
| 16    | VAT rule 16:                                                                   |
|       | if (Purchases, Intra-community, EU, 200 (Investments)) then                    |
|       | apply 0.21 %                                                                   |
|       | and book to VAT deductible                                                     |
|       | (return to VAT returnable)                                                     |
+-------+--------------------------------------------------------------------------------+
| 17    | VAT rule 17:                                                                   |
|       | if (Sales, Intra-community, EU, 200 (Investments)) then                        |
|       | apply 0 %                                                                      |
|       | and book to None                                                               |
+-------+--------------------------------------------------------------------------------+
| 18    | VAT rule 18:                                                                   |
|       | if (Purchases, Co-contractor, National, 200 (Investments)) then                |
|       | apply 0.21 %                                                                   |
|       | and book to VAT deductible                                                     |
|       | (return to VAT returnable)                                                     |
+-------+--------------------------------------------------------------------------------+
| 19    | VAT rule 19:                                                                   |
|       | if (Sales, Co-contractor, National, 200 (Investments)) then                    |
|       | apply 0 %                                                                      |
|       | and book to None                                                               |
+-------+--------------------------------------------------------------------------------+
| 20    | VAT rule 20:                                                                   |
|       | if (Purchases, Subject to VAT, National, 010 (Goods at normal VAT rate)) then  |
|       | apply 0.21 %                                                                   |
|       | and book to VAT deductible                                                     |
+-------+--------------------------------------------------------------------------------+
| 21    | VAT rule 21:                                                                   |
|       | if (Purchases, Subject to VAT, National, 020 (Goods at reduced VAT rate)) then |
|       | apply 0.12 %                                                                   |
|       | and book to VAT deductible                                                     |
+-------+--------------------------------------------------------------------------------+
| 22    | VAT rule 22:                                                                   |
|       | if (Purchases, Subject to VAT, National, 100 (Services)) then                  |
|       | apply 0.21 %                                                                   |
|       | and book to VAT deductible                                                     |
+-------+--------------------------------------------------------------------------------+
| 23    | VAT rule 23:                                                                   |
|       | if (Purchases, Subject to VAT, National, 200 (Investments)) then               |
|       | apply 0.21 %                                                                   |
|       | and book to VAT deductible                                                     |
+-------+--------------------------------------------------------------------------------+
| 24    | VAT rule 24:                                                                   |
|       | if (Sales, 010 (Goods at normal VAT rate)) then                                |
|       | apply 0.21 %                                                                   |
|       | and book to VAT due                                                            |
+-------+--------------------------------------------------------------------------------+
| 25    | VAT rule 25:                                                                   |
|       | if (Sales, 020 (Goods at reduced VAT rate)) then                               |
|       | apply 0.12 %                                                                   |
|       | and book to VAT due                                                            |
+-------+--------------------------------------------------------------------------------+
| 26    | VAT rule 26:                                                                   |
|       | if (Sales, 100 (Services)) then                                                |
|       | apply 0.21 %                                                                   |
|       | and book to VAT due                                                            |
+-------+--------------------------------------------------------------------------------+
| 27    | VAT rule 27:                                                                   |
|       | if (Sales, 200 (Investments)) then                                             |
|       | apply 0.21 %                                                                   |
|       | and book to VAT due                                                            |
+-------+--------------------------------------------------------------------------------+
| 28    | VAT rule 28:                                                                   |
|       | apply 0 %                                                                      |
|       | and book to None                                                               |
+-------+--------------------------------------------------------------------------------+
<BLANKLINE>



e-Invoices and PEPPOL
=====================

The following snippet is to test the
:attr:`lino_xl.lib.trading.VatProductInvoice.vat_subtotals` property, which is
used in :xfile:`config/vat/peppol-ubl.xml`.

>>> regimes = set()
>>> for obj in trading.VatProductInvoice.objects.filter(journal__make_ledger_movements=True):
...     if obj.vat_regime in regimes: continue
...     regimes.add(obj.vat_regime)
...     print(obj.vat_regime, str(obj), ":")
...     for cat, rule, base, vat in obj.vat_subtotals:
...         print("-", cat, rule.rate, base, vat)
...     print("Total", obj.total_base, obj.total_vat)
Subject to VAT SLS 1/2023 :
- S 0.21 2999.85 629.97
Total 2999.85 629.97
Intra-community SLS 2/2023 :
- AE 0 2039.82 0.00
Total 2039.82 0.00
Private person SLS 14/2023 :
- S 0.21 831.82 174.68
Total 831.82 174.68


VAT declaration
===============

.. class:: DeclarationFields

    The list of fields in a VAT declaration.

>>> rt.show(bevat.DeclarationFields, language="de")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
+------+------+------+-------------------------------------------------+
| Wert | name | Text | Beschreibung                                    |
+======+======+======+=================================================+
| 00   | F00  | [00] | Verkauf |br|                                    |
|      |      |      | columns 00 |br|                                 |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| 01   | F01  | [01] | Verkauf |br|                                    |
|      |      |      | columns 01 |br|                                 |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| 02   | F02  | [02] | Sales 12% |br|                                  |
|      |      |      | columns 02 |br|                                 |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| 03   | F03  | [03] | Sales 21% |br|                                  |
|      |      |      | columns 03 |br|                                 |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| 44   | F44  | [44] | Sales located inside EU |br|                    |
|      |      |      | columns 00 01 02 03 |br|                        |
|      |      |      | regimes inside |br|                             |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| 45   | F45  | [45] | Vertragspartner |br|                            |
|      |      |      | columns 00 01 02 03 |br|                        |
|      |      |      | regimes cocontractor |br|                       |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| 46   | F46  | [46] | Sales intracom and ABC |br|                     |
|      |      |      | columns 00 01 02 03 |br|                        |
|      |      |      | regimes intracom |br|                           |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| 47   | F47  | [47] | Verkauf |br|                                    |
|      |      |      | columns 00 01 02 03 |br|                        |
|      |      |      | regimes intracom |br|                           |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| 48   | F48  | [48] | CN sales 48 |br|                                |
|      |      |      | columns 00 01 02 03 |br|                        |
|      |      |      | MvtDeclarationField Debit |br|                  |
+------+------+------+-------------------------------------------------+
| 49   | F49  | [49] | CN sales 49 |br|                                |
|      |      |      | columns 00 01 02 03 |br|                        |
|      |      |      | MvtDeclarationField Debit |br|                  |
+------+------+------+-------------------------------------------------+
| 81   | F81  | [81] | Lebenslauf |br|                                 |
|      |      |      | columns 81 |br|                                 |
|      |      |      | MvtDeclarationField Debit |br|                  |
+------+------+------+-------------------------------------------------+
| 82   | F82  | [82] | Dienstleistungen |br|                           |
|      |      |      | columns 82 |br|                                 |
|      |      |      | MvtDeclarationField Debit |br|                  |
+------+------+------+-------------------------------------------------+
| 83   | F83  | [83] | Investierungen |br|                             |
|      |      |      | columns 83 |br|                                 |
|      |      |      | MvtDeclarationField Debit |br|                  |
+------+------+------+-------------------------------------------------+
| 84   | F84  | [84] | CN purchases on operations in 86 and 88 |br|    |
|      |      |      | columns 81 82 83 |br|                           |
|      |      |      | regimes intracom |br|                           |
|      |      |      | MvtDeclarationField Kredit only |br|            |
+------+------+------+-------------------------------------------------+
| 85   | F85  | [85] | CN purchases on other operations |br|           |
|      |      |      | columns 81 82 83 |br|                           |
|      |      |      | regimes !delayed !intracom |br|                 |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| 86   | F86  | [86] | IC purchases and ABC sales |br|                 |
|      |      |      | columns 81 82 83 |br|                           |
|      |      |      | regimes intracom |br|                           |
|      |      |      | MvtDeclarationField Debit |br|                  |
+------+------+------+-------------------------------------------------+
| 87   | F87  | [87] | Other purchases in Belgium |br|                 |
|      |      |      | columns 81 82 83 |br|                           |
|      |      |      | regimes cocontractor |br|                       |
|      |      |      | MvtDeclarationField Debit |br|                  |
+------+------+------+-------------------------------------------------+
| 88   | F88  | [88] | IC services |br|                                |
|      |      |      | columns 81 82 83 |br|                           |
|      |      |      | regimes delayed |br|                            |
|      |      |      | MvtDeclarationField Debit |br|                  |
+------+------+------+-------------------------------------------------+
| 54   | F54  | [54] | Due VAT for 01, 02 and 03 |br|                  |
|      |      |      | columns 54 |br|                                 |
|      |      |      | regimes !cocontractor !delayed !intracom |br|   |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| 55   | F55  | [55] | Due VAT for 86 and 88 |br|                      |
|      |      |      | columns 54 |br|                                 |
|      |      |      | regimes intracom |br|                           |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| 56   | F56  | [56] | Due VAT for 87 except those covered by 57 |br|  |
|      |      |      | columns 54 |br|                                 |
|      |      |      | regimes cocontractor |br|                       |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| 57   | F57  | [57] | Due VAT for 87 except those covered by 57 |br|  |
|      |      |      | columns 54 |br|                                 |
|      |      |      | regimes delayed |br|                            |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| 61   | F61  | [61] | Diverse Buchungen |br|                          |
|      |      |      | WritableDeclarationField Kredit |br|            |
+------+------+------+-------------------------------------------------+
| XX   | FXX  | [XX] | Total of due taxes |br|                         |
|      |      |      | SumDeclarationField Kredit |br|                 |
|      |      |      | = 54 + 55 + 56 + 57 |br|                        |
+------+------+------+-------------------------------------------------+
| 59   | F59  | [59] | Deductible VAT from purchase invoices |br|      |
|      |      |      | columns 59 |br|                                 |
|      |      |      | MvtDeclarationField Kredit |br|                 |
|      |      |      | = 81 + 82 + 83 |br|                             |
+------+------+------+-------------------------------------------------+
| 62   | F62  | [62] | Diverse Buchungen |br|                          |
|      |      |      | WritableDeclarationField Kredit |br|            |
+------+------+------+-------------------------------------------------+
| 64   | F64  | [64] | VAT on sales CN |br|                            |
|      |      |      | columns 59 |br|                                 |
|      |      |      | MvtDeclarationField Kredit |br|                 |
+------+------+------+-------------------------------------------------+
| YY   | FYY  | [YY] | Total of deductible taxes |br|                  |
|      |      |      | SumDeclarationField Kredit |br|                 |
|      |      |      | = 59 + 62 + 64 |br|                             |
+------+------+------+-------------------------------------------------+
| 72   | F72  | [72] | Total to pay (+) or to return (-) |br|          |
|      |      |      | SumDeclarationField Debit |br|                  |
|      |      |      | = XX + YY |br|                                  |
+------+------+------+-------------------------------------------------+
<BLANKLINE>


.. _dg.plugins.bevat.intracom_statement_iterator:

Intra-community clients
=======================

Usage example of
:meth:`lino_xl.lib.vat.VatDeclaration.intracom_statement_iterator` method:

>>> for dcl in bevat.Declaration.objects.all():
...     for p in dcl.intracom_statement_iterator():
...         print(f"{dcl} {p} : {p.total_base:.2f}")
VAT 1/2023 Rumma & Ko OÜ : 2039.82
VAT 2/2023 Donderweer BV : 1499.85
VAT 2/2023 Van Achter NV : 1939.82
VAT 2/2023 Hans Flott & Co : 815.96
VAT 3/2023 Bernd Brechts Bücherladen : 320.00
VAT 4/2023 Reinhards Baumschule : 548.50
VAT 4/2023 Moulin Rouge : 2013.88
VAT 4/2023 Auto École Verte : 1949.85
VAT 7/2024 AS Express Post : 2359.78
VAT 8/2024 AS Matsalu Veevärk : 59.85
VAT 8/2024 Eesti Energia AS : 580.00
VAT 8/2024 IIZI kindlustusmaakler AS : 834.00
VAT 8/2024 Maksu- ja Tolliamet : 11.20
VAT 8/2024 Ragn-Sells AS : 4255.59
VAT 10/2024 Rumma & Ko OÜ : 2140.50
VAT 12/2024 Donderweer BV : 489.20
VAT 12/2024 Van Achter NV : 5045.27
VAT 12/2024 Hans Flott & Co : 379.81
VAT 12/2024 Bernd Brechts Bücherladen : 740.00
VAT 1/2025 Reinhards Baumschule : 375.00
VAT 1/2025 Moulin Rouge : 310.20
VAT 1/2025 Auto École Verte : 3599.71



External references
===================

- `Notice pour la rédaction des déclarations périodiques à la TVA 2016
  <https://finances.belgium.be/sites/default/files/downloads/165-625-directives-2016.pdf>`__
