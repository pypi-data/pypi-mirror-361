.. doctest docs/specs/sheets.rst
.. _xl.specs.sheets:

===============================================
``sheets`` : Balance sheet and Income statement
===============================================

.. currentmodule:: lino_xl.lib.sheets

The :mod:`lino_xl.lib.sheets` plugin adds an annual financial report: three
types of account balances (general, partner and analytical) as well as the
*Balance sheet* and the *Income statement*.

You should have read :doc:`accounting` before reading this document.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.tera1.settings')
>>> from lino.api.doctest import *
>>> ses = rt.login("robin")
>>> translation.activate('en')
>>> from lino_xl.lib.accounting.choicelists import DC


Vocabulary
==========


.. glossary::

  asset

    Anything of value that you *own* and that can be expressed as a monetary
    value. For example the money in your cash drawer, a positive balance on your
    bank account, a computer, a car, a house,

    An asset might generate revenue, or you might benefit in some way from
    owning or using the asset.

  liability

    An amount of money that you *owe* to somebody else.

  revenue

    The money you get for your business activity, e.g. for the sale of your
    products and services.

  expense

    The cost of doing business.  For example the rent you pay for your office
    room, the salaries you pay to your employees, office supplies and coffee you
    consume while working, ...

  capital

    The money given to your business by your investors.

  ownership equity

    The amount of the business assets owned by the business owner.

.. _xl.specs.sheets.accounting_eq:


The Accounting Equation
=======================

The basic `Accounting Equation
<https://en.wikipedia.org/wiki/Accounting_equation>`_ states:

  Assets = Liabilities + Capital

And the expanded accounting equation is:

    Assets **+ Expenses** = Liabilities + Equity **+ Revenue**

Accounts on the left side of the equation (Assets and Expenses) are
normally DEBITed and have DEBIT balances.  That's what the :attr:`dc
<CommonItem.dc>` attribute means:

>>> print(sheets.CommonItems.assets.dc)
Debit
>>> print(sheets.CommonItems.expenses.dc)
Debit

`Wikipedia <http://en.wikipedia.org/wiki/Debits_and_credits>`_ gives a
Summary table of standard increasing and decreasing attributes for the
five accounting elements:

============= ===== ======
ACCOUNT TYPE  DEBIT CREDIT
============= ===== ======
Asset         \+    \−
Liability     \−    \+
Income        \−    \+
Expense       \+    \−
Equity        \−     \+
============= ===== ======

The equivalent in Lino is:

>>> for t in sheets.CommonItems.get_list_items():
... #doctest: +NORMALIZE_WHITESPACE
...   if len(t.value) <= 2:
...     print("%-2s|%-15s|%-6s" % (t.value, t, t.dc))
1 |Assets         |Debit
10|Current assets |Debit
11|Non-current assets|Debit
2 |Passiva        |Credit
20|Liabilities    |Credit
21|Own capital    |Credit
4 |Commercial assets & liabilities|Credit
5 |Financial assets & liabilities|Credit
6 |Expenses       |Debit
60|Operation costs|Debit
62|Wages          |Debit
7 |Revenues       |Credit


TODO: the following tests aren't yet very meaningful, we must first
automatically generate the profit/loss booking (:ticket:`3476`) so that the
expenses and revenues are balanced.

>>> rpt = sheets.Report.objects.get(pk=1)
>>> def getval(ci):
...     try:
...         e = sheets.ItemEntry.objects.get(report=rpt, item=ci.get_object())
...     except sheets.ItemEntry.DoesNotExist:
...         return 0
...     return e.new_balance().value(e.item.dc)

>>> assets = getval(sheets.CommonItems.assets)
>>> liabilities = getval(sheets.CommonItems.liabilities)
>>> capital = getval(sheets.CommonItems.capital)
>>> passiva = getval(sheets.CommonItems.passiva)
>>> expenses = getval(sheets.CommonItems.expenses)
>>> revenues = getval(sheets.CommonItems.revenues)

