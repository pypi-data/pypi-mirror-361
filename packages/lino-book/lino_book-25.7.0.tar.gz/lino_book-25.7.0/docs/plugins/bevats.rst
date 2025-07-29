.. doctest docs/specs/bevats.rst
.. _xl.bevats:

================================================
``bevats`` : Simplified Belgian VAT declarations
================================================

.. currentmodule:: lino_xl.lib.bevats

The :mod:`lino_xl.lib.bevats` plugin adds functionality for handling
**Special** Belgian VAT declarations to be used by organizations who don't need
to introduce "normal" VAT declarations (:doc:`bevat`) but may declare only
purchases. See e.g. `here
<https://finances.belgium.be/fr/entreprises/tva/declaration/declaration_speciale>`__.


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.tera1.settings')
>>> from lino.api.doctest import *

Dependencies
============

Installing this plugin will automatically install
:mod:`lino_xl.lib.vat`.

>>> dd.plugins.bevats.needs_plugins
['lino_xl.lib.vat']

The choice lists for VAT regimes and VAT columns are reduced compared
to those defined in :doc:`bevat`:

>>> rt.show('vat.VatRegimes')
======= =============== ==================== ========== ============== ================ =============
 value   name            text                 VAT area   Needs VAT id   Reverse charge   Send Peppol
------- --------------- -------------------- ---------- -------------- ---------------- -------------
 10      normal          Not subject to VAT              No             No               No
 20      subject         Subject to VAT       National   Yes            No               No
 30      intracom        Intracom services    EU         Yes            Yes              No
 35      intracom_supp   Intracom supplies    EU         Yes            Yes              No
======= =============== ==================== ========== ============== ================ =============
<BLANKLINE>


>>> rt.show('vat.VatColumns')
======= ============================== ========================= ================================
 value   text                           Common account            Account
------- ------------------------------ ------------------------- --------------------------------
 54      VAT due                        VAT due                   (4510) VAT due
 55      VAT returnable                 VAT returnable            (4530) VAT returnable
 59      VAT deductible                 VAT deductible            (4520) VAT deductible
 71      Purchase of ware               Purchase of goods         (6040) Purchase of goods
 72      Purchase of new vehicles       Purchase of investments   (6020) Purchase of investments
 73      Purchase of excised products
 75      Purchase of services           Purchase of services      (6010) Purchase of services
 76      Other purchase
======= ============================== ========================= ================================
<BLANKLINE>



>>> rt.show('bevats.DeclarationFields')  #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF +ELLIPSIS
+-------+------+------+--------------------------------------------+
| value | name | text | Description                                |
+=======+======+======+============================================+
| 71    | F71  | [71] | Intracom supplies |br|                     |
|       |      |      | columns 71 |br|                            |
|       |      |      | MvtDeclarationField Debit |br|             |
+-------+------+------+--------------------------------------------+
| 72    | F72  | [72] | New vehicles |br|                          |
|       |      |      | columns 72 |br|                            |
|       |      |      | MvtDeclarationField Debit |br|             |
+-------+------+------+--------------------------------------------+
| 73    | F73  | [73] | Excised products |br|                      |
|       |      |      | columns 73 |br|                            |
|       |      |      | MvtDeclarationField Debit |br|             |
+-------+------+------+--------------------------------------------+
| 75    | F75  | [75] | Intracom services |br|                     |
|       |      |      | columns 75 |br|                            |
|       |      |      | MvtDeclarationField Debit |br|             |
+-------+------+------+--------------------------------------------+
| 76    | F76  | [76] | Other operations |br|                      |
|       |      |      | columns 76 |br|                            |
|       |      |      | MvtDeclarationField Debit |br|             |
+-------+------+------+--------------------------------------------+
| 77    | F77  | [77] | Credit notes on 71, 72, 73 and 75 |br|     |
|       |      |      | columns 71 72 73 75 |br|                   |
|       |      |      | MvtDeclarationField Credit only |br|       |
+-------+------+------+--------------------------------------------+
| 78    | F78  | [78] | Credit notes on 76 |br|                    |
|       |      |      | columns 76 |br|                            |
|       |      |      | MvtDeclarationField Debit only |br|        |
+-------+------+------+--------------------------------------------+
| 80    | F80  | [80] | Due VAT for 71...76 |br|                   |
|       |      |      | columns 54 |br|                            |
|       |      |      | MvtDeclarationField Credit |br|            |
+-------+------+------+--------------------------------------------+
| 81    | F81  | [81] | Miscellaneous corrections due |br|         |
|       |      |      | WritableDeclarationField Credit |br|       |
+-------+------+------+--------------------------------------------+
| 82    | F82  | [82] | Miscellaneous corrections returnable |br|  |
|       |      |      | WritableDeclarationField Debit |br|        |
+-------+------+------+--------------------------------------------+
| 83    | F83  | [83] | Total to pay (+) or to return (-) |br|     |
|       |      |      | SumDeclarationField Credit |br|            |
|       |      |      | = 80 + 81 + 82 |br|                        |
+-------+------+------+--------------------------------------------+
<BLANKLINE>


