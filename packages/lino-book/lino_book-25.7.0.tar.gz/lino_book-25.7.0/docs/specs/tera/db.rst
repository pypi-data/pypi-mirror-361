.. doctest docs/specs/tera/db.rst
.. _specs.tera.db:

===============================
Database structure in Lino Tera
===============================

.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.tera1.settings')
>>> from lino.api.doctest import *


Complexity factors
==================

>>> print(analyzer.show_complexity_factors())
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
- 51 plugins
- 101 models
- 4 user types
- 378 views
- 34 dialog actions
<BLANKLINE>

Journals overview
=================

>>> rt.show(accounting.JournalsOverview)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
| **SLS** |  47 Sales invoices |
|---------|--------------------|
| **SLC** |  0 Sales credit notes |
|---------|-----------------------|
| **PRC** |  35 Purchase invoices |
|---------|-----------------------|
| **PMO** |  4 Payment orders Bestbank |
|---------|----------------------------|
| **CSH** |  0 Cash book |
|---------|--------------|
| **BNK** |  4 Bestbank |
|---------|-------------|
| **MSC** |  0 Miscellaneous transactions |
|---------|-------------------------------|
| **PRE** |  1 Preliminary transactions |
|---------|-----------------------------|
| **SAL** |  0 Paychecks |
|---------|--------------|
| **VAT** |  3 VAT declarations |
|---------|---------------------|




The database models
===================

>>> analyzer.show_db_overview()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
51 plugins: lino, about, ipdict, jinja, bootstrap3, extjs, printing, system, users, contenttypes, gfks, help, office, xl, excerpts, courses, dashboard, countries, contacts, households, clients, healthcare, products, memo, linod, checkdata, periods, weasyprint, uploads, accounting, bevats, vat, trading, cal, calview, invoicing, sepa, finan, ana, sheets, topics, notes, appypod, export_excel, tinymce, tera, teams, lists, search, staticfiles, sessions.
101 models:
=========================== ============================== ========= =======
 Name                        Default table                  #fields   #rows