>>> print(assets)
19098.19
>>> print(liabilities)
5572.28
>>> print(capital)  #doctest: +SKIP
-9354.40
>>> print(liabilities+capital)  #doctest: +SKIP
13836.75
>>> print(passiva)  #doctest: +SKIP
13836.75
>>> print(expenses)
26094.33
>>> print(revenues)  #doctest: +SKIP
24518.54




Types of accounting sheets
==========================

.. glossary::

  balance sheet

    A summary of the financial balances of an organisation. Also called a
    *statement of financial position*.

    :term:`Assets <asset>`, :term:`liabilities <liability>` and ownership
    equity are listed as of a specific date, such as the end of its
    financial year.  A balance sheet is often described as a "snapshot of a
    company's financial condition".  Of the four basic financial statements,
    the balance sheet is the only statement that applies to a single point
    in time of a business' calendar year.

    A standard company balance sheet has three parts: assets, liabilities
    and ownership equity. The main categories of assets are usually listed
    first, and typically in order of liquidity. Assets are followed by the
    liabilities. The difference between the assets and the liabilities is
    known as equity or the net assets or the net worth or capital of the
    company and according to the accounting equation, net worth must equal
    assets minus liabilities.

    https://en.wikipedia.org/wiki/Balance_sheet



.. class:: SheetTypes

    The global list of **sheet types** .

    >>> rt.show(sheets.SheetTypes, language="en")
    ... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
    ======= ========= ==================
     value   name      text
    ------- --------- ------------------
     B       balance   Balance sheet
     R       results   Income statement
    ======= ========= ==================
    <BLANKLINE>

    .. attribute:: balance

    .. attribute:: results

        https://en.wikipedia.org/wiki/Statement_of_comprehensive_income#Requirements_of_IFRS


.. class:: CommonItems

    The global list of **common sheet items** .

    >>> rt.show(sheets.CommonItems, language="en")
    ... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
    ======= ================= ================================= ================== ======== ===================================== ========
     value   name              text                              Sheet type         D/C      Sheet item                            Mirror
    ------- ----------------- --------------------------------- ------------------ -------- ------------------------------------- --------
     1       assets            Assets                            Balance sheet      Debit    (1) Assets
     10                        Current assets                    Balance sheet      Debit    (10) Current assets
     1000    customers         Customers receivable              Balance sheet      Debit    (1000) Customers receivable
     1010                      Taxes receivable                  Balance sheet      Debit    (1010) Taxes receivable               2010
     1020                      Cash and cash equivalents         Balance sheet      Debit    (1020) Cash and cash equivalents      2020
     1030                      Current transfers                 Balance sheet      Debit    (1030) Current transfers              2030
     1090                      Other current assets              Balance sheet      Debit    (1090) Other current assets           2090
     11                        Non-current assets                Balance sheet      Debit    (11) Non-current assets
     2       passiva           Passiva                           Balance sheet      Credit   (2) Passiva
     20      liabilities       Liabilities                       Balance sheet      Credit   (20) Liabilities
     2000    suppliers         Suppliers payable                 Balance sheet      Credit   (2000) Suppliers payable
     2010    taxes             Taxes payable                     Balance sheet      Credit   (2010) Taxes payable                  1010
     2020    banks             Banks                             Balance sheet      Credit   (2020) Banks                          1020
     2030    transfers         Current transfers                 Balance sheet      Credit   (2030) Current transfers              1030
     2090    other             Other liabilities                 Balance sheet      Credit   (2090) Other liabilities              1090
     21      capital           Own capital                       Balance sheet      Credit   (21) Own capital
     2150    net_income_loss   Net income (loss)                 Balance sheet      Credit   (2150) Net income (loss)
     4       com_ass_lia       Commercial assets & liabilities   Balance sheet      Credit   (4) Commercial assets & liabilities
     5       fin_ass_lia       Financial assets & liabilities    Balance sheet      Credit   (5) Financial assets & liabilities
     6       expenses          Expenses                          Income statement   Debit    (6) Expenses
     60      op_costs          Operation costs                   Income statement   Debit    (60) Operation costs
     6000    costofsales       Cost of sales                     Income statement   Debit    (6000) Cost of sales
     6010    operating         Operating expenses                Income statement   Debit    (6010) Operating expenses
     6020    otherexpenses     Other expenses                    Income statement   Debit    (6020) Other expenses
     62      wages             Wages                             Income statement   Debit    (62) Wages
     6900    net_income        Net income                        Income statement   Debit    (6900) Net income                     7900
     7       revenues          Revenues                          Income statement   Credit   (7) Revenues
     7000    sales             Net sales                         Income statement   Credit   (7000) Net sales
     7900    net_loss          Net loss                          Income statement   Credit   (7900) Net loss                       6900
    ======= ================= ================================= ================== ======== ===================================== ========
    <BLANKLINE>


    Every item of this list is an instance of :class:`CommonItem`.

