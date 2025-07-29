.. doctest docs/plugins/accounting.rst
.. _xl.specs.accounting:
.. _cosi.specs.accounting:
.. _cosi.tested.accounting:

==================================
``accounting``: General accounting
==================================

.. currentmodule:: lino_xl.lib.accounting

The :mod:`lino_xl.lib.accounting` plugin adds basic notions for
accounting: accounts, journals, vouchers and movements.

Table of contents:

.. contents::
   :depth: 1
   :local:

Examples in this document use the :mod:`lino_book.projects.cosi1` demo project.

>>> from lino_book.projects.cosi1.startup import *

>>> ses = rt.login("robin")
>>> translation.activate('en')

List of partners who are both supplier and customer and have open movements:

>>> from lino_xl.lib.accounting.choicelists import TradeTypes
>>> def has_mvt(obj, tt):
...     qs = accounting.Movement.objects.filter(partner=obj, cleared=False, voucher__journal__trade_type=tt)
...     return qs.exists()
>>> for p in contacts.Partner.objects.all():
...     if has_mvt(p, TradeTypes.purchases) and has_mvt(p, TradeTypes.sales):
...         print(p.pk, p)



Overview
========

:term:`Ledger movements <ledger movement>` are never created individually but by
registering a :term:`numbered voucher`.

Vouchers are stored in the database using some subclass of the
:class:`Voucher` model. The voucher model is never being used directly
despite the fact that it is a concrete model.

In applications that use the :mod:`accounting <lino_xl.lib.accounting>` plugin,
accounts are used as the target of :term:`ledger movements <ledger
movement>`.

There are many views for looking at accounting data.

- :class:`GeneralAccountsBalance`, :class:`CustomerAccountsBalance` and
  :class:`SupplierAccountsBalance`

- :class:`Debtors` and :class:`Creditors` are tables with one row for
  each partner who has a positive balance (either debit or credit).
  Accessible via :menuselection:`Reports --> Ledger --> Debtors` and
  :menuselection:`Reports --> Ledger --> Creditors`

Plugin configuration settings
=============================

Here is a list of the :term:`plugin settings <plugin setting>` for this plugin.

.. setting:: accounting.ref_length

  The :attr:`max_length` of the `Reference` field of a :term:`ledger account`.

.. setting:: accounting.currency_symbol

  The currency symbol to use when no currency is set.

  Temporary approach until we add support for multiple currencies.
  See also :meth:`lino.core.site.Site.format_currency`.

.. setting:: accounting.use_pcmn

    Whether to use the PCMN notation.

    PCMN stands for "plan compatable minimum normalisé" and is a
    standardized nomenclature for accounts used in France and
    Belgium.


.. setting:: accounting.project_model

    Leave this to `None` for normal behaviour.  Set this to a
    string of the form `'<app_label>.<ModelName>'` if you want to
    add an additional field `project` to all models which inherit
    from :class:`ProjectRelated`.


.. setting:: accounting.worker_model

    The model to use for workers.

    Default value is `None`.  If this is set to a model name (e.g.
    'contacts.Person'), Lino will add a field
    :class:`PaymentTerm.worker`.


.. setting:: accounting.suppress_movements_until

  Don't create any movements before that date.  Vouchers can exist
  and get registered before that date, but they don't have any
  influence to the ledger.

  This is useful e.g. when you want to keep legacy vouchers in your
  database but not their movments.

.. setting:: accounting.sales_method

  Which sales-related journals to create on a new site and how they
  collaborate. The resulting demo data also depends on whether the trading
  and/or invoicing plugins are installed.


.. setting:: accounting.has_payment_methods

  Whether this :term:`Lino site` knows about :term:`payment methods <payment
  method>` and cash invoices (both used on a :term:`point of sale`).



User roles
==========

.. class:: LedgerPartner

  Can see transactions related to their :term:`partner` account.

.. class:: AccountingReader

  Can read all accounting data and create reports,
  but cannot change any relevant data.

.. class:: LedgerUser

  Can see all journals, create vouchers of any kind, can see vouchers of other
  users but cannot edit them.

.. class:: VoucherSupervisor

  Can edit vouchers that have been written by other users.

.. class:: LedgerStaff

    Can configure ledger functionality.


Accounts
========