--------------------------- ------------------------------ --------- -------
 accounting.Account          accounting.Accounts            21        21
 accounting.Journal          accounting.Journals            27        10
 accounting.LedgerInfo       accounting.LedgerInfoTable     2         0
 accounting.MatchRule        accounting.MatchRules          3         33
 accounting.Movement         accounting.Movements           12        321
 accounting.PaymentTerm      accounting.PaymentTerms        12        8
 accounting.Voucher          accounting.AllVouchers         9         94
 ana.Account                 ana.Accounts                   6         20
 ana.AnaAccountInvoice       ana.Invoices                   21        35
 ana.InvoiceItem             ana.InvoiceItemTable           10        55
 bevats.Declaration          bevats.Declarations            29        3
 cal.Calendar                cal.Calendars                  6         1
 cal.EntryRepeater           cal.EntryRepeaterTable         17        0
 cal.Event                   cal.Events                     27        363
 cal.EventPolicy             cal.EventPolicies              20        6
 cal.EventType               cal.EventTypes                 24        6
 cal.Guest                   cal.Guests                     7         280
 cal.GuestRole               cal.GuestRoles                 6         2
 cal.RecurrentEvent          cal.RecurrentEvents            22        15
 cal.RemoteCalendar          cal.RemoteCalendars            7         0
 cal.Room                    cal.Rooms                      10        0
 cal.Subscription            cal.Subscriptions              4         0
 cal.Task                    cal.Tasks                      17        0
 calview.DailyPlannerRow     calview.DailyPlannerRows       7         2
 checkdata.Message           checkdata.Messages             6         0
 clients.ClientContact       clients.ClientContacts         7         0
 clients.ClientContactType   clients.ClientContactTypes     5         0
 contacts.Company            contacts.Companies             29        30
 contacts.CompanyType        contacts.CompanyTypes          7         16
 contacts.Partner            contacts.Partners              27        105
 contacts.Person             contacts.Persons               34        69
 contacts.Role               contacts.Roles                 4         3
 contacts.RoleType           contacts.RoleTypes             5         5
 contenttypes.ContentType    gfks.ContentTypes              3         101
 countries.Country           countries.Countries            6         10
 countries.Place             countries.Places               9         80
 courses.Course              courses.Activities             44        52
 courses.Enrolment           courses.Enrolments             15        78
 courses.Line                courses.Lines                  25        3
 courses.Slot                courses.Slots                  5         0
 courses.Topic               courses.Topics                 4         0
 dashboard.Widget            dashboard.Widgets              5         0
 excerpts.Excerpt            excerpts.Excerpts              12        52
 excerpts.ExcerptType        excerpts.ExcerptTypes          17        9
 finan.BankStatement         finan.BankStatements           17        4
 finan.BankStatementItem     finan.BankStatementItemTable   9         55
 finan.JournalEntry          finan.FinancialVouchers        15        1
 finan.JournalEntryItem      finan.JournalEntryItemTable    9         4
 finan.PaymentOrder          finan.PaymentOrders            16        4
 finan.PaymentOrderItem      finan.PaymentOrderItemTable    9         32
 healthcare.Plan             healthcare.Plans               4         5
 healthcare.Rule             healthcare.Rules               6         0
 healthcare.Situation        healthcare.Situations          6         0
 households.Household        households.Households          30        6
 households.Member           households.Members             14        12
 households.Type             households.Types               4         6
 invoicing.FollowUpRule      invoicing.FollowUpRules        5         3
 invoicing.Item              invoicing.Items                10        0
 invoicing.Plan              invoicing.Plans                8         1
 invoicing.Tariff            invoicing.Tariffs              8         2
 invoicing.Task              invoicing.Tasks                29        1
 linod.SystemTask            linod.SystemTasks              25        0
 lists.List                  lists.Lists                    7         8
 lists.ListType              lists.ListTypes                4         3
 lists.Member                lists.Members                  5         105
 memo.Mention                memo.Mentions                  5         0
 notes.EventType             notes.EventTypes               8         1
 notes.Note                  notes.Notes                    17        100
 notes.NoteType              notes.NoteTypes                11        3
 periods.StoredPeriod        periods.StoredPeriods          7         6
 periods.StoredYear          periods.StoredYears            5         6
 products.Category           products.Categories            15        2
 products.PriceRule          products.PriceRules            7         3
 products.Product            products.Products              21        7
 sepa.Account                sepa.Accounts                  6         31
 sessions.Session            users.Sessions                 3         ...
 sheets.AccountEntry         sheets.AccountEntries          7         12
 sheets.AnaAccountEntry      sheets.AnaAccountEntries       7         15
 sheets.Item                 sheets.Items                   9         29
 sheets.ItemEntry            sheets.ItemEntries             7         16
 sheets.PartnerEntry         sheets.PartnerEntries          8         48
 sheets.Report               sheets.Reports                 6         1
 system.SiteConfig           system.SiteConfigs             10        1
 teams.Team                  teams.Teams                    5         2
 tera.Client                 tera.Clients                   44        58
 tera.LifeMode               tera.LifeModes                 4         0
 tera.Procurer               tera.Procurers                 4         0
 tinymce.TextFieldTemplate   tinymce.TextFieldTemplates     5         2
 topics.Tag                  topics.Tags                    4         86
 topics.Topic                topics.Topics                  4         3
 trading.InvoiceItem         trading.InvoiceItems           16        76
 trading.PaperType           trading.PaperTypes             5         2
 trading.TradingRule         trading.TradingRules           6         93
 trading.VatProductInvoice   trading.Invoices               29        47
 uploads.Upload              uploads.Uploads                12        9
 uploads.UploadType          uploads.UploadTypes            8         2
 uploads.Volume              uploads.Volumes                4         1
 users.Authority             users.Authorities              3         0
 users.User                  users.AllUsers                 24        6
 vat.InvoiceItem             vat.InvoiceItemTable           9         0
 vat.VatAccountInvoice       vat.Invoices                   21        0
=========================== ============================== ========= =======
<BLANKLINE>



Foreign Keys and their `on_delete` setting
==========================================

Here is a list of foreign keys in :ref:`tera` and their on_delete
behaviour. See also :doc:`/dev/delete`.

>>> from lino.utils.diag import analyzer
>>> print(analyzer.show_foreign_keys())
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
- accounting.Account :
  - PROTECT : accounting.Journal.account, accounting.MatchRule.account, accounting.Movement.account, ana.InvoiceItem.account, finan.BankStatement.item_account, finan.BankStatementItem.account, finan.JournalEntry.item_account, finan.JournalEntryItem.account, finan.PaymentOrder.item_account, finan.PaymentOrderItem.account, sheets.AccountEntry.account, vat.InvoiceItem.account
- accounting.Journal :
  - CASCADE : accounting.MatchRule.journal, invoicing.FollowUpRule.source_journal
  - PROTECT : accounting.Voucher.journal, invoicing.Task.target_journal