.. class:: CommonItem

    .. attribute:: value

         Corresponds to the :attr:`ref` field in :class:`Item`

    .. attribute:: dc
    .. attribute:: sheet


.. class:: Item

    In this table the user can configure their local list of items for
    both sheet types.

    The default table is populated from :class:`CommonItems`.

    >>> rt.show(sheets.Items, language="en")
    ... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
    =========== ================================= =================================================== ================================= ================== =================== =================================
     Reference   Designation                       Designation (de)                                    Designation (fr)                  Sheet type         Booking direction   Common sheet item
    ----------- --------------------------------- --------------------------------------------------- --------------------------------- ------------------ ------------------- ---------------------------------
     1           Assets                            Vermögen                                            Actifs                            Balance sheet      Debit               Assets
     10          Current assets                    Umlaufvermögen                                      Current assets                    Balance sheet      Debit               Current assets
     1000        Customers receivable              Customers receivable                                Customers receivable              Balance sheet      Debit               Customers receivable
     1010        Taxes receivable                  Taxes receivable                                    Taxes receivable                  Balance sheet      Debit               Taxes receivable
     1020        Cash and cash equivalents         Cash and cash equivalents                           Cash and cash equivalents         Balance sheet      Debit               Cash and cash equivalents
     1030        Current transfers                 Current transfers                                   Current transfers                 Balance sheet      Debit               Current transfers
     1090        Other current assets              Sonstige kurzfristige Vermögenswerte                Other current assets              Balance sheet      Debit               Other current assets
     11          Non-current assets                Langfristige Vermögenswerte                         Non-current assets                Balance sheet      Debit               Non-current assets
     2           Passiva                           Russland                                            Passiva                           Balance sheet      Credit              Passiva
     20          Liabilities                       Verpflichtungen                                     Passifs                           Balance sheet      Credit              Liabilities
     2000        Suppliers payable                 Lieferanten zahlbar                                 Suppliers payable                 Balance sheet      Credit              Suppliers payable
     2010        Taxes payable                     Taxes payable                                       Taxes payable                     Balance sheet      Credit              Taxes payable
     2020        Banks                             Banken                                              Banks                             Balance sheet      Credit              Banks
     2030        Current transfers                 Current transfers                                   Current transfers                 Balance sheet      Credit              Current transfers
     2090        Other liabilities                 Sonstige Verbindlichkeiten                          Other liabilities                 Balance sheet      Credit              Other liabilities
     21          Own capital                       Eigenkapital                                        Own capital                       Balance sheet      Credit              Own capital
     2150        Net income (loss)                 Net income (loss)                                   Net income (loss)                 Balance sheet      Credit              Net income (loss)
     4           Commercial assets & liabilities   Kommerzielle Vermögenswerte und Verbindlichkeiten   Commercial assets & liabilities   Balance sheet      Credit              Commercial assets & liabilities
     5           Financial assets & liabilities    Finanzielle Vermögenswerte und Verbindlichkeiten    Financial assets & liabilities    Balance sheet      Credit              Financial assets & liabilities
     6           Expenses                          Ausgaben                                            Dépenses                          Income statement   Debit               Expenses
     60          Operation costs                   Diplome                                             Operation costs                   Income statement   Debit               Operation costs
     6000        Cost of sales                     Cost of sales                                       Cost of sales                     Income statement   Debit               Cost of sales
     6010        Operating expenses                Betriebliche Aufwendungen                           Operating expenses                Income statement   Debit               Operating expenses
     6020        Other expenses                    Sonstige Auslagen                                   Other expenses                    Income statement   Debit               Other expenses
     62          Wages                             Löhne und Gehälter                                  Salaires                          Income statement   Debit               Wages
     6900        Net income                        Net income                                          Net income                        Income statement   Debit               Net income
     7           Revenues                          Einnahmen                                           Revenus                           Income statement   Credit              Revenues
     7000        Net sales                         Net sales                                           Net sales                         Income statement   Credit              Net sales
     7900        Net loss                          Net loss                                            Net loss                          Income statement   Credit              Net loss
    =========== ================================= =================================================== ================================= ================== =================== =================================
    <BLANKLINE>



    In the demo database this list is an unchanged copy of :class:`CommonItems`.


