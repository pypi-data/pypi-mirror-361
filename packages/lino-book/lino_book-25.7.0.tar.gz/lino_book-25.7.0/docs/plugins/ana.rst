.. doctest docs/plugins/ana.rst
.. _xl.specs.ana:

==============================
``ana``: Analytical accounting
==============================

.. currentmodule:: lino_xl.lib.ana

The :mod:`lino_xl.lib.ana` plugin adds analytic accounting to
general ledger.

The plugin defines several models:

- Analytical accounts and their groups
- Analytical invoices and their items


Table of contents:

.. contents::
   :depth: 1
   :local:


About this document
===================

Examples in this document use the :mod:`lino_book.projects.tera1` demo
project.

>>> from lino import startup
>>> startup('lino_book.projects.tera1.settings')
>>> from lino.api.doctest import *

The plugin requires :mod:`lino_xl.lib.accounting`.

>>> dd.plugins.ana.needs_plugins
['lino_xl.lib.accounting']


Analytical accounts
===================

"Analytical accounts" can be configured via :menuselection:`Configure
--> Accounting --> Analytical accounts`.

>>> show_menu_path('ana.Accounts')
Configure --> Accounting --> Analytical accounts


>>> rt.show('ana.Accounts')
=========== ====================== ====================== ======================
 Reference   Designation            Designation (de)       Designation (fr)
----------- ---------------------- ---------------------- ----------------------
 1           Operation costs        Diplome                Operation costs
 1100        Wages                  Löhne und Gehälter     Salaires
 1200        Transport              Transport              Transport
 1300        Training               Ausbildung             Formation
 1400        Other costs            Sonstige Unkosten      Other costs
 2           Administrative costs   Verwaltungskosten      Administrative costs
 2100        Secretary wages        Gehälter Sekretariat   Secretary wages
 2110        Manager wages          Gehälter Direktion     Manager wages
 2200        Transport              Transport              Transport
 2300        Training               Ausbildung             Formation
 3           Investments            Investierungen         Investissements
 3000        Investment             Investierung           Investment
 4           Project 1              Projekt 1              Project 1
 4100        Wages                  Löhne und Gehälter     Salaires
 4200        Transport              Transport              Transport
 4300        Training               Ausbildung             Formation
 5           Project 2              Projekt 2              Project 2
 5100        Wages                  Löhne und Gehälter     Salaires
 5200        Transport              Transport              Transport
 5300        Other costs            Sonstige Unkosten      Other costs
=========== ====================== ====================== ======================
<BLANKLINE>

>>> dd.plugins.ana.ref_length
4

>>> fld = rt.models.ana.Account._meta.get_field('ref')
>>> fld.max_length
200

The plugin then injects two fields to your general accounts model and
one field into your movments model:

>>> show_fields(accounting.Account, "needs_ana ana_account")  #doctest: +NORMALIZE_WHITESPACE
- Needs analytical account (needs_ana) : Whether transactions on this account
  require the user to also specify an analytic account.
- Analytical account (ana_account) : Which analytic account to suggest for
  transactions on this account.

>>> show_fields(accounting.Movement, "ana_account")
- Analytical account (ana_account) : The analytic account to move together with this transactions.

And finally this plugin defines a new voucher type
`ana.AnaAccountInvoice`, which is almost the same as
`vat.AccountInvoice` except that it has an additional field per
invoice item where the user can specify an analytic account.  For
example:

>>> obj = ana.AnaAccountInvoice.objects.order_by('id').first()
>>> rt.show(ana.ItemsByInvoice, obj)
============================= ============= ==================== ========================== ============= ============ =============
 Account                       Description   Analytical account   VCl                        TotExcl       VAT          TotIncl
----------------------------- ------------- -------------------- -------------------------- ------------- ------------ -------------
 (6010) Purchase of services                 (1100) Wages         Goods at normal VAT rate   33,0579       6,9421       40,0000
 **Total (1 rows)**                                                                          **33,0579**   **6,9421**   **40,0000**
============================= ============= ==================== ========================== ============= ============ =============
<BLANKLINE>


When you change the general account of an invoice item, Lino always
updates the analytical account of that item.





Analytic accounts
=================

.. class:: Account

    .. attribute:: ref

       The unique reference.

    .. attribute:: designation

    .. attribute:: group

        The analytic account group this account belongs to.

Groups of analytic accounts
===========================

.. class:: Group

    .. attribute:: ref

       The unique reference.

    .. attribute:: designation


Invoices with analytic account
==============================

.. class:: AnaAccountInvoice


    .. attribute:: make_copy

        The :class:`MakeCopy` action.

.. class:: InvoiceItem

    .. attribute:: voucher
    .. attribute:: ana_account
    .. attribute:: title


Make a copy of an invoice (:guilabel:`⁂`)
=========================================


.. class:: MakeCopy

    You can simplify manual recording of invoices using the :guilabel:`⁂`
    button which creates an invoice using an existing invoice as template.

    Lino then opens the following dialog window:

    .. image:: ana/AnaAccountInvoice.make_copy.de.png

    Wenn man das Fenster bestätigt, wird ohne weitere Fragen eine neue
    Rechnung erstellt und registriert.

    Das Verhalten dieser Aktion hängt teilweise davon ab, ob man den
    Gesamtbetrag (:guilabel:`Total inkl MWSt`) eingibt oder nicht:

    - Wenn man einen Gesamtbetrag eingibt, wird eine einzige
      Rechnungszeile erstellt mit diesem Betrag. Das Generalkonto dieser
      Zeile ist entweder das im Dialogfenster angegebene, oder (falls man
      das Feld dort leer gelassen hat) das G-Konto der ersten Zeile der
      Kopiervorlage.  Ebenso das A-Konto.

    - Wenn man den Gesamtbetrag leer lässt, werden alle Zeilen der
      Kopiervorlage exakt kopiert.




    .. attribute:: entry_date

        The entry date of the invoice to create.

    .. attribute:: partner

        The partner of the invoice to create.

    .. attribute:: subject

        The subject of the invoice to create.

    .. attribute:: your_ref

        The "your reference" of the invoice to create.

    .. attribute:: total_incl

        The total amount of the invoice to create.  Leave blank if you
        want to copy all rows.

        If you enter an amount,

    .. attribute:: account

        The general account to use for the item of the invoice if you
        specified a total amount.

    .. attribute:: ana_account

        The analytical account to use for the item of the invoice if
        you specified a total amount.