- accounting.PaymentTerm :
  - PROTECT : ana.AnaAccountInvoice.payment_term, bevats.Declaration.payment_term, courses.Course.payment_term, trading.TradingRule.payment_term, trading.VatProductInvoice.payment_term, vat.VatAccountInvoice.payment_term
- accounting.Voucher :
  - CASCADE : accounting.Movement.voucher
  - PROTECT : ana.AnaAccountInvoice.voucher_ptr, bevats.Declaration.voucher_ptr, finan.BankStatement.voucher_ptr, finan.JournalEntry.voucher_ptr, finan.PaymentOrder.voucher_ptr, trading.VatProductInvoice.voucher_ptr, vat.VatAccountInvoice.voucher_ptr
  - SET_NULL : invoicing.Item.invoice
- ana.Account :
  - PROTECT : accounting.Account.ana_account, accounting.Movement.ana_account, ana.InvoiceItem.ana_account, sheets.AnaAccountEntry.ana_account
- ana.AnaAccountInvoice :
  - CASCADE : ana.InvoiceItem.voucher
- cal.Calendar :
  - CASCADE : cal.Subscription.calendar
  - PROTECT : cal.Room.calendar, system.SiteConfig.site_calendar
- cal.Event :
  - CASCADE : cal.Guest.event
  - PROTECT : cal.EntryRepeater.cal_entry
- cal.EventType :
  - PROTECT : cal.Event.event_type, cal.EventPolicy.event_type, cal.RecurrentEvent.event_type, courses.Line.event_type, products.PriceRule.selector, system.SiteConfig.default_event_type, users.User.event_type
- cal.GuestRole :
  - PROTECT : cal.Guest.role, courses.Enrolment.guest_role, courses.Line.guest_role, system.SiteConfig.pupil_guestrole
- cal.Room :
  - PROTECT : cal.Event.room, courses.Course.room
- clients.ClientContactType :
  - PROTECT : clients.ClientContact.type, contacts.Partner.client_contact_type
- contacts.Company :
  - PROTECT : accounting.Journal.partner, cal.Room.company, clients.ClientContact.company, contacts.Role.company, courses.Line.company, excerpts.Excerpt.company, healthcare.Plan.provider, notes.Note.company
- contacts.CompanyType :
  - PROTECT : contacts.Company.type
- contacts.Partner :
  - CASCADE : contacts.Company.partner_ptr, contacts.Person.partner_ptr, courses.Course.partner, households.Household.partner_ptr, invoicing.Item.partner, lists.Member.partner, sepa.Account.partner, trading.TradingRule.partner
  - PROTECT : accounting.Movement.partner, ana.AnaAccountInvoice.partner, bevats.Declaration.partner, clients.ClientContact.client, finan.BankStatementItem.partner, finan.JournalEntryItem.partner, finan.PaymentOrderItem.partner, invoicing.Plan.partner, sheets.PartnerEntry.partner, trading.TradingRule.invoice_recipient, trading.VatProductInvoice.partner, users.User.partner, vat.VatAccountInvoice.partner
- contacts.Person :
  - CASCADE : tera.Client.person_ptr
  - PROTECT : cal.Guest.partner, cal.Room.contact_person, clients.ClientContact.contact_person, contacts.Role.person, courses.Enrolment.pupil, courses.Line.contact_person, excerpts.Excerpt.contact_person, healthcare.Situation.client, households.Member.person, notes.Note.contact_person
- contacts.RoleType :
  - PROTECT : cal.Room.contact_role, clients.ClientContact.contact_role, contacts.Role.type, courses.Line.contact_role, excerpts.Excerpt.contact_role, notes.Note.contact_role
- contenttypes.ContentType :
  - PROTECT : accounting.Journal.default_invoiceable_type, cal.Event.owner_type, cal.Task.owner_type, checkdata.Message.owner_type, excerpts.Excerpt.owner_type, excerpts.ExcerptType.content_type, invoicing.FollowUpRule.invoice_generator, invoicing.Item.generator_type, memo.Mention.owner_type, memo.Mention.target_type, notes.Note.owner_type, topics.Tag.owner_type, trading.InvoiceItem.invoiceable_type, uploads.Upload.owner_type
- countries.Country :
  - PROTECT : contacts.Partner.country, countries.Place.country, tera.Client.nationality
- countries.Place :
  - PROTECT : contacts.Partner.city, contacts.Partner.region, countries.Place.parent