The accounting report
=====================

.. glossary::

  accounting report

    A printable document that describes the accountable aspects of the business
    activity.

.. class:: Report

  Database model used to store an :term:`accounting report`.

.. class:: AccountEntry
.. class:: PartnerEntry
.. class:: AnaAccountEntry
.. class:: ItemEntry

    The computed value of given *item* for a given report.

>>> rpt = sheets.Report.objects.get(pk=1)
>>> print(rpt.start_period)
2015-01
>>> print(rpt.end_period)
2015-12
>>> rpt.run_update_plan(rt.login('robin'))  # temporary 20200927
>>> rt.show(sheets.ResultsEntriesByReport, rpt)  # doctest: -SKIP
========================= =========== ==========
 Description               Expenses    Revenues
------------------------- ----------- ----------
 **6 Expenses**            26 094,33
 ** 60 Operation costs**   26 094,33
 6000 Cost of sales        6 316,32
 6010 Operating expenses   16 179,12
 6020 Other expenses       3 598,89
 **7 Revenues**                        9 950,00
 7000 Net sales                        9 950,00
========================= =========== ==========
<BLANKLINE>


>>> ses = rt.login("robin")
>>> ses.show_story(rpt.get_story(ses), header_level=2)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
------------------------
General account balances
------------------------
============================== ================ =============== =============== ===============
 Account                        Balance before   Debit           Credit          Balance after
------------------------------ ---------------- --------------- --------------- ---------------
 4000 Customers                 0.00 CR          10 069,20       7 621,80        2447.40 DB
 4100 Suppliers                 0.00 CR          22 332,12       27 904,40       5572.28 CR
 4300 Pending payment orders    0.00 CR          22 437,72       22 437,72       0 CR
 4500 Tax offices               0.00 CR          105,60          105,60          0 CR
 4510 VAT due                   0.00 CR          105,60          159,00          53.40 CR
 4520 VAT deductible            0.00 CR          1 909,07                        1909.07 DB
 5500 Bestbank                  0.00 CR          14 835,12       40,00           14795.12 DB
 6010 Purchase of services      0.00 CR          16 179,12                       16179.12 DB
 6020 Purchase of investments   0.00 CR          3 598,89                        3598.89 DB
 6040 Purchase of goods         0.00 CR          6 316,32                        6316.32 DB
 7000 Sales                     0.00 CR                          4 600,00        4600.00 CR
 7010 Sales on therapies        0.00 CR                          5 350,00        5350.00 CR
 **Total (12 rows)**                             **97 888,76**   **68 218,52**
============================== ================ =============== =============== ===============
<BLANKLINE>
--------------------------
Analytic accounts balances
--------------------------
====================== ================ =============== ======== ===============
 Account                Balance before   Debit           Credit   Balance after