Intra-community purchases
=========================

When an organizations with special VAT buys goods or services from other EU
member states, the provider does not write any VAT on their invoice. But the
organization computes that VAT for their VAT declaration based on their
national rate and declares it as due to the VAT office of their own country.

Here is an example of such an invoice:

>>> qs = ana.AnaAccountInvoice.objects.filter(vat_regime=vat.VatRegimes.intracom)
>>> obj = qs[0]
>>> print(obj)
PRC 2/2015

How the data has been entered:

>>> rt.show(ana.ItemsByInvoice, obj)
================================ ============= ==================== =========================== ============== ===== ==============
 Account                          Description   Analytical account   VCl                         TotExcl        VAT   TotIncl
-------------------------------- ------------- -------------------- --------------------------- -------------- ----- --------------
 (6020) Purchase of investments                 (1200) Transport     Goods at reduced VAT rate   60,4000              60,4000
 (6040) Purchase of goods                       (1300) Training      Goods exempt from VAT       80,9000              80,9000
 **Total (2 rows)**                                                                              **141,3000**         **141,3000**
================================ ============= ==================== =========================== ============== ===== ==============
<BLANKLINE>

Note that no VAT amounts are shown in the VAT column.  Because these amounts are
not shown on the invoice.  Also the invoice's totals don't show any VAT:

>>> print(obj.total_base)
141.30
>>> print(obj.total_vat)
0.00
>>> print(obj.total_incl)
141.30

The VAT appears only in the generated movements:

>>> rt.show(accounting.MovementsByVoucher, obj)
================================ =============== ============ ============ ================ =========
 Account                          Partner         Debit        Credit       Match            Cleared
-------------------------------- --------------- ------------ ------------ ---------------- ---------
 (6020) Purchase of investments                   64,63                                      Yes
 (4510) VAT due                                                4,23                          Yes
 (6040) Purchase of goods                         80,90                                      Yes
 (4100) Suppliers                 Rumma & Ko OÜ                141,30       **PRC 2/2015**   Yes
                                                  **145,53**   **145,53**
================================ =============== ============ ============ ================ =========
<BLANKLINE>


The movements show that we had actually **48,40 €** of costs, **40 €** of
which are due to the supplier and **8,40 €** due to the tax office. The amount
of the costs account (here 6010) has increased by **8,40 €** from 40,00 to 48,40.

Now let's look at how this invoice shows in the VAT declaration.

Our invoice is in January 2015.

>>> print(obj.entry_date)
2015-01-04

>>> obj.accounting_period
StoredPeriod #1 ('2015-01')

At the end of the month they have several such invoices and we must declare the
sum of their VAT to the tax office. Here are the VAT declarations in our demo
database:

>>> jnl = rt.models.accounting.Journal.get_by_ref('VAT')
>>> rt.show('bevats.DeclarationsByJournal', jnl)
==================== ============ ============== ============ =================== ============ ====== ====== ============ ================
 No.                  Date         Start period   End period   Accounting period   [80]         [81]   [82]   [83]         Workflow
-------------------- ------------ -------------- ------------ ------------------- ------------ ------ ------ ------------ ----------------
 1/2015               31/01/2015   2015-01                     2015-01             46,21                      46,21        **Registered**
 2/2015               28/02/2015   2015-02                     2015-02             42,11                      42,11        **Registered**
 3/2015               28/03/2015   2015-03                     2015-03             17,28                      17,28        **Registered**
 **Total (3 rows)**                                                                **105,60**                 **105,60**
==================== ============ ============== ============ =================== ============ ====== ====== ============ ================
<BLANKLINE>

There is usually one declaration per accounting period.
Let's look at the declaration of our period.

>>> dcl = rt.models.bevats.Declaration.objects.get(accounting_period=obj.accounting_period)