.. class:: Account

    Django model for representing a :term:`ledger account`.

    .. attribute:: name

        The multilingual designation of this account, as the users see
        it.

    .. attribute:: ref

        An optional unique name which can be used to reference a given
        account.

    .. attribute:: type

        The *account type* of this account.  This points to an item of
        :class:`CommonAccounts`.

    .. attribute:: needs_partner

        Whether bookings to this account need a partner specified.

        For :term:`payment orders <payment order>` this causes the counter entry
        of financial documents to be detailed or not (i.e. one contra entry for
        every item or a single counter entry per voucher.

    .. attribute:: vat_class

        The default VAT class to use for transactions on this account.

    .. attribute:: default_amount

        The default amount to book in bank statements or journal entries when
        this account has been selected manually. The default :term:`booking
        direction` is that of the :attr:`type`.

    .. attribute:: purchases_allowed
    .. attribute:: sales_allowed
    .. attribute:: wages_allowed
    .. attribute:: clearings_allowed
    .. attribute:: FOO_allowed

        These checkboxes indicate whether this account can be used on
        an item of a purchases (or sales or wages or FOO)
        invoice. There is one such checkbox for every trade type
        (:class:`TradeTypes`).  They
        exist only when the :mod:`accounting <lino_xl.lib.accounting>` plugin
        is installed as well.  See also the
        :meth:`get_allowed_accounts
        <Journal.get_allowed_accounts>` method.

    .. attribute:: needs_ana

        Whether transactions on this account require the user to also
        specify an analytic account.

        This field exists only when :mod:`lino_xl.lib.ana` is
        installed as well.

    .. attribute:: ana_account

        Which analytic account to suggest for transactions on this
        account.

        This field exists only when :mod:`lino_xl.lib.ana` is
        installed as well.

    .. attribute:: sheet_item

        Pointer to the item of the balance sheet or income statement
        that will report the movements of this account.

        This field is a dummy field when :mod:`lino_xl.lib.sheets` is
        not installed.



Common accounts
===============

Here is the standard list of :term:`common accounts <common account>` in a
:ref:`cosi` application:

>>> rt.show(accounting.CommonAccounts, language="en")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
======= ========================= ========================= =========== ================================
 value   name                      text                      Clearable   Account
------- ------------------------- ------------------------- ----------- --------------------------------
 1000    net_income_loss           Net income (loss)         Yes         (1000) Net income (loss)
 4000    customers                 Customers                 Yes         (4000) Customers
 4100    suppliers                 Suppliers                 Yes         (4100) Suppliers
 4200    employees                 Employees                 Yes         (4200) Employees
 4300    pending_po                Pending payment orders    Yes         (4300) Pending payment orders
 4500    tax_offices               Tax offices               Yes         (4500) Tax offices
 4510    vat_due                   VAT due                   No          (4510) VAT due
 4513    due_taxes                 VAT declared              No          (4513) VAT declared
 4520    vat_deductible            VAT deductible            No          (4520) VAT deductible
 4530    vat_returnable            VAT returnable            No          (4530) VAT returnable
 4800    clearings                 Internal clearings        Yes         (4800) Internal clearings
 4900    waiting                   Waiting account           Yes         (4900) Waiting account
 5500    best_bank                 Bestbank                  No          (5500) Bestbank
 5700    cash                      Cash                      No          (5700) Cash
 6010    purchase_of_services      Purchase of services      No          (6010) Purchase of services
 6020    purchase_of_investments   Purchase of investments   No          (6020) Purchase of investments
 6040    purchase_of_goods         Purchase of goods         No          (6040) Purchase of goods
 6300    wages                     Wages                     No          (6300) Wages
 6900    net_income                Net income                No          (6900) Net income
 7000    sales                     Sales                     No          (7000) Sales
 7900    net_loss                  Net loss                  No
======= ========================= ========================= =========== ================================
<BLANKLINE>

Lino applications can add specific items to that list or potentially redefine it
completely.


.. class:: CommonAccounts

    The global list of :term:`common accounts <common account>`.

    This is a :class:`lino.core.choicelists.ChoiceList`.
    Every item is an instance of :class:`CommonAccount`.

    This list is automatically sorted at startup because it is populated by
    several plugins and because the natural sorting order would be useless and
    irritating.


    .. attribute:: waiting

      The **waiting account**, used to temporarily book movements for which you
      do not know where to book them.

    .. attribute:: undeclared_costs

      Used to books costs that will be reculated internally and are irrelevant
      for VAT declaration and annual report.





.. class:: CommonAccount

    The base class for items of ::class:`CommonAccounts`.

    It defines two additional attributes:

    .. attribute:: clearable

        Default value for :attr:`Account.clearable`.

    .. attribute:: needs_partner

        Default value for :attr:`Account.needs_partner`.

    .. method:: get_object(self)

        Return the database object representing this common account.

    .. method:: set_object(self, obj)

        Set the cached database object representing this common account.

        Called internally when :attr:`Account.common_account` is updated via web
        interface.



Keep in mind that common accounts are no database objects.   See them rather as
a list of configuration values. They are just a list of named pointers to
actual database objects.

For example you might want to know how many sales operations are in your
database:

>>> obj = accounting.CommonAccounts.sales.get_object()
>>> obj
Account #20 ('(7000) Sales')
>>> accounting.Movement.objects.filter(account=obj).count()
163

A common account neither requires nor makes sure that its :term:`database row`
exists. For example the common account "Net loss" has no database object in the
accounts chart pointing to it.  The above trick won't work for counting the
number of net loss operations:

>>> obj = accounting.CommonAccounts.net_loss.get_object()
>>> obj
MissingRow('No Account pointing to <accounting.CommonAccounts.net_loss:7900>')
>>> print(obj)
MissingRow(No Account pointing to <accounting.CommonAccounts.net_loss:7900>)
>>> accounting.Movement.objects.filter(account=obj).count()
Traceback (most recent call last):
...
TypeError: Field 'id' expected a number but got MissingRow('No Account pointing to <accounting.CommonAccounts.net_loss:7900>').



Debit and credit
================


Every journal has its specific default :term:`booking direction` (configured in
:attr:`Journal.dc`). For example a (positive) amount in a sales invoice means
the opposite direction of a (positive) amount in a purchase invoice.

See also :ref:`xl.specs.sheets.accounting_eq`.

When migrating from Lino before 20201008, keep in mind that that a **checked**
:attr:`dc` field meant *credit* and **not checked** meant *debit*.


.. class:: DC

  A choicelist with the two values "debit" and "credit".

  It can be used e.g. to express the "expected" or "normal" :term:`booking
  direction` for a journal, account or field in an accounting report.

>>> rt.show(accounting.DC)
======= ======== ========
 value   name     text
------- -------- --------
 D       debit    Debit
 C       credit   Credit
======= ======== ========
<BLANKLINE>

For the following code examples we import it:

>>> from lino_xl.lib.accounting.choicelists import DC

The balance of an account
=========================

The **balance** of an account is the amount of money in that account.
An account balance is either debiting or crediting.

.. class:: Balance

    A light-weight object to represent a balance, i.e. an amount together with
    its :term:`booking direction` (debiting or crediting).

    Attributes:

    .. attribute:: d

        The amount of this balance when it is debiting, otherwise zero.

    .. attribute:: c

        The amount of this balance when it is crediting, otherwise zero.


>>> from lino_xl.lib.accounting.utils import Balance
>>> b = Balance(10, 2)
>>> b
Balance(8,0)
>>> print(b)
8 DB
>>> b.value(DC.debit)
Decimal('8')

>>> Balance(15, 23)
Balance(0,8)

A negative value on one side of the balance is automatically moved to
the other side.

>>> Balance(10, -2)
Balance(12,0)

>>> Balance(10, 2) + Balance(15, 23)
Balance(0,0)

>>> from decimal import Decimal
>>> Balance(Decimal("12.34"), Decimal("12.33"))
Balance(0.01,0)


Database fields
===============

.. class:: DebitOrCreditField

    After 20201008 this is replaced by :meth:`DC.field`.

    A field that stores the "direction" of a movement, i.e. either
    :data:`DEBIT` or :data:`CREDIT`.


.. class:: DebitOrCreditStoreField

    No longer used after 20201008.

    Used as `lino_atomizer_class` for :class:`DebitOrCreditField`.


Movements
=========


.. class:: Movement

    Django model used to represent a :term:`ledger movement`

    .. attribute:: value_date

        The date at which this movement is to be entered into the
        accounting.  This is usually the voucher's :attr:`entry_date
        <Voucher.entry_date>`, except
        e.g. for bank statements where each item can have its own
        value date.

    .. attribute:: voucher

        Pointer to the :term:`numbered voucher` that caused this movement.

    .. attribute:: partner

        Pointer to the partner involved in this movement.

        If :attr:`account` has :attr:`Account.needs_partner` set, this may not
        be blank, otherwise it must be blank.

    .. attribute:: seqno

        Sequential number within a voucher.

    .. attribute:: account

        Pointer to the :class:`Account` that is being moved by this movement.

    .. attribute:: debit

        Virtual field showing :attr:`amount` if :attr:`dc` is DEBIT.

    .. attribute:: credit

        Virtual field showing :attr:`amount` if :attr:`dc` is CREDIT.

    .. attribute:: amount

    .. attribute:: dc

    .. attribute:: match

        An unique name used to group a set of :term:`movements <ledger
        movement>` that are to be :attr:`cleared`.

    .. attribute:: cleared

        Whether this movement "is satisfied" or "has been paid".

        The movements of a matching group are cleared if and only if the sum of
        their amounts is zero.


    .. attribute:: voucher_partner

        A virtual field which returns the *partner of the voucher*.
        For incoming invoices this is the supplier, for outgoing
        invoices this is the customer, for financial vouchers this is
        empty.

    .. attribute:: voucher_link

        A virtual field which shows a link to the voucher.

    .. attribute:: match_link

        A virtual field which shows a clickable variant of the match
        string. Clicking it will open a table with all movements
        having that match.


    .. attribute:: ana_account

        The analytic account to move together with this transactions.

        This field exists only when :mod:`lino_xl.lib.ana` is
        installed as well.

.. class:: Movements

    The base table for all tables having :term:`ledger movements <ledger
    movement>` as rows.

    Defines filtering parameters and general behaviour.

    .. attribute:: start_period
    .. attribute:: end_period
    .. attribute:: start_date
    .. attribute:: end_date
    .. attribute:: cleared
    .. attribute:: journal_group
    .. attribute:: journal
    .. attribute:: year
    .. attribute:: project
    .. attribute:: partner
    .. attribute:: account


.. class:: MovementsByPartner

   Shows the ledger movements linked to a given partner.

.. class:: MovementsByAccount

    Shows the ledger movements done on a given general account.

    .. attribute:: description

        A virtual field showing a comma-separated list of the
        following items:

        - voucher narration
        - voucher partner
        - transaction's partner
        - transaction's project


.. class:: MovementsByMatch

    Show all movements having a given :attr:`Movement.match`.

    This is another example of a slave table whose master is not a database
    object, and the first example of a slave table whose master is a simple
    string.

.. class:: MovementsByProject

    Show the ledger movements of a project.

.. class:: AllMovements

    Show all the ledger movements in the database.

    Displayed by :menuselection:`Explorer --> Accounting --> Movements`.

.. class:: MovementsByVoucher

    Show the ledger movements generated by a given voucher.


The summary of :class:`MovementsByPartner` shows a *balance*. A negative number
means that we owe money to this partner, a positive number means that this
partner owes us money.

Let's pick some examples from our demo data. Here are the partners who have mode
than 2 open movements:

>>> def openmvts(p):
...     qs = accounting.Movement.objects.filter(partner=p)
...     qs = qs.filter(cleared=False)
...     return qs.count()

>>> [p for p in contacts.Partner.objects.all() if openmvts(p) > 2]
[Partner #12 ('Moulin Rouge'), Partner #80 ('Dubois Robin')]

For example Moulin Rouge:

>>> obj = contacts.Company.objects.get(pk=12)
>>> obj
Company #12 ('Moulin Rouge')

>>> rt.show(accounting.MovementsByPartner, obj)
**3 open movements (-4.65 €)**

>>> rt.show(accounting.MovementsByPartner, obj, nosummary=True)
============ ===================== ================================================= ============== ============== ============= =========
 Value date   Voucher               Description                                       Debit          Credit         Match         Cleared
------------ --------------------- ------------------------------------------------- -------------- -------------- ------------- ---------
 21/02/2025   `BNK 2/2025 <…>`__    `(4000) Customers <…>`__ | `Moulin Rouge <…>`__                  10,86          SLS 2/2025    No
 21/01/2025   `BNK 1/2025 <…>`__    `(4000) Customers <…>`__ | `Moulin Rouge <…>`__                  294,69         SLS 2/2025    No
 08/01/2025   `SLS 2/2025 <…>`__    `(4000) Customers <…>`__ | `Moulin Rouge <…>`__   310,20                        SLS 2/2025    No
 21/04/2023   `BNK 4/2023 <…>`__    `(4000) Customers <…>`__ | `Moulin Rouge <…>`__                  2 013,88       SLS 12/2023   Yes
 08/04/2023   `SLS 12/2023 <…>`__   `(4000) Customers <…>`__ | `Moulin Rouge <…>`__   2 013,88                      SLS 12/2023   Yes
                                    **Balance 4.65 (5 movements)**                    **2 324,08**   **2 319,43**
============ ===================== ================================================= ============== ============== ============= =========
<BLANKLINE>



Vouchers
========


The :class:`Voucher` model is *not* abstract because we want :class:`Movement`
to have a ForeignKey to a Voucher. A voucher is never instantiated using this
base model but using one of its subclasses.  Here are the voucher subclasses
available in :ref:`cosi`:

>>> pprint(rt.models_by_base(accounting.Voucher))
[<class 'lino_xl.lib.accounting.models.Voucher'>,
 <class 'lino_xl.lib.bevat.models.Declaration'>,
 <class 'lino_xl.lib.finan.models.BankStatement'>,
 <class 'lino_xl.lib.finan.models.JournalEntry'>,
 <class 'lino_xl.lib.finan.models.PaymentOrder'>,
 <class 'lino_xl.lib.trading.models.VatProductInvoice'>,
 <class 'lino_xl.lib.vat.models.VatAccountInvoice'>]

When the partner of an empty voucher has a purchase account, Lino automatically
creates a voucher item using this account with empty amount.



.. class:: Voucher

    Django model used to represent a :term:`numbered voucher`.

    .. attribute:: state

      The :term:`state <voucher state>` of this voucher. It decides among others
      whether you can edit this voucher or not.

      This field is defined by the implementing voucher class, which depends
      on the journal's :term:`voucher type`.

      Choices are defined in :class:`VoucherStates`

    .. attribute:: journal

      The journal into which this voucher has been booked.

      This is a mandatory pointer to a :class:`Journal` instance.

    .. attribute:: number

      The sequence number of this voucher within its :attr:`journal`.

      The voucher number is automatically assigned when the voucher is saved for
      the first time.  The voucher number depends on whether
      :attr:`yearly_numbering` is enabled or not.

      There might be surprising numbering if two users create vouchers in a same
      journal at the same time.

    .. attribute:: entry_date

      The date of the journal entry, i.e. when this voucher is to be booked.

    .. attribute:: voucher_date

      The date on the voucher (i.e. when it has been issued by its emitter).

      This is usually the same as :attr:`entry_date`.  Exceptions
      may be invoices arriving after their fiscal year has been
      closed.  Note that if you change :attr:`entry_date` of a
      voucher, then Lino will set the :attr:`voucher_date` to that
      date.

    .. attribute:: accounting_period

      The :term:`accounting period` to use when booking this voucher.
      The default value is determined from :attr:`entry_date`.

      If user changes this field, the :attr:`number` gets
      re-computed because it might change depending on the fiscal
      year of the accounting period.


    .. attribute:: narration

      A short explanation to explain the subject matter of this journal entry.

    .. attribute:: number_with_year

      Shows the accounting year and the number of this voucher within its
      journal.


    .. method:: do_and_clear(func, do_clear)

        Delete all movements of this voucher, then run the given
        callable `func`, passing it a set with all partners who had at
        least one movement in this voucher. The function is expected
        to add more partners to this set.  Then call :func:`check_clearings`
        for all these partners.

    .. method:: create_movement(item, acc_tuple, project, dc, amount, **kw):

        Create a movement for this voucher.

        The specified `item` may be `None` if this the movement is
        caused by more than one item.  It is used by
        :class:`DatedFinancialVoucher
        <lino_xl.lib.finan.DatedFinancialVoucher>`.

    .. method:: get_partner()

        Return the partner related to this voucher.  Overridden by
        :class:`lino_xl.lib.contacts.PartnerRelated` vouchers.

    .. method:: get_movement_description(self, ar)

        Generate a series of HTML chunks to be displayed in the
        :attr:`Movment.description` field.

    .. method:: get_wanted_movements()

        Subclasses must implement this.  Supposed to return or yield a
        list of unsaved :class:`Movement` instances.

    .. method:: get_mti_leaf(self):

        Return the specialized form of this voucher.

        From any :class:`Voucher` instance we can get the actual
        document (Invoice, PaymentOrder, BankStatement, ...) by
        calling this method.

    .. method:: make_xml_file(self)

      Write an :term:`XML file` in an appropriate format for this voucher.

      Lino currently knows PEPPOL and SEPA.

.. rubric:: Class inheritance diagram

.. inheritance-diagram:: lino_xl.lib.accounting.models.Voucher
    :parts: 1
    :top-classes: lino.core.model.Model




Registering a voucher
=====================


.. class:: LedgerRegistrable

  .. attribute:: toggle_state

    Toggle between "registered" and "draft" state.

    A one-click action to quickly toggle between the two the most-used
    states of a voucher.
    Represented in the :term:`toolbar` as a :guilabel:`⇅` button.

    >>> finan.BankStatements.get_action_by_name('toggle_state').help_text
    'Toggle between “registered” and “draft” state.'

  .. attribute:: hide_editable_number

    Whether to hide the number that will be used for this voucher in its journal
    as long as the voucher is in an editable state.

    We usually don't want to see the number of a voucher in an editable state
    because that number may change. We prefer to see the primary key prefixed
    with a hash to indicate that the voucher is not registered.  But e.g. in
    :mod:`lino_xl.lib.orders` we want to disable this feature.

    NB we might simply override :meth:`__str__`, but maybe this feature will be
    used in other contexts as well.

The state of a voucher is stored in a field :attr:`voucher_state
<Voucher.voucher_state>`. The available states and the rules
for changing the state are called the workflow.

.. class:: ToggleState

    The action behind :attr:`LedgerRegistrable.toggle_state`.


Journals
========

Here is the list of all :term:`journals <journal>`.


>>> ses.show(accounting.Journals,
...     column_names="ref name trade_type account dc")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=========== =========================== ============================= ============================ ===================== =============================== ===========================
 Reference   Designation                 Designation (fr)              Designation (en)             Trade type            Account                         Primary booking direction
----------- --------------------------- ----------------------------- ---------------------------- --------------------- ------------------------------- ---------------------------
 SLS         Verkaufsrechnungen          Factures vente                Sales invoices               Sales                                                 Credit
 SLC         Gutschriften Verkauf        Notes de crédit vente         Sales credit notes           Sales                                                 Debit
 PRC         Einkaufsrechnungen          Factures achat                Purchase invoices            Purchases                                             Debit
 PMO         Zahlungsaufträge Bestbank   Ordres de paiement Bestbank   Payment orders Bestbank      Bank payment orders   (4300) Pending payment orders   Credit
 CSH         Kassenbuch                  Livre de caisse               Cash book                                          (5700) Cash                     Credit
 BNK         Bestbank                    Bestbank                      Bestbank                                           (5500) Bestbank                 Credit
 MSC         Diverse Buchungen           Opérations diverses           Miscellaneous transactions                         (5700) Cash                     Credit
 PRE         Preliminary transactions    Preliminary transactions      Preliminary transactions                           (5700) Cash                     Credit
 SAL         Lohnscheine                 Fiches de paie                Paychecks                                          (5700) Cash                     Debit
 VAT         MwSt.-Erklärungen           Déclarations TVA              VAT declarations             Taxes                 (4513) VAT declared             Debit
 INB         Eingangsdokumente           Eingangsdokumente             Inbound documents            Purchases                                             Debit
=========== =========================== ============================= ============================ ===================== =============================== ===========================
<BLANKLINE>


.. class:: Journal

    Django model used to represent a :term:`journal`.

    **Fields:**

    .. attribute:: ref
    .. attribute:: trade_type

        Pointer to :class:`TradeTypes`.

    .. attribute:: voucher_type

        Pointer to an item of :class:`VoucherTypes`.

    .. attribute:: journal_group

        Pointer to an item of :class:`JournalGroups`.

    .. attribute:: yearly_numbering

        Whether the :attr:`number <Voucher.number>` of
        vouchers should restart at 1 every year.

    .. attribute:: force_sequence

    .. attribute:: make_ledger_movements

      Whether vouchers in this journal generate ledger movements.

      For example, a journal "Delivery notes" or "Offers" generally doesn't
      cause ledger movements.

    .. attribute:: preliminary

        Whether transactions in this journal are considered :term:`preliminary
        <preliminary transactions>`.

    .. attribute:: account

        The account to use for the counter-movements generated by
        vouchers in this journal.

    .. attribute:: partner

      The partner to use as default partner for vouchers in this journal.

    .. attribute:: printed_name

    .. attribute:: must_declare

      Whether movements made by this journal should be included in :term:`VAT
      declarations <VAT declaration>`.

    .. attribute:: dc

        The primary :term:`booking direction`. Voucher items in this direction
        increase the total amount of the voucher.

        In a journal of *sales invoices* this should be *Credit* because a
        positive invoice item should *credit* the turnover account (and hence
        their sum will *debit* the *customers receivable* account).

        In a journal of *purchase invoices* this should be *Debit* because a
        positive invoice item should *debit* the cost account (and hence their
        sum will *credit* the *suppliers payable* account).

        In a journal of *bank statements* this should be *Credit* because a
        crediting item (income) should increase the balance of the bank account
        while a debiting item (expense) should decrease it.

        In a journal of *payment orders* this should be *Debit* because a
        positive total means an expense to be *debited* from the *pending
        payment orders* account (see :class:`CommonAccounts`).

        In a journal of *paychecks* this should be *Debit* because a positive
        paycheck item should *debit* the wages account (and hence their sum will
        *credit* the *employees payable* account).


    .. attribute:: auto_check_clearings

        Whether to automatically check and update the 'cleared' status of ledger
        movements when (de)registering a voucher of this journal.

        This can be temporarily disabled e.g. by batch actions in order to save
        time.

    .. attribute:: auto_fill_suggestions

        Whether to automatically fill voucher item from due payments
        of the partner when entering a financial voucher.

    .. attribute:: template

        See :attr:`PrintableType.template
        <lino.mixins.printable.PrintableType.template>`.

    .. attribute:: sepa_account

        Your bank account to specify in payment order.

        Added by :doc:`sepa`.

    .. attribute:: default_invoiceable_type

        Default value for the type of
        :attr:`lino_xl.lib.trading.InvoiceItem.invoiceable`.


.. class:: Journals

  List of all Journals. Accessible via :menuselection:`Configure --> Accounting
  --> Journals`.

.. class:: JournalsOverview

    The list of all Journals shown in the dashboard.

    This is used as the primary dashboard item in :ref:`cosi`. It gives an idea
    of how much data is in the database, and it adds links for quickly opening a
    journal (which is after all one of the frequent actions in an accounting
    application).

    >>> rt.login("robin").show(accounting.JournalsOverview)
    ... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
    | **SLS** |  129 Sales invoices **⊕** |
    |---------|---------------------------|
    | **SLC** |  0 Sales credit notes **⊕** |
    |---------|-----------------------------|
    | **PRC** |  189 Purchase invoices **⊕** |
    |---------|------------------------------|
    | **PMO** |  26 Payment orders Bestbank **⊕** |
    |---------|-----------------------------------|
    | **CSH** |  0 Cash book **⊕** |
    |---------|--------------------|
    | **BNK** |  26 Bestbank **⊕** |
    |---------|--------------------|
    | **MSC** |  0 Miscellaneous transactions **⊕** |
    |---------|-------------------------------------|
    | **PRE** |  1 Preliminary transactions **⊕** |
    |---------|-----------------------------------|
    | **SAL** |  0 Paychecks **⊕** |
    |---------|--------------------|
    | **VAT** |  26 VAT declarations **⊕** |
    |---------|----------------------------|
    | **INB** |  0 Inbound documents **⊕** |
    |---------|----------------------------|


    >>> rt.login("robin").show(accounting.JournalsOverview, display_mode=DISPLAY_MODE_GRID)
    ... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
    ======================================================== ========= =========== ============ ============ ==========
     Description                                              Total     This year   This month   Unfinished   Warnings
    -------------------------------------------------------- --------- ----------- ------------ ------------ ----------
     Sales invoices (SLS) / **New Invoice**                   **129**   **15**      **4**
     Sales credit notes (SLC) / **New Credit note**
     Purchase invoices (PRC) / **New Invoice**                **189**   **21**      **7**
     Payment orders Bestbank (PMO) / **New Payment order**    **26**    **2**
     Cash book (CSH) / **New Cash statement**
     Bestbank (BNK) / **New Bank statement**                  **26**    **2**
     Miscellaneous transactions (MSC) / **New Transaction**
     Preliminary transactions (PRE) / **New Transaction**     **1**
     Paychecks (SAL) / **New Paycheck**
     VAT declarations (VAT) / **New VAT declaration**         **26**    **2**
     Inbound documents (INB) / **New Invoice**
     **Total (11 rows)**                                      **397**   **42**      **11**       **0**
    ======================================================== ========= =========== ============ ============ ==========
    <BLANKLINE>


.. rubric:: Class inheritance diagram

.. inheritance-diagram:: lino_xl.lib.accounting.models.Journal
    :parts: 1
    :top-classes: lino.core.model.Model




Debit or credit? The PCSD rule
==============================

The "PCSD" rule: A **purchase** invoice **credits** the partner's account, a
**sales** invoice **debits** the partner's account.

>>> obj = vat.VatAccountInvoice.objects.order_by('id')[0]
>>> obj
VatAccountInvoice #1 ('PRC 1/2023')

>>> rt.show(vat.MovementsByVoucher, obj)
============================= ========== =========== =========== ================================ ================ =========
 Account                       Partner    Debit       Credit      VAT class                        Match            Cleared
----------------------------- ---------- ----------- ----------- -------------------------------- ---------------- ---------
 (6010) Purchase of services              33,06                   010 (Goods at normal VAT rate)                    Yes
 (4520) VAT deductible                    6,94                    010 (Goods at normal VAT rate)                    Yes
 (4100) Suppliers              Bestbank               40,00                                        **PRC 1/2023**   Yes
                                          **40,00**   **40,00**
============================= ========== =========== =========== ================================ ================ =========
<BLANKLINE>

>>> obj = trading.VatProductInvoice.objects.order_by('id')[0]
>>> obj
VatProductInvoice #190 ('SLS 1/2023')
>>> rt.show(vat.MovementsByVoucher, obj)
================== ========== ============== ============== ================ ================ =========
 Account            Partner    Debit          Credit         VAT class        Match            Cleared
------------------ ---------- -------------- -------------- ---------------- ---------------- ---------
 (7000) Sales                                 2 999,85       100 (Services)                    Yes
 (4510) VAT due                               629,97         100 (Services)                    Yes
 (4000) Customers   Bestbank   3 629,82                                       **SLS 1/2023**   Yes
                               **3 629,82**   **3 629,82**
================== ========== ============== ============== ================ ================ =========
<BLANKLINE>


But beware: when **configuring your journals**, Lino asks for the
:guilabel:`Primary booking direction` of a journal. This is the *opposite* of
what the PCSD rule says because the primary movements are the movements
mentioned on the document.

>>> print(accounting.Journal.get_by_ref("SLS").dc)
Credit
>>> print(accounting.Journal.get_by_ref("PRC").dc)
Debit
>>> accounting.Journal._meta.get_field("dc").verbose_name
'Primary booking direction'

Or in other words:

- the balance of a supplier's account with unpaid **purchase** invoices is on the **credit**
  side (we received credit from them)

- the balance of a customer's account with unpaid **sales** invoices is on the
  **debit** side (we gave them credit).

>>> print(accounting.TradeTypes.purchases.dc)
Credit
>>> print(accounting.TradeTypes.sales.dc)
Debit


Ledger info
===========

.. class:: LedgerInfo

    Django model used to store ledger specific information per user.

    .. attribute:: user

        OneToOneField pointing to the user.

    .. attribute:: entry_date

        The last value this user typed as :attr:`entry_date
        <Voucher.entry_date>` of a voucher.  It is the default value
        for every new voucher.

    .. classmethod:: get_by_user(self, user)

        Returns the ledger info entry for a given user.


Match rules
===========

.. class:: MatchRule

    Django model used to store *match rules*.


Payment terms
=============

>>> rt.show(accounting.PaymentTerms)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
==================== ==================================== ==================================== ======================================= ======== ========= ============== ================= ==========
 Reference            Designation                          Designation (fr)                     Designation (en)                        Months   Days      End of month   Payer             Informal
-------------------- ------------------------------------ ------------------------------------ --------------------------------------- -------- --------- -------------- ----------------- ----------
 07                   Zahlung sieben Tage Rechnungsdatum   Zahlung sieben Tage Rechnungsdatum   Payment seven days after invoice date   0        7         No                               No
 10                   Zahlung zehn Tage Rechnungsdatum     Zahlung zehn Tage Rechnungsdatum     Payment ten days after invoice date     0        10        No                               No
 30                   Zahlung 30 Tage Rechnungsdatum       Zahlung 30 Tage Rechnungsdatum       Payment 30 days after invoice date      0        30        No                               No
 60                   Zahlung 60 Tage Rechnungsdatum       Zahlung 60 Tage Rechnungsdatum       Payment 60 days after invoice date      0        60        No                               No
 90                   Zahlung 90 Tage Rechnungsdatum       Zahlung 90 Tage Rechnungsdatum       Payment 90 days after invoice date      0        90        No                               No
 EOM                  Zahlung Monatsende                   Zahlung Monatsende                   Payment end of month                    0        0         Yes                              No
 P30                  Anzahlung 30%                        Anzahlung 30%                        Prepayment 30%                          0        30        No                               No
 PIA                  Vorauszahlung                        Vorauszahlung                        Payment in advance                      0        0         No                               No
 robin                Cash Robin                           Cash Robin                           Cash Robin                              0        0         No             Mr Robin Dubois   No
 **Total (9 rows)**                                                                                                                     **0**    **227**
==================== ==================================== ==================================== ======================================= ======== ========= ============== ================= ==========
<BLANKLINE>


.. class:: PaymentTerm

    Django model used to store :term:`payment terms <payment term>`.

    The following fields define the default value for :attr:`due_date`:

    .. attribute:: days

        Number of days to add to :attr:`voucher_date`.

    .. attribute:: months

        Number of months to add to :attr:`voucher_date`.

    .. attribute:: end_of_month

        Whether to move :attr:`voucher_date` to the end of month.

    .. attribute:: informal

      Whether to suppress the detail ledger movements.

      An invoice with this payment term books only the total amount to the
      partner account.
      This is called "extourne automatique" in French.
      Usage example see  :ref:`invoices_to_emit`.

    .. attribute:: payer

      The payer who pays for the invoice instead of the recipient. Usage
      examples see :ref:`internal_clearings` and :ref:`invoices_to_emit`

    .. attribute:: printed_text

        Used in :xfile:`trading/VatProductInvoice/trailer.html` as
        follows::

            {% if obj.payment_term.printed_text %}
            {{parse(obj.payment_term.printed_text)}}
            {% else %}
            {{_("Payment terms")}} : {{obj.payment_term}}
            {% endif %}

    The :attr:`printed_text` field is important when using
    **prepayments** or other more complex payment terms.  Lino uses a
    rather simple approach to handle prepayment invoices: only the
    global amount and the final due date is stored in the database,
    all intermediate amounts and due dates are just generated in the
    printable document. You just define one :class:`PaymentTerm` row for each prepayment
    formula and configure your :attr:`printed_text` field. For
    example::

        Prepayment <b>30%</b>
        ({{(obj.total_incl*30)/100}} {{obj.currency}})
        due on <b>{{fds(obj.due_date)}}</b>, remaining
        {{obj.total_incl - (obj.total_incl*30)/100}} {{obj.currency}}
        due 10 days before delivery.

Payment methods
===============

.. class:: PaymentMethod

    Django model used to store :term:`payment methods <payment method>`.

    Exists only when :setting:`accounting.has_payment_methods` it `True`.

    The following fields define the default value for `due_date`:

    .. attribute:: payment_account

        Which :term:`ledger account` to book.

    .. attribute:: is_cash

        Whether this is considered a cash payment.



Actors
======


.. class:: ByJournal

  Mixin for journal-based tables of vouchers.

  Note that this is not explicitly marked as abstract by the :term:`application
  developer`, but Lino knows that it is abstract because it has no model.

  >>> accounting.ByJournal.abstract
  False
  >>> accounting.ByJournal.is_abstract()
  True


.. class:: Vouchers

    The base table for all tables working on :class:`Voucher`.

.. class:: ExpectedMovements

    A virtual table of :class:`DueMovement` rows, showing all "expected"
    "movements (payments)".

    Subclasses are :class:`DebtsByAccount` and :class:`DebtsByPartner`.

    Also subclassed by
    :class:`lino_xl.lib.finan.SuggestionsByVoucher`.

    .. attribute:: date_until

      Show only movements whose booking date is before or on the given date.

    .. attribute:: trade_type

      Show only movements in the given trade type.

    .. attribute:: from_journal

      Show only movements generated by a voucher in the given journal.

    .. attribute:: for_journal

      Show only movements that may be matched by the given journal (i.e. for
      which a match rule exists).

    .. attribute:: account

      Show only movements on the given account.

    .. attribute:: partner

      Show only movements with the given partner.

    .. attribute:: project

      Show only movements about the given project.

    .. attribute:: show_sepa

      Show only movements whose partner has a SEPA account.

    .. attribute:: same_dc

      Show only movements having the same booking direction as the target
      voucher.


.. class:: DebtsByAccount

    The :class:`ExpectedMovements` accessible by clicking the "Debts"
    action button on an account.

.. class:: DebtsByPartner

    This is the table being printed in a Payment Reminder.  Usually
    this table has one row per sales invoice which is not fully paid.
    But several invoices ("debts") may be grouped by match.  If the
    partner has purchase invoices, these are deduced from the balance.

    This table is accessible by clicking the "Debts" action button on
    a Partner.

.. class:: PartnerVouchers

    Base class for tables of partner vouchers.

    .. attribute:: cleared

        - Yes : show only completely cleared vouchers.
        - No : show only vouchers with at least one open partner movement.
        - empty: don't care about movements.


.. class:: AccountsBalance

    A virtual table, the base class for different reports that show a
    list of accounts with the following columns:

      ref description old_d old_c during_d during_c new_d new_c

    Subclasses are :class:'GeneralAccountsBalance`,
    :class:'CustomerAccountsBalance` and
    :class:'SupplierAccountsBalance`.

.. class:: GeneralAccountsBalance

    An :class:`AccountsBalance` for general accounts.

.. class:: PartnerAccountsBalance

    An :class:`AccountsBalance` for partner accounts.

.. class:: CustomerAccountsBalance

    A :class:`PartnerAccountsBalance` for the TradeType "sales".

.. class:: SuppliersAccountsBalance

    A :class:`PartnerAccountsBalance` for the TradeType "purchases".

.. class:: DebtorsCreditors

    Abstract base class for different tables showing a list of
    partners with the following columns:

      partner due_date balance actions

.. class:: Debtors

    Shows partners who have some debt against us.
    Inherits from :class:`DebtorsCreditors`.

.. class:: Creditors

    Shows partners who give us some form of credit.
    Inherits from :class:`DebtorsCreditors`.




.. _cosi.specs.accounting.movements:


.. _cosi.specs.accounting.vouchers:


.. _cosi.specs.accounting.journals:



Trade types
===========

The default list of :term:`trade types <trade type>` is:

>>> rt.show(accounting.TradeTypes)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
======= =========== ===================== ======================================================== ============================================== =============================== =====================================
 value   name        text                  Main account                                             Base account                                   Product account field           Invoice account field
------- ----------- --------------------- -------------------------------------------------------- ---------------------------------------------- ------------------------------- -------------------------------------
 S       sales       Sales                 (4000) Customers (Customers)                             (7000) Sales (Sales)                           Sales account (sales_account)
 P       purchases   Purchases             (4100) Suppliers (Suppliers)                             (6040) Purchase of goods (Purchase of goods)                                   Purchase account (purchase_account)
 W       wages       Wages                 (4200) Employees (Employees)                             (6300) Wages (Wages)
 T       taxes       Taxes                 (4500) Tax offices (Tax offices)                         (4513) VAT declared (VAT declared)
 C       clearings   Clearings             (4800) Internal clearings (Internal clearings)
 B       bank_po     Bank payment orders   (4300) Pending payment orders (Pending payment orders)
======= =========== ===================== ======================================================== ============================================== =============================== =====================================
<BLANKLINE>


.. class:: TradeTypes

    The choicelist with the *trade types* defined for this application.

    The default configuration defines the following trade types:

    .. attribute:: sales

        When you write an invoice to a customer and when the customer pays it.

    .. attribute:: purchases

        When you get an invoice from a provider and when you pay it.

    .. attribute:: wages

        When you write a payroll (declare the fact that you owe some wage to an
        employee) and later pay it (e.g. via a payment order).

    .. attribute:: clearings

        When an employee declares that he paid some invoice for you, and later
        you pay that money back to his account.  Or the employee collects money
        for a sales invoice and later returns that money to you.  See
        :ref:`internal_clearings`.

    .. attribute:: bank_po

      When you ask your bank to execute a payment, and later the bank debits
      your account.

Every trade type has the following properties.

.. class:: TradeType

    Base class for the choices of :class:`TradeTypes`.

    .. attribute:: dc

        The default booking direction.

    .. attribute:: main_account

        The common account into which the total amount of partner vouchers (base
        + taxes) and their payments should be booked.

    .. attribute:: base_account

        The default common account into which the base amount of any operation
        should be booked.

    .. attribute:: invoice_account_field_name

        The name of a field to be injected on the :class:`Partner
        <lino_xl.lib.contacts.Partner>` model which points to an
        account to be used instead of the default
        :attr:`base_account`.

    .. attribute:: base_account_field_name

        The name of a field to be injected on the :class:`Product
        <lino.modlib.products.models.Product>` database model which
        points to an account to be used instead of the default
        :attr:`base_account`.

    .. attribute:: price_field

        The name and label of the `price` field to be defined on the
        :class:`Product <lino.modlib.products.Product>` database
        model.


    .. method:: get_product_base_account(product)

        Return the account into which the **base amount** of any
        operation of this rete type should be booked.

        This is either the base account defined in the
        :attr:`base_account_field_name` for the given product, or the
        site-wide :attr:`base_account`.

    .. method:: get_catalog_price(product)

        Return the catalog price of the given product for operations
        with this trade type.

    .. method:: get_partner_invoice_account(partner)

        Return the account to use as default value for account invoice
        items.  This is the :attr:`invoice_account_field` of the given
        partner and can be `None`.




Match rules
===========

The demo database has the following :term:`match rules <match rule>`:

>>> ses.show(accounting.MatchRules)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
==== =============================== ==================================
 ID   Account                         Journal
---- ------------------------------- ----------------------------------
 1    (4000) Customers                Sales invoices (SLS)
 2    (4000) Customers                Sales credit notes (SLC)
 3    (4100) Suppliers                Purchase invoices (PRC)
 4    (4000) Customers                Payment orders Bestbank (PMO)
 5    (4100) Suppliers                Payment orders Bestbank (PMO)
 6    (4500) Tax offices              Payment orders Bestbank (PMO)
 7    (6300) Wages                    Payment orders Bestbank (PMO)
 8    (4000) Customers                Cash book (CSH)
 9    (4100) Suppliers                Cash book (CSH)
 10   (4500) Tax offices              Cash book (CSH)
 11   (6300) Wages                    Cash book (CSH)
 12   (4300) Pending payment orders   Cash book (CSH)
 13   (4000) Customers                Bestbank (BNK)
 14   (4100) Suppliers                Bestbank (BNK)
 15   (4500) Tax offices              Bestbank (BNK)
 16   (6300) Wages                    Bestbank (BNK)
 17   (4300) Pending payment orders   Bestbank (BNK)
 18   (4000) Customers                Miscellaneous transactions (MSC)
 19   (4100) Suppliers                Miscellaneous transactions (MSC)
 20   (4500) Tax offices              Miscellaneous transactions (MSC)
 21   (6300) Wages                    Miscellaneous transactions (MSC)
 22   (4300) Pending payment orders   Miscellaneous transactions (MSC)
 23   (4000) Customers                Preliminary transactions (PRE)
 24   (4100) Suppliers                Preliminary transactions (PRE)
 25   (4500) Tax offices              Preliminary transactions (PRE)
 26   (6300) Wages                    Preliminary transactions (PRE)
 27   (4300) Pending payment orders   Preliminary transactions (PRE)
 28   (4000) Customers                Paychecks (SAL)
 29   (4100) Suppliers                Paychecks (SAL)
 30   (4500) Tax offices              Paychecks (SAL)
 31   (6300) Wages                    Paychecks (SAL)
 32   (4300) Pending payment orders   Paychecks (SAL)
 33   (4500) Tax offices              VAT declarations (VAT)
==== =============================== ==================================
<BLANKLINE>


For example a :term:`payment order` can be used to pay wages and suppliers
invoices or (less frequently) to send back money that a customer had paid too
much:

>>> jnl = accounting.Journal.objects.get(ref="PMO")
>>> rt.show(accounting.MatchRulesByJournal, jnl)
====================
 Account
--------------------
 (4000) Customers
 (4100) Suppliers
 (4500) Tax offices
 (6300) Wages
====================
<BLANKLINE>

Or a sales invoice can be used to clear another sales invoice:

>>> jnl = accounting.Journal.objects.get(ref="SLS")
>>> rt.show(accounting.MatchRulesByJournal, jnl)
==================
 Account
------------------
 (4000) Customers
==================
<BLANKLINE>


Debtors
=======

**Debtors** are partners who received credit from us and therefore are
in debt towards us.

The most common debtors are customers, i.e. partners who received a sales
invoice from us and did not yet pay that invoice.

There can be debtors who are not customers.  For example a tax office. A bank is
a debtor when pending payment orders are booked to this account.  A tax office
is a debtor when we had more VAT deductible (sales) than VAT due (purchases).

>>> ses.show(accounting.Debtors, column_names="due_date partner partner_id balance")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
==================== =================================== ========= ===============
 Due date             Partner                             ID        Balance
-------------------- ----------------------------------- --------- ---------------
 10/02/2023           Dubois Robin                        80        16 827,71
 08/01/2025           Moulin Rouge                        12        4,65
 11/02/2025           Charlier Ulrike                     20        39,02
 07/03/2025           Chantraine Marc                     21        859,95
 08/03/2025           Dericum Daniel                      22        21,00
 09/03/2025           Demeulenaere Dorothée               23        3 387,78
 10/03/2025           Dobbelstein-Demeulenaere Dorothée   24        2 129,25
 **Total (7 rows)**                                       **202**   **23 269,36**
==================== =================================== ========= ===============
<BLANKLINE>


The :class:`DebtsByPartner` table shows one row
per uncleared invoice, and a list of --usually partial-- payments per invoice.
This table is used for both debtors and creditors, which can be useful when you
have business partners who are both customers and providers.

By convention, this list shows a debit balance as a negative number and a
crediting balance as a positive number.

For example here is the detail of the debts for partner 12 from above list:

>>> obj = contacts.Partner.objects.get(pk=12)
>>> obj
Partner #12 ('Moulin Rouge')
>>> ses.show(accounting.DebtsByPartner, obj)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
==================== =========== ==================== =======================================
 Due date             Balance     Debts                Payments
-------------------- ----------- -------------------- ---------------------------------------
 08/01/2025           -4,65       `SLS 2/2025 <…>`__   `BNK 1/2025 <…>`__ `BNK 2/2025 <…>`__
 **Total (1 rows)**   **-4,65**
==================== =========== ==================== =======================================
<BLANKLINE>

Here is an example of a provider to whom we owe money, i.e. the balance is
positive:

>>> obj = contacts.Partner.objects.get(pk=2)
>>> obj
Partner #2 ('Rumma & Ko OÜ')
>>> ses.show(accounting.DebtsByPartner, obj)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
==================== ============ ======= =====================
 Due date             Balance      Debts   Payments
-------------------- ------------ ------- ---------------------
 04/03/2025           144,80               `PRC 16/2025 <…>`__
 **Total (1 rows)**   **144,80**
==================== ============ ======= =====================
<BLANKLINE>


**Creditors** are partners who gave us credit, IOW to whom we owe
money.  The most common creditors are providers, i.e. partners who
sent us a purchase invoice (which we did not yet pay).

>>> ses.show(accounting.Creditors, column_names="partner partner_id balance")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
===================== ======== ==============
 Partner               ID       Balance
--------------------- -------- --------------
 Arens Annette         15       18,63
 Bestbank              1        41,40
 Rumma & Ko OÜ         2        144,80
 Bäckerei Ausdemwald   3        614,30
 Bäckerei Mießen       4        1 224,50
 Bäckerei Schmitz      5        3 307,18
 Garage Mergelsberg    6        144,90
 Donderweer BV         7        204,50
 **Total (8 rows)**    **43**   **5 700,21**
===================== ======== ==============
<BLANKLINE>

(Currently not tested because the only example is a sales invoice for partner 2 in
2014-01 that is already paid. Need to adapt some fixture to get more cases)
Partner 2 from above list is both a supplier and a customer: Note that most
numbers in above table are negative. A purchase invoice is a *credit* received
from the provider, and we asked a list of *debts* by partner.

>>> obj = contacts.Partner.objects.get(pk=2)
>>> ses.show(accounting.DebtsByPartner, obj)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF +SKIP
===================== ============ ========================= ==========================
 Due date              Balance      Debts                     Payments
--------------------- ------------ ------------------------- --------------------------
 04/01/2016            -141,30                                `PRC 2/2016 <Detail>`__
 08/01/2016            2 039,82     `SLS 2/2016 <Detail>`__
 04/02/2016            -142,00                                `PRC 9/2016 <Detail>`__
 04/03/2016            -143,40                                `PRC 16/2016 <Detail>`__
 04/04/2016            -142,10                                `PRC 23/2016 <Detail>`__
 04/05/2016            -140,20                                `PRC 30/2016 <Detail>`__
 04/06/2016            -141,30                                `PRC 37/2016 <Detail>`__
 04/07/2016            -142,00                                `PRC 44/2016 <Detail>`__
 04/08/2016            -143,40                                `PRC 51/2016 <Detail>`__
 04/09/2016            -142,10                                `PRC 58/2016 <Detail>`__
 04/10/2016            -140,20                                `PRC 65/2016 <Detail>`__
 04/11/2016            -141,30                                `PRC 72/2016 <Detail>`__
 04/12/2016            -142,00                                `PRC 79/2016 <Detail>`__
 04/01/2017            -144,80                                `PRC 2/2017 <Detail>`__
 04/02/2017            -143,50                                `PRC 9/2017 <Detail>`__
 04/03/2017            -141,60                                `PRC 16/2017 <Detail>`__
 **Total (16 rows)**   **-91,38**
===================== ============ ========================= ==========================
<BLANKLINE>


Journal groups
==============

.. class:: JournalGroup

    .. attribute:: menu_group

    The name of another plugin

    For each journal group
    there will be a menu item in the main menu.

    If the journal group has a :attr:`menu_group <JournalGroup.menu_group>`,
    then journals are added to the menu of the named plugin, otherwise to the
    menu of the accounting plugin.


.. class:: JournalGroups

    The list of possible journal groups.

    This list is used to build the main menu.
    Journals whose :attr:`journal_group <Journal.journal_group>` is
    empty will not be available through the main user menu.
    See also :attr:`JournalGroup.menu_group`.

    The default configuration defines the following journal groups:

    >>> rt.show(accounting.JournalGroups)
    ... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
    ======= =========== ============================
     value   name        text
    ------- ----------- ----------------------------
     10      sales       Sales
     20      purchases   Purchases
     30      wages       Wages
     40      financial   Financial
     50      vat         VAT
     60      misc        Miscellaneous transactions
    ======= =========== ============================
    <BLANKLINE>

    .. attribute:: sales

        For sales journals.

    .. attribute:: purchases

        For purchases journals.

    .. attribute:: wages

        For wages journals.

    .. attribute:: financial

        For financial journals (bank statements and cash reports)


.. class:: PeriodStates

    The list of possible states of an accounting period.

    .. attribute:: open

    .. attribute:: closed

Voucher types
=============

The accounting plugin defines a list of **voucher types**, a choicelist that is
populated by other plugins like :mod:`lino_xl.lib.vat`, :mod:`lino_xl.lib.trading`
or :mod:`lino_xl.lib.orders` who define some subclass of :class:`Voucher` and
then must "register" that model to be used by one or several voucher types.

Every :term:`journal` must have its voucher type, configured in the journal's
:attr:`voucher_type <Journal.voucher_type>` field.  Several
journals may share a same voucher type.  The voucher type of a journal must not
change as long as the journal has at least one voucher.


.. class:: VoucherTypes

    The list of voucher types available in this application.

    Each item is an instances of :class:`VoucherType`.

    .. method:: get_for_model()
    .. method:: get_for_table()

.. class:: VoucherType

    Base class for all items of :class:`VoucherTypes`.

    The **voucher type** defines the database model used to store
    vouchers of this type (:attr:`model`).

    In more complex cases the :term:`application developer` can define more than
    one *voucher type* per model by providing alternative tables (views) for it.

    .. attribute:: model

        The database model used to store vouchers of this type.
        A subclass of :class:`Voucher``.

    .. attribute:: table_class

        Must be a table on :attr:`model` having :attr:`master_key` set to
        the :term:`journal`.

The states of a voucher
=======================

.. class:: VoucherState

    Base class for items of :class:`VoucherStates`.

    .. attribute:: is_editable

        Whether a voucher in this state is editable.

.. class:: VoucherStates

    The list of possible states of a voucher.

    In a default configuration, vouchers can be :attr:`draft`,
    :attr:`registered`, :attr:`cancelled` or :attr:`signed`.

    >>> rt.show(accounting.VoucherStates)
    ======= ============ ============ ==========
     value   name         text         Editable
    ------- ------------ ------------ ----------
     10      draft        Draft        Yes
     20      registered   Registered   No
     30      cancelled    Cancelled    No
    ======= ============ ============ ==========
    <BLANKLINE>

    .. attribute:: draft

        *Draft* vouchers can be modified but are not yet visible as movements
        in the ledger.

    .. attribute:: registered

        *Registered* vouchers cannot be modified, but are visible as
        movements in the ledger.

    .. attribute:: cancelled

        The *Cancelled* state is similar to *Draft*, except that you cannot edit
        the fields. This is used e.g. for an invoice that has been sent, but the
        customer signaled that they don't agree. Instead of writing a credit
        nota, you can decide to just cancel the invoice.

    .. attribute:: signed

        The *Signed* state is similar to *registered*, but cannot usually be
        deregistered any more. This state is not visible in the default
        configuration. In order to make it usable, you must define a custom
        workflow for :class:`VoucherStates`.



Model mixins
============


.. class:: SequencedVoucherItem

   A :class:`VoucherItem` which also inherits from
   :class:`lino.mixins.sequenced.Sequenced`.


.. class:: AccountVoucherItem


    Abstract base class for voucher items which point to an account.

    This is also a :class:`SequencedVoucherItem`.

    This is subclassed by
    :class:`lino_xl.lib.vat.models.InvoiceItem`
    and
    :class:`lino_xl.lib.vatless.models.InvoiceItem`.

    It defines the :attr:`account` field and some related methods.

    .. attribute:: account

        ForeignKey pointing to the account (:class:`accounting.Account
        <Account>`) that is to be moved.



.. class:: VoucherItem

    Model mixin for items of a :term:`numbered voucher`.

    Makes sure that the item may not be edited when its voucher is registered.

    Subclasses must define a field named :attr:`voucher`:

    .. attribute:: voucher

        A :term:`foreign key` to the :term:`numbered voucher` that contains this
        item.  The `related_name
        <https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.ForeignKey.related_name>`__
        must be ``'items'``.


.. class:: Matching

    Model mixin for database objects that are considered *matching vouchers*.  A
    **matching voucher** is a voucher that potentially can clear some existing
    movement (fully or partially).

    The movements of a matching group are cleared if and only if the sum of
    their amounts is zero.

    Adds a field :attr:`match` and a chooser for it.  Requires a field
    `partner`.  The default implementation of the chooser for :attr:`match`
    requires a `journal`.

    Base class for :class:`lino_xl.lib.vat.AccountInvoice`,
    :class:`lino_xl.lib.trading.Invoice`, :class:`lino_xl.lib.finan.DocItem` and
    maybe others.

    .. attribute:: match

      An unique name used to group a set of :term:`movements <ledger movement>`
      that are to be :attr:`cleared <Movement.cleared>`.

.. class:: PaymentRelated

    This is base class for both (1) trade document vouchers
    (e.g. invoices or offers) and (2) for the individual entries of
    financial vouchers and ledger movements.

    .. attribute:: payment_term

        The :term:`payment term` to apply for this transaction.

        This is a pointer to :class:`PaymentTerm`.

    .. attribute:: payment_method

        The :term:`payment method` to to apply for this transaction.


.. class:: ProjectRelated

    Model mixin for objects that are related to a :attr:`project`.

    .. attribute:: project

        Pointer to the "project". This field exists only if the
        :attr:`project_model <Plugin.project_model>` setting is
        nonempty.

.. class:: Payable

    Model mixin for objects that represent a :term:`payable transaction`.

    .. attribute:: your_ref

      The reference used by the business partner for referring to this voucher.

    .. attribute:: due_date

      The date when the invoice is expected to have been paid.

    .. method:: get_payable_sums_dict(self)

        To be implemented by subclasses.  Expected to return a dict which maps
        4-tuples `(acc_tuple, project, vat_class, vat_regime)` to the payable
        amount. `acc_tuple` is itself a tuple `(general_account,
        analytic_account)`, `vat_class` is a :class:`lino_xl.lib.vat.VatClasses`
        choice and `vat_regime` a :class:`lino_xl.lib.vat.VatRegimes` choice.

    .. method:: get_wanted_movements(self)

        Implements :meth:`Voucher.get_wanted_movements`.


.. class:: PeriodRange

    Model mixin for objects that cover a range of :term:`accounting periods
    <accounting period>`.

    .. attribute:: start_period

       The first period of the range to cover.

    .. attribute:: end_period

       The last period of the range to cover.

       Leave empty if you want only one period (specified in
       :attr:`start_period`). If this is non-empty, all periods between and
       including these two are covered.

    .. method:: get_period_filter(self, voucher_prefix, **kwargs)


.. class:: PeriodRangeObservable

    Model mixin for objects that can be filtered by a range of :term:`accounting
    periods <accounting period>`. This adds two parameter fields
    :attr:`start_period` and :attr:`end_period` to every table on this model.

    Class attribute:

    .. attribute:: observable_period_field = 'accounting_period'

        The name of the database field on the observed model to use for
        filtering.


.. class:: ItemsByVoucher

    Shows the items of this voucher.

    This is used as base class for slave tables in
    :mod:`lino_xl.lib.finan`,
    :mod:`lino_xl.lib.vat`,
    :mod:`lino_xl.lib.vatless`,
    :mod:`lino_xl.lib.ana`, ...


.. _has_open_movements:

Filtering partners regarding ledger movements
=============================================

The accounting plugin adds a choice
:attr:`has_open_movements <lino_xl.lib.contacts.PartnerEvents.has_open_movements>`
to  the
:attr:`observed_events <lino_xl.lib.contacts.Partners.observed_events>`
parameter field
of the :class:`lino_xl.lib.contacts.Partners` table.

Show only companies that have at least one open ledger movement:

>>> pv = dict(observed_event=rt.models.contacts.PartnerEvents.has_open_movements)
>>> rt.login("robin").show(contacts.Companies, param_values=pv)
... #doctest: +REPORT_UDIFF +ELLIPSIS
===================== ===================================================== ================ ======= ======== ==== ==========
 Name                  Address                                               e-mail address   Phone   Mobile   ID   Language
--------------------- ----------------------------------------------------- ---------------- ------- -------- ---- ----------
 Bestbank                                                                                                      1
 Bäckerei Ausdemwald   Vervierser Straße 45, 4700 Eupen                                                        3
 Bäckerei Mießen       Gospert 103, 4700 Eupen                                                                 4
 Bäckerei Schmitz      Aachener Straße 53, 4700 Eupen                                                          5
 Donderweer BV         Edisonstraat 12, 4816 AR Breda, Netherlands                                             7
 Garage Mergelsberg    Hauptstraße 13, 4730 Raeren                                                             6
 Moulin Rouge          Boulevard de Clichy 82, 75018 Paris, France                                             12
 Rumma & Ko OÜ         Uus tn 1, Vigala vald, 78003 Rapla maakond, Estonia                                     2
===================== ===================================================== ================ ======= ======== ==== ==========
<BLANKLINE>


>>> settings.SITE.the_demo_date
datetime.date(2025, 3, 12)

>>> pv['start_date'] = i2d(20241231)
>>> rt.login("robin").show(contacts.Companies, param_values=pv)
... #doctest: +REPORT_UDIFF +ELLIPSIS
===================== ===================================================== ================ ======= ======== ==== ==========
 Name                  Address                                               e-mail address   Phone   Mobile   ID   Language
--------------------- ----------------------------------------------------- ---------------- ------- -------- ---- ----------
 Bestbank                                                                                                      1
 Bäckerei Ausdemwald   Vervierser Straße 45, 4700 Eupen                                                        3
 Bäckerei Mießen       Gospert 103, 4700 Eupen                                                                 4
 Bäckerei Schmitz      Aachener Straße 53, 4700 Eupen                                                          5
 Donderweer BV         Edisonstraat 12, 4816 AR Breda, Netherlands                                             7
 Garage Mergelsberg    Hauptstraße 13, 4730 Raeren                                                             6
 Moulin Rouge          Boulevard de Clichy 82, 75018 Paris, France                                             12
 Rumma & Ko OÜ         Uus tn 1, Vigala vald, 78003 Rapla maakond, Estonia                                     2
===================== ===================================================== ================ ======= ======== ==== ==========
<BLANKLINE>


>>> pv['start_date'] = i2d(20251231)
>>> rt.login("robin").show(contacts.Companies, param_values=pv)
... #doctest: -REPORT_UDIFF +ELLIPSIS
No data to display


Utilities
=========

.. class:: DueMovement

    A volatile object representing a group of matching movements.

    A **due movement** is a movement which a partner should do in
    order to clear their debt.  Or which we should do in order to
    clear our debt towards a partner.

    The "matching" movements of a given movement are those whose
    `match`, `partner` and `account` fields have the same values.

    These movements are themselves grouped into "debts" and "payments".
    A "debt" increases the debt and a "payment" decreases it.

    .. attribute:: match

        The common `match` name of these movements.

    .. attribute:: dc

        Whether I mean *my* debts and payments (towards that partner)
        or those *of the partner* (towards me).

    .. attribute:: partner

    .. attribute:: account


.. function:: get_due_movements(dc, flt)

    Generates a series of :class:`DueMovement` objects which --if they were
    booked-- would clear the movements given by the filter condition `flt`.

    There will be at most one :class:`DueMovement` per `(account, partner,
    project, match)`, each of them grouping the movements with same partner,
    account, project and match.

    This is the data source for :class:`ExpectedMovements` and subclasses.

    The balances of the :class:`DueMovement` objects will be positive or
    negative depending on the specified `dc`.

    Arguments:

    :dc: (boolean): The target booking direction, i.e. which direction should
         be considered positive. Open movements in the opposite direction will be
         negative.

    :flt: Optional filter arguments to give to Django's `filter()
          <https://docs.djangoproject.com/en/5.0/ref/models/querysets/#filter>`_
          method in order to specifiy which :class:`Movement` objects
          to consider.

.. function:: check_clearings(qs, matches=[])

    Check whether involved movements are cleared or not, and update
    their :attr:`cleared` field accordingly.

.. function:: check_clearings_by_account(account, matches=[])

    Call :func:`check_clearings` for the given ledger account.

.. function:: check_clearings_by_partner(partner, matches=[])

    Call :func:`check_clearings` for the given partner.


Plugin attributes
=================

See :class:`Plugin`.


Mixins
======

.. class:: AccountBalances

    A table which shows a list of general ledger accounts during the
    observed period, showing their old and new balances and the sum of
    debit and credit movements.



Data exchange with other systems
================================

.. glossary::

  XML file

    For some types of numbered vouchers, Lino can write an XML file in an
    appropriate format for this voucher.

    For example a :term:`product invoice` can generate a :term:`PEPPOL`
    compliant XML file, or a :term:`payment order` a :term:`SEPA` compliant XML
    file.


The `on_ledger_movement` signal
===============================

.. data:: on_ledger_movement

    Custom signal sent when a partner has had at least one change in a
    ledger movement.

    - `sender`   the database model
    - `instance` the partner

Don't read me
=============

Until 20181016 it was not possible to manually reverse the sort order
of a virtual field having a sortable_by which contained itself a
reversed field.  The :attr:`Movement.credit` field is an example:

>>> rmu(accounting.Movement.get_data_elem('credit').sortable_by)
['-amount', 'value_date']

>>> par = contacts.Partner.objects.get(pk=10)
>>> rt.show(accounting.MovementsByPartner, par, nosummary=True)
============ ===================== ============================================================== ============== ============== ============= =========
 Value date   Voucher               Description                                                    Debit          Credit         Match         Cleared
------------ --------------------- -------------------------------------------------------------- -------------- -------------- ------------- ---------
 21/01/2025   `BNK 1/2025 <…>`__    `(4000) Customers <…>`__ | `Bernd Brechts Bücherladen <…>`__                  222,00         SLS 57/2024   Yes
 21/12/2024   `BNK 12/2024 <…>`__   `(4000) Customers <…>`__ | `Bernd Brechts Bücherladen <…>`__                  518,00         SLS 57/2024   Yes
 14/12/2024   `SLS 57/2024 <…>`__   `(4000) Customers <…>`__                                       740,00                        SLS 57/2024   Yes
 21/03/2023   `BNK 3/2023 <…>`__    `(4000) Customers <…>`__ | `Bernd Brechts Bücherladen <…>`__                  320,00         SLS 10/2023   Yes
 07/03/2023   `SLS 10/2023 <…>`__   `(4000) Customers <…>`__                                       320,00                        SLS 10/2023   Yes
                                    **Balance 0.00 (5 movements)**                                 **1 060,00**   **1 060,00**
============ ===================== ============================================================== ============== ============== ============= =========
<BLANKLINE>


>>> mt = contenttypes.ContentType.objects.get_for_model(par.__class__).pk
>>> url = "api/accounting/MovementsByPartner?fmt=json&mk={}&mt={}".format(par.pk, mt)
>>> cols = 'count html_text no_data_text overridden_column_headers rows success title param_values'
>>> demo_get('robin', url + "&sort=credit&dir=ASC", cols, 5)

The following failed before 20181016:

>>> demo_get('robin', url + "&sort=credit&dir=DESC", cols, 5)


Templates
=========

.. xfile:: payment_reminder.body.html

  Defines the body text of a payment reminder.

.. xfile:: base.weasy.html
.. xfile:: payment_reminder.weasy.html

  Defines the body text of a payment reminder.


Generating counter-entries
==========================

A payment order generates counter entries

If you want Lino to suggest the cleaning of payment orders when entering bank
statements, then create  a  an organization (:class:`contacts.Company`)
representing your bank and have the :attr:`Journal.partner` field point to that
partner.

Note that the journal must also have an :attr:`account` with
:attr:`Account.needs_partner` enabled in order to prevent Lino from generating
detailed counter-entries (one per item). Clearing a payment order makes sense
only when the counter-entry is  the sum of all movements.

The :manage:`reregister` admin command
======================================

In certain exceptional situations you may want to rebuild all the :term:`ledger
movements <ledger movement>` on your site.  For example after the changes on
2020-10-15 (see :ref:`xl.changes.2020`). Or when you have changed something in
your site configuration so that certain movements would go to other accounts
than before (and want to apply this change to all registered vouchers).

The :manage:`reregister` admin command re-registers all numbered vouchers.


.. management_command:: reregister

Example run:

>>> from atelier.sheller import Sheller
>>> shell = Sheller(settings.SITE.project_dir)
>>> shell('python manage.py reregister --help')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
usage: manage.py reregister [-h] [--noinput] [--version] [-v {0,1,2,3}]
                            [--settings SETTINGS] [--pythonpath PYTHONPATH]
                            [--traceback] [--no-color] [--force-color]
                            [--skip-checks]
<BLANKLINE>
Re-register all numbered vouchers. If no arguments are given, run it on all
vouchers. Otherwise every positional argument is expected to be the ref of a
journal. When called with no arguments, all movements are deleted from the
database. This can help if the database contains movements with invalid voucher
pointer.
<BLANKLINE>
options:
  -h, --help            show this help message and exit
  --noinput             Do not prompt for input of any kind.
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output,
                        2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g.
                        "myproject.settings.main". If this isn't provided, the
                        DJANGO_SETTINGS_MODULE environment variable will be
                        used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g.
                        "/home/djangoprojects/myproject".
  --traceback           Display a full stack trace on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.

>>> shell('python manage.py reregister --noinput')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
Re-register all vouchers in journal Verkaufsrechnungen (SLS)
Re-register all vouchers in journal Gutschriften Verkauf (SLC)
Re-register all vouchers in journal Einkaufsrechnungen (PRC)
Re-register all vouchers in journal Zahlungsaufträge Bestbank (PMO)
Re-register all vouchers in journal Kassenbuch (CSH)
Re-register all vouchers in journal Bestbank (BNK)
Re-register all vouchers in journal Diverse Buchungen (MSC)
Re-register all vouchers in journal Preliminary transactions (PRE)
Re-register all vouchers in journal Lohnscheine (SAL)
Re-register all vouchers in journal MwSt.-Erklärungen (VAT)
Re-register all vouchers in journal Eingangsdokumente (INB)
397 vouchers have been re-registered.
Check clearings for all partners

..

  check_virgin() would alert because the movements have new ids after running
  reregister, but we can safely assume that it's actually the same data, so we
  mark it as virgin:

  >>> dbhash.mark_virgin()