---------------------- ---------------- --------------- -------- ---------------
 1100 Wages             0.00 CR          538,96                   538.96 DB
 1200 Transport         0.00 CR          1 411,98                 1411.98 DB
 1300 Training          0.00 CR          3 128,42                 3128.42 DB
 1400 Other costs       0.00 CR          650,08                   650.08 DB
 2100 Secretary wages   0.00 CR          1 520,72                 1520.72 DB
 2110 Manager wages     0.00 CR          4 366,90                 4366.90 DB
 2200 Transport         0.00 CR          3 671,17                 3671.17 DB
 2300 Training          0.00 CR          523,71                   523.71 DB
 3000 Investment        0.00 CR          1 192,03                 1192.03 DB
 4100 Wages             0.00 CR          3 586,76                 3586.76 DB
 4200 Transport         0.00 CR          481,78                   481.78 DB
 4300 Training          0.00 CR          501,50                   501.50 DB
 5100 Wages             0.00 CR          1 328,76                 1328.76 DB
 5200 Transport         0.00 CR          2 942,07                 2942.07 DB
 5300 Other costs       0.00 CR          249,49                   249.49 DB
 **Total (15 rows)**                     **26 094,33**
====================== ================ =============== ======== ===============
<BLANKLINE>
------------------------
Partner balances (Sales)
------------------------
=========================================== ================ =============== ============== ===============
 Partner                                     Balance before   Debit           Credit         Balance after
------------------------------------------- ---------------- --------------- -------------- ---------------
 `Altenberg Hans <…>`__                      0.00 CR          440,00          419,00         21.00 DB
 `Arens Andreas <…>`__                       0.00 CR          500,00          500,00         0 CR
 `Arens Annette <…>`__                       0.00 CR          775,00          775,00         0 CR
 `Ausdemwald Alfons <…>`__                   0.00 CR          500,00          500,00         0 CR
 `Auto École Verte <…>`__                    0.00 CR          225,00          225,00         0 CR
 `Bastiaensen Laurent <…>`__                 0.00 CR          245,00          20,00          225.00 DB
 `Bernd Brechts Bücherladen <…>`__           0.00 CR          120,00          120,00         0 CR
 `Bestbank <…>`__                            0.00 CR          225,00          225,00         0 CR
 `Bäckerei Ausdemwald <…>`__                 0.00 CR          605,00          605,00         0 CR
 `Bäckerei Mießen <…>`__                     0.00 CR          120,00          120,00         0 CR
 `Bäckerei Schmitz <…>`__                    0.00 CR          420,00          420,00         0 CR
 `Chantraine Marc <…>`__                     0.00 CR          150,00          30,00          120.00 DB
 `Charlier Ulrike <…>`__                     0.00 CR          635,00          30,00          605.00 DB
 `Collard Charlotte <…>`__                   0.00 CR          490,00          30,00          460.00 DB
 `Demeulenaere Dorothée <…>`__               0.00 CR          50,00           50,00          0 CR
 `Denon Denis <…>`__                         0.00 CR          90,00           90,00          0 CR
 `Dericum Daniel <…>`__                      0.00 CR          900,00                         900.00 DB
 `Dobbelstein-Demeulenaere Dorothée <…>`__   0.00 CR          30,00           30,00          0 CR
 `Donderweer BV <…>`__                       0.00 CR          225,00          225,00         0 CR
 `Emonts Erich <…>`__                        0.00 CR          20,00           20,00          0 CR
 `Emontspool Erwin <…>`__                    0.00 CR          30,00           30,00          0 CR
 `Garage Mergelsberg <…>`__                  0.00 CR          489,60          489,60         0 CR
 `Groteclaes Gregory <…>`__                  0.00 CR          20,00           20,00          0 CR
 `Hans Flott & Co <…>`__                     0.00 CR          605,00          605,00         0 CR
 `Hilgers Henri <…>`__                       0.00 CR          30,00           30,00          0 CR
 `Jonas Josef <…>`__                         0.00 CR          20,40           20,40          0 CR
 `Kaivers Karl <…>`__                        0.00 CR          30,00           30,00          0 CR
 `Leffin Electronics <…>`__                  0.00 CR          100,00          100,00         0 CR
 `Malmendier Marc <…>`__                     0.00 CR          20,00           20,00          0 CR
 `Martelaer Mark <…>`__                      0.00 CR          30,00           30,00          0 CR
 `Moulin Rouge <…>`__                        0.00 CR          480,00          489,60         9.60 CR
 `Radermacher Daniela <…>`__                 0.00 CR          20,00           20,00          0 CR
 `Radermacher Edgard <…>`__                  0.00 CR          30,00           30,00          0 CR
 `Radermecker Rik <…>`__                     0.00 CR          20,00           20,00          0 CR
 `Reinhards Baumschule <…>`__                0.00 CR          420,00          294,00         126.00 DB
 `Rumma & Ko OÜ <…>`__                       0.00 CR          469,20          469,20         0 CR
 `Van Achter NV <…>`__                       0.00 CR          460,00          460,00         0 CR
 `da Vinci David <…>`__                      0.00 CR          30,00           30,00          0 CR
 **Total (38 rows)**                                          **10 069,20**   **7 621,80**