On screen you can see:

>>> dcl.print_declared_values()
[71] Intracom supplies : 1337.90
[72] New vehicles : 742.88
[75] Intracom services : 3482.22
[80] Due VAT for 71...76 : 46.21
[83] Total to pay (+) or to return (-) : 46.21

When you print the declaration, Lino also includes the :class:`IntracomPurchases
<lino_xl.lib.vat.IntracomPurchases>` table for the declared accounting period:

>>> pv = dict(start_period=dcl.start_period, end_period=dcl.end_period)
>>> rt.show(vat.IntracomPurchases, param_values=pv, header_level=2)
-----------------------------------
Intra-Community purchases (2015-01)
-----------------------------------
==================== =============== =================== =================== ============ ===== ============
 Invoice              Partner         VAT id              VAT regime          TotExcl      VAT   TotIncl
-------------------- --------------- ------------------- ------------------- ------------ ----- ------------
 `PRC 2/2015 <…>`__   Rumma & Ko OÜ   EE 100.588.749      Intracom services   141,30             141,30
 `PRC 7/2015 <…>`__   Donderweer BV   NL 928.188.312B01   Intracom services   199,90             199,90
 **Total (2 rows)**                                                           **341,20**         **341,20**
==================== =============== =================== =================== ============ ===== ============
<BLANKLINE>

And these are the movements generated by our declaration:

>>> rt.show('accounting.MovementsByVoucher', dcl)
==================== ================================== =========== =========== ================ =========
 Account              Partner                            Debit       Credit      Match            Cleared
-------------------- ---------------------------------- ----------- ----------- ---------------- ---------
 (4510) VAT due                                          46,21                                    Yes
 (4500) Tax offices   Mehrwertsteuer-Kontrollamt Eupen               46,21       **VAT 1/2015**   Yes
                                                         **46,21**   **46,21**
==================== ================================== =========== =========== ================ =========
<BLANKLINE>

A declaration in general moves the sum of all those little amounts of due VAT in
account 4510 into another account, which means that now we have no more due VAT
*to declare* but now we have it as a *debt towards the tax office*.  From that
point on a VAT declaration behaves and is handled like a purchase invoice that
needs to get paid in time. That will be described in :doc:`finan`.

We can verify that the VAT declaration did the correct sum by looking at the
history of 4510 for that month:

>>> acc = accounting.Account.get_by_ref("4510")
>>> rt.show(accounting.MovementsByAccount, acc,
...     param_values=dict(start_period=obj.accounting_period))
============ ==================== ========================================== =========== =========== =======
 Value date   Voucher              Description                                Debit       Credit      Match
------------ -------------------- ------------------------------------------ ----------- ----------- -------
 31/01/2015   `VAT 1/2015 <…>`__   `Mehrwertsteuer-Kontrollamt Eupen <…>`__   46,21
 09/01/2015   `PRC 7/2015 <…>`__   `Donderweer BV <…>`__                                  41,98
 04/01/2015   `PRC 2/2015 <…>`__   `Rumma & Ko OÜ <…>`__                                  4,23
                                   **Balance 0.00 (3 movements)**             **46,21**   **46,21**
============ ==================== ========================================== =========== =========== =======
<BLANKLINE>

e-Invoices and PEPPOL
=====================

The following snippet is to test the
:attr:`lino_xl.lib.trading.VatProductInvoice.vat_subtotals` property, which is
used in the :xfile:`vat/peppol-ubl.xml` template.

>>> regimes = set()
>>> for obj in trading.VatProductInvoice.objects.filter(journal__make_ledger_movements=True):
...     if obj.vat_regime in regimes: continue
...     regimes.add(obj.vat_regime)
...     print(obj.vat_regime, str(obj), ":")
...     for cat, rule, base, vat in obj.vat_subtotals:
...         print("-", cat, rule.rate, base, vat)
...     print("Total", obj.total_base, obj.total_vat)
Subject to VAT SLS 1/2015 :
- S 0 225.00 0.00
Total 225.00 0.00
Intracom services SLS 2/2015 :
- AE 0 460.00 0.00
Total 460.00 0.00
Not subject to VAT SLS 14/2015 :
- S 0 460.00 0.00
Total 460.00 0.00


Reference
=========

.. class:: Declaration

    Implements :class:`lino_xl.lib.vat.VatDeclaration`.


.. class:: DeclarationFields

    Implements :class:`lino_xl.lib.vat.DeclarationFields`.