- courses.Course :
  - PROTECT : cal.Event.project, cal.Task.project, courses.Enrolment.course, excerpts.Excerpt.project, invoicing.Plan.order, notes.Note.project
- courses.Line :
  - PROTECT : courses.Course.line
- courses.Slot :
  - PROTECT : courses.Course.slot
- courses.Topic :
  - PROTECT : courses.Line.topic
- excerpts.Excerpt :
  - SET_NULL : bevats.Declaration.printed_by, courses.Enrolment.printed_by, finan.BankStatement.printed_by, finan.JournalEntry.printed_by, finan.PaymentOrder.printed_by, sheets.Report.printed_by, trading.VatProductInvoice.printed_by
- excerpts.ExcerptType :
  - PROTECT : excerpts.Excerpt.excerpt_type
- finan.BankStatement :
  - CASCADE : finan.BankStatementItem.voucher
- finan.JournalEntry :
  - CASCADE : finan.JournalEntryItem.voucher
- finan.PaymentOrder :
  - CASCADE : finan.PaymentOrderItem.voucher
- healthcare.Plan :
  - PROTECT : courses.Course.healthcare_plan, healthcare.Rule.plan, healthcare.Situation.healthcare_plan
- households.Household :
  - CASCADE : households.Member.household
- households.Type :
  - PROTECT : households.Household.type
- invoicing.Plan :
  - CASCADE : invoicing.Item.plan
- invoicing.Task :
  - CASCADE : invoicing.FollowUpRule.invoicing_task
  - PROTECT : invoicing.Plan.invoicing_task
- lists.List :
  - CASCADE : lists.Member.list
- lists.ListType :
  - PROTECT : lists.List.list_type
- notes.EventType :
  - PROTECT : notes.Note.event_type, system.SiteConfig.system_note_type
- notes.NoteType :
  - PROTECT : notes.Note.type
- periods.StoredPeriod :
  - PROTECT : accounting.Voucher.accounting_period, bevats.Declaration.end_period, bevats.Declaration.start_period, sheets.Report.end_period, sheets.Report.start_period
- periods.StoredYear :
  - PROTECT : accounting.Voucher.fiscal_year, periods.StoredPeriod.year
- products.Category :
  - PROTECT : courses.Line.fees_cat, courses.Line.options_cat, products.Category.parent, products.Product.category
- products.Product :
  - PROTECT : courses.Enrolment.option, courses.Line.fee, healthcare.Rule.client_fee, healthcare.Rule.provider_fee, invoicing.Tariff.product, products.PriceRule.product, trading.InvoiceItem.product, users.User.cash_daybook
- sepa.Account :
  - PROTECT : accounting.Journal.sepa_account, finan.PaymentOrderItem.bank_account
- sheets.Item :
  - PROTECT : accounting.Account.sheet_item, sheets.ItemEntry.item
- sheets.Report :
  - CASCADE : sheets.AccountEntry.report, sheets.AnaAccountEntry.report, sheets.ItemEntry.report, sheets.PartnerEntry.report
- teams.Team :
  - PROTECT : courses.Course.team, users.User.team
- tera.Client :
  - PROTECT : tera.Client.obsoletes
- tera.LifeMode :
  - PROTECT : tera.Client.life_mode
- tera.Procurer :
  - PROTECT : courses.Course.procurer
- topics.Topic :
  - PROTECT : topics.Tag.topic
- trading.PaperType :
  - PROTECT : courses.Course.paper_type, trading.TradingRule.paper_type, trading.VatProductInvoice.paper_type
- trading.VatProductInvoice :
  - CASCADE : trading.InvoiceItem.voucher
- uploads.UploadType :
  - PROTECT : uploads.Upload.type
- uploads.Volume :
  - PROTECT : accounting.Journal.uploads_volume, uploads.Upload.volume
- users.User :
  - CASCADE : accounting.LedgerInfo.user, cal.Subscription.user
  - PROTECT : accounting.Voucher.user, cal.Event.assigned_to, cal.Event.user, cal.RecurrentEvent.user, cal.Task.user, checkdata.Message.user, courses.Course.teacher, courses.Course.user, courses.Enrolment.user, dashboard.Widget.user, excerpts.Excerpt.user, invoicing.Plan.user, invoicing.Task.user, notes.Note.user, sheets.Report.user, tera.Client.user, tinymce.TextFieldTemplate.user, uploads.Upload.user, users.Authority.authorized, users.Authority.user
- vat.VatAccountInvoice :
  - CASCADE : vat.InvoiceItem.voucher
<BLANKLINE>