=========================================== ================ =============== ============== ===============
<BLANKLINE>
----------------------------
Partner balances (Purchases)
----------------------------
========================================== ================ =============== =============== ===============
 Partner                                    Balance before   Debit           Credit          Balance after
------------------------------------------ ---------------- --------------- --------------- ---------------
 `Bestbank <…>`__                           0.00 CR          163,00          205,50          42.50 CR
 `Bäckerei Ausdemwald <…>`__                0.00 CR          2 407,80        3 010,00        602.20 CR
 `Bäckerei Mießen <…>`__                    0.00 CR          4 802,60        6 005,00        1202.40 CR
 `Bäckerei Schmitz <…>`__                   0.00 CR          12 970,32       16 210,90       3240.58 CR
 `Donderweer BV <…>`__                      0.00 CR          802,60          1 005,00        202.40 CR
 `Garage Mergelsberg <…>`__                 0.00 CR          567,00          709,00          142.00 CR
 `Rumma & Ko OÜ <…>`__                      0.00 CR          568,80          709,00          140.20 CR
 `Tough Thorough Thought Therapies <…>`__   0.00 CR          50,00           50,00           0 CR
 **Total (8 rows)**                                          **22 332,12**   **27 904,40**
========================================== ================ =============== =============== ===============
<BLANKLINE>
------------------------
Partner balances (Wages)
------------------------
No data to display
------------------------
Partner balances (Taxes)
------------------------
========================================== ================ ============ ============ ===============
 Partner                                    Balance before   Debit        Credit       Balance after
------------------------------------------ ---------------- ------------ ------------ ---------------
 `Mehrwertsteuer-Kontrollamt Eupen <…>`__   0.00 CR          105,60       105,60       0 CR
 **Total (1 rows)**                                          **105,60**   **105,60**
========================================== ================ ============ ============ ===============
<BLANKLINE>
----------------------------
Partner balances (Clearings)
----------------------------
No data to display
--------------------------------------
Partner balances (Bank payment orders)
--------------------------------------
==================== ================ =============== =============== ===============
 Partner              Balance before   Debit           Credit          Balance after
-------------------- ---------------- --------------- --------------- ---------------
 `Bestbank <…>`__     0.00 CR          22 437,72       22 437,72       0 CR
 **Total (1 rows)**                    **22 437,72**   **22 437,72**
==================== ================ =============== =============== ===============
<BLANKLINE>
-------------
Balance sheet
-------------
================================ ========== ===========
 Description                      Activa     Passiva
-------------------------------- ---------- -----------
 **1 Assets**                                19 098,19
 ** 10 Current assets**                      19 098,19
 1000 Customers receivable                   2 447,40
 1010 Taxes receivable                       1 855,67
 1020 Cash and cash equivalents              14 795,12
 **2 Passiva**                    5 572,28
 ** 20 Liabilities**              5 572,28
 2000 Suppliers payable           5 572,28
 2030 Current transfers
================================ ========== ===========
<BLANKLINE>
----------------
Income statement
----------------
========================= =========== ==========
 Description               Expenses    Revenues
------------------------- ----------- ----------
 **6 Expenses**            26 094,33
 ** 60 Operation costs**   26 094,33
 6000 Cost of sales        6 316,32
 6010 Operating expenses   16 179,12
 6020 Other expenses       3 598,89
 **7 Revenues**                        9 950,00
 7000 Net sales                        9 950,00
========================= =========== ==========
<BLANKLINE>


TODO
====

- The Belgian and French `PCMN
  <https://en.wikipedia.org/wiki/French_generally_accepted_accounting_principles>`__
  has 7+1 top-level accounts:

    | CLASSE 0 : Droits & engagements hors bilan
    | CLASSE 1 : Fonds propres, provisions pour risques & charges et Dettes à plus d'un an
    | CLASSE 2 : Frais d'établissement, actifs immobilisés et créances à plus d'un an

  | CLASSE 3 : Stock & commandes en cours d'exécution
    | CLASSE 4 : Créances et dettes à un an au plus
    | CLASSE 5 : Placements de trésorerie et valeurs disponibles
    | CLASSE 6 : Charges
    | CLASSE 7 : Produits

  explain the differences and how to solve this.

  See also

  - http://code.gnucash.org/docs/help/acct-types.html
  - http://www.futureaccountant.com/accounting-process/study-notes/financial-accounting-account-types.php


- A Liability is Capital acquired from others.
  Both together is what French accountants call *passif*.

  The accounting equation "Assets = Liabilities + Capital"
  in French is simply:

      Actif = Passif

  I found an excellent definition of these two terms at
  `plancomptable.com <http://www.plancomptable.com/titre-II/titre-II.htm>`_:

  - Un actif est un élément identifiable du patrimoine ayant une
    valeur économique positive pour l’entité, c’est-à-dire un élément
    générant une ressource que l’entité contrôle du fait d’événements
    passés et dont elle attend des avantages économiques futurs.

  - Un passif est un élément du patrimoine ayant une valeur
    économique négative pour l'entité, c'est-à-dire une obligation de
    l'entité à l'égard d'un tiers dont il est probable ou certain
    qu'elle provoquera une sortie des ressources au bénéfice de ce
    tiers, sans contrepartie au moins équivalente attendue de celui-ci.


Some vocabulary

- Provisions pour risques et charges : Gesetzliche Rücklagen.
- Créances et dettes : Kredite, Anleihen, Schulden.

The template of the report
==========================

.. xfile:: accounting/Report/default.weasy.html

   Uses the method :meth:`ar.show_story
   <lino.core.requests.BaseRequest.show_story>`

Don't read me
=============


>>> t = rt.models.sheets.BalanceEntriesByReport
>>> th = t.get_handle()
>>> th  #doctest: +ELLIPSIS
<lino.core.tables.TableHandle object at ...>

>>> ll = th.get_grid_layout()
>>> ll.layout._datasource is t
True

>>> cols = th.get_columns()
>>> el = cols[0]
>>> print(el.field.name)
description
>>> print(el.name)
description
>>> print(el.width)
40
>>> el.preferred_width
30

>>> th = rt.models.sheets.Items.get_handle()
>>> cols = th.get_columns()
>>> el = cols[0]
>>> print(el.field.name)
ref
>>> print(el.width)
4
>>> el.preferred_width
21

TODO: the preferred_width of the ref field should be 4, not 21.
It is a :class:`lino.mixins.ref.StructuredReferrable`
with :attr:`ref_max_length` set to 4.
