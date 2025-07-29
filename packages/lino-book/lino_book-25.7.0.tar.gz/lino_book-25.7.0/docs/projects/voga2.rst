.. doctest docs/projects/voga2.rst
.. _book.projects.voga2:
.. _voga.specs.roger:
.. _voga.specs.db_roger:

===========================================
``voga2`` : A customized Lino Voga site
===========================================

.. module:: lino_book.projects.voga2

A :ref:`voga` site with a few local customizations.

Used in :doc:`/specs/voga/index`.

The :mod:`lino_book.projects.voga2` demo project illustrates some local
customizations.


.. contents::
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.voga2.startup import *

A customized management of membership fees
==========================================

The :mod:`lino_voga.lib.roger.courses` plugin demonstrates the following rules
for handling memberships:

- Membership costs 15€ per year.
- Members get a discount on enrolments to courses.
- Customers can freely decide whether they want to be members or not.
- They become member by paying the membership fee.

To handle these rules, we have an additional field :attr:`member_until
<lino_voga.lib.roger.courses.Pupil.member_until>` on
each pupil.

There is a custom data checker
:class:`lino_voga.lib.roger.courses.MemberChecker`


>>> dd.demo_date()
datetime.date(2015, 5, 22)


>>> rt.show(courses.Pupils)
... #doctest: +ELLIPSIS +REPORT_UDIFF
========================================== ================================= ================== ============ ===== ===== ======== ==============
 Name                                       Address                           Participant type   Section      LFV   CKK   Raviva   Mitglied bis
------------------------------------------ --------------------------------- ------------------ ------------ ----- ----- -------- --------------
 Hans Altenberg (MES)                       Aachener Straße, 4700 Eupen       Member             Eupen        No    No    No       31/12/2015
 Annette Arens (MEL)                        Alter Malmedyer Weg, 4700 Eupen   Helper                          Yes   No    No       31/12/2015
 Laurent Bastiaensen (MEC)                  Am Berg, 4700 Eupen               Non-member                      No    Yes   No       31/12/2015
 Bernd Brecht (MEC)                         Aachen, Germany                   Member                          No    Yes   No       31/12/2015
 Ulrike Charlier (MELS)                     Auenweg, 4700 Eupen               Helper             Nidrum       Yes   No    No       31/12/2015
 Dorothée Demeulenaere (ME)                 Auf'm Rain, 4700 Eupen            Non-member                      No    No    No       31/12/2016
 ...
 Hedi Radermacher (ME)                      4730 Raeren                       Non-member                      No    No    No       31/12/2015
 Jean Radermacher (MS)                      4730 Raeren                       Member             Elsenborn    No    No    No
 Marie-Louise Vandenmeulenbos (MEL)         Amsterdam, Netherlands            Helper                          Yes   No    No       31/12/2015
 Didier di Rupo (MEL)                       4730 Raeren                       Non-member                      Yes   No    No       31/12/2015
 Erna Ärgerlich (ML)                        4730 Raeren                       Member                          Yes   No    No
 Otto Östges (ME)                           4730 Raeren                       Helper                          No    No    No       31/12/2015
========================================== ================================= ================== ============ ===== ===== ======== ==============
<BLANKLINE>



>>> print(dd.plugins.accounting.suppress_movements_until)
None

>>> rt.show(checkdata.MessagesByChecker, 'courses.MemberChecker')
============= ============================================ ==========================================
 Responsible   Database object                              Message text
------------- -------------------------------------------- ------------------------------------------
 Robin Rood    `Karl Kaivers (MEC) <…>`__                   Member until 2015-12-31, but no payment.
 Robin Rood    `Josefine Leffin (ME) <…>`__                 Member until 2015-12-31, but no payment.
 Robin Rood    `Erna Emonts-Gast (ME) <…>`__                Member until 2015-12-31, but no payment.
 Robin Rood    `Alfons Radermacher (MEC) <…>`__             Member until 2015-12-31, but no payment.
 Robin Rood    `Edgard Radermacher (ME) <…>`__              Member until 2015-12-31, but no payment.
 Robin Rood    `Hedi Radermacher (ME) <…>`__                Member until 2015-12-31, but no payment.
 Robin Rood    `Didier di Rupo (MEL) <…>`__                 Member until 2015-12-31, but no payment.
 Robin Rood    `Otto Östges (ME) <…>`__                     Member until 2015-12-31, but no payment.
 Robin Rood    `Mark Martelaer (ME) <…>`__                  Member until 2015-12-31, but no payment.
 Robin Rood    `Marie-Louise Vandenmeulenbos (MEL) <…>`__   Member until 2015-12-31, but no payment.
 Robin Rood    `Lisa Lahm (ME) <…>`__                       Member until 2015-12-31, but no payment.
 Robin Rood    `Bernd Brecht (MEC) <…>`__                   Member until 2015-12-31, but no payment.
 Robin Rood    `Jérôme Jeanémart (ME) <…>`__                Member until 2015-12-31, but no payment.
============= ============================================ ==========================================
<BLANKLINE>


>>> acc = rt.models.accounting.CommonAccounts.membership_fees.get_object()
>>> print(acc)
(7310) Membership fees

>>> rt.show(accounting.MovementsByAccount, acc)
============ ==================== =========================================== ======= ============ =============
 Value date   Voucher              Description                                 Debit   Credit       Match
------------ -------------------- ------------------------------------------- ------- ------------ -------------
 22/12/2015   `CSH 5/2015 <…>`__   `Faymonville Luc <…>`__                             15,00        **CSH 5:1**
 22/12/2015   `CSH 5/2015 <…>`__   `Groteclaes Gregory <…>`__                          15,00        **CSH 5:2**
 22/12/2015   `CSH 5/2015 <…>`__   `Hilgers Hildegard <…>`__                           15,00        **CSH 5:3**
 22/12/2015   `CSH 5/2015 <…>`__   `Jacobs Jacqueline <…>`__                           15,00        **CSH 5:4**
 22/12/2015   `CSH 5/2015 <…>`__   `Jonas Josef <…>`__                                 15,00        **CSH 5:5**
 22/11/2015   `CSH 4/2015 <…>`__   `Dobbelstein-Demeulenaere Dorothée <…>`__           15,00        **CSH 4:1**
 22/11/2015   `CSH 4/2015 <…>`__   `Emonts Daniel <…>`__                               15,00        **CSH 4:3**
 22/11/2015   `CSH 4/2015 <…>`__   `Engels Edgar <…>`__                                15,00        **CSH 4:4**
 22/11/2015   `CSH 4/2015 <…>`__   `Evers Eberhart <…>`__                              15,00        **CSH 4:2**
 22/10/2015   `CSH 3/2015 <…>`__   `Demeulenaere Dorothée <…>`__                       15,00        **CSH 3:2**
 22/10/2015   `CSH 3/2015 <…>`__   `Dericum Daniel <…>`__                              15,00        **CSH 3:1**
 22/02/2015   `CSH 2/2015 <…>`__   `Charlier Ulrike <…>`__                             15,00        **CSH 2:1**
 22/01/2015   `CSH 1/2015 <…>`__   `Altenberg Hans <…>`__                              15,00        **CSH 1:2**
 22/01/2015   `CSH 1/2015 <…>`__   `Arens Annette <…>`__                               15,00        **CSH 1:1**
 22/01/2015   `CSH 1/2015 <…>`__   `Bastiaensen Laurent <…>`__                         15,00        **CSH 1:3**
                                   **Balance -225.00 (15 movements)**                  **225,00**
============ ==================== =========================================== ======= ============ =============
<BLANKLINE>


Django and the VatVoucher model mixin
=====================================

This section is no longer needed since 20230829. It helped us to discover that
when you call :meth:`contenttypes.ContentType.objects.get_for_model` with an
abstract Model class, Django creates a contenttype database record. We then
optimized :meth:`lino_react.react.Renderer.actor2json` to not fall into that pit
anymore.

The code snippets in this section are not actively tested, but you may remove
the  ``#doctest: +SKIP`` and play.

The contenttypes framework seems to sometimes create an entry for the
VatVoucher model mixin although this is an abstract model.

>>> from django.apps import apps
>>> cts = set([ct.model_class() for ct in contenttypes.ContentType.objects.all()])
>>> for m in apps.get_models():
...     if m in cts:
...         cts.remove(m)
>>> cts  #doctest: +SKIP
{None}
>>> for ct in contenttypes.ContentType.objects.all():  #doctest: +SKIP
...   if ct.model_class() is None:
...     print(ct)
vatvoucher

This is caused by the following method:

>>> get_for_model = contenttypes.ContentType.objects.get_for_model

When passing a non-existed Model class (that is abstract) it creates a
contenttype database record. For example see how the contenttype count
increasing when looking up abstract models:

>>> contenttypes.ContentType.objects.count()  #doctest: +SKIP
92

>>> users.UserAuthored._meta.abstract, contenttypes.ContentType.objects.filter(model="userauthored").count()  #doctest: +SKIP
(True, 0)

Now see when we look it up using get_for_model method:

>>> get_for_model(users.UserAuthored)  #doctest: +SKIP
<ContentType: userauthored>

>>> contenttypes.ContentType.objects.count()  #doctest: +SKIP
93

And there's one more contenttype object.

Database structure
==================

>>> from lino.utils.diag import analyzer
>>> analyzer.show_db_overview()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
49 plugins: lino, about, jinja, react, printing, system, help, users, office, xl, countries, contacts, phones, lists, beid, contenttypes, gfks, linod, checkdata, cal, courses, products, rooms, memo, excerpts, periods, weasyprint, uploads, accounting, bevats, vat, trading, summaries, storage, invoicing, finan, sepa, notes, outbox, voga, export_excel, calview, wkhtmltopdf, appypod, changes, bootstrap3, publisher, staticfiles, sessions.
95 models:
=========================== ============================== ========= =======
 Name                        Default table                  #fields   #rows
--------------------------- ------------------------------ --------- -------
 accounting.Account          accounting.Accounts            18        21
 accounting.Journal          accounting.Journals            28        10
 accounting.LedgerInfo       accounting.LedgerInfoTable     2         0
 accounting.MatchRule        accounting.MatchRules          3         33
 accounting.Movement         accounting.Movements           11        1561
 accounting.PaymentTerm      accounting.PaymentTerms        12        8
 accounting.Voucher          accounting.AllVouchers         9         465
 bevats.Declaration          bevats.Declarations            29        15
 cal.Calendar                cal.Calendars                  6         8
 cal.EntryRepeater           cal.EntryRepeaterTable         17        0
 cal.Event                   cal.Events                     25        1171
 cal.EventPolicy             cal.EventPolicies              20        6
 cal.EventType               cal.EventTypes                 24        10
 cal.Guest                   cal.Guests                     6         0
 cal.GuestRole               cal.GuestRoles                 5         3
 cal.RecurrentEvent          cal.RecurrentEvents            22        16
 cal.RemoteCalendar          cal.RemoteCalendars            7         0
 cal.Room                    cal.Rooms                      11        7
 cal.Subscription            cal.Subscriptions              4         35
 cal.Task                    cal.Tasks                      16        0
 calview.DailyPlannerRow     calview.DailyPlannerRows       7         2
 changes.Change              changes.Changes                10        0
 checkdata.Message           checkdata.Messages             6         20
 contacts.Company            contacts.Companies             25        31
 contacts.CompanyType        contacts.CompanyTypes          7         16
 contacts.Partner            contacts.Partners              23        103
 contacts.Person             contacts.Persons               41        72
 contacts.Role               contacts.Roles                 4         3
 contacts.RoleType           contacts.RoleTypes             5         5
 contenttypes.ContentType    gfks.ContentTypes              3         95
 countries.Country           countries.Countries            6         10
 countries.Place             countries.Places               9         80
 courses.Course              courses.Activities             34        26
 courses.CourseType          courses.CourseTypes            5         0
 courses.Enrolment           courses.Enrolments             17        94
 courses.Line                courses.Lines                  25        10
 courses.Pupil               courses.Pupils                 50        35
 courses.PupilType           courses.PupilTypes             5         3
 courses.Slot                courses.Slots                  5         0
 courses.Teacher             courses.Teachers               43        9
 courses.TeacherType         courses.TeacherTypes           5         4
 courses.Topic               courses.Topics                 4         5
 excerpts.Excerpt            excerpts.Excerpts              11        ...
 excerpts.ExcerptType        excerpts.ExcerptTypes          17        15
 finan.BankStatement         finan.BankStatements           17        21
 finan.BankStatementItem     finan.BankStatementItemTable   9         398
 finan.JournalEntry          finan.FinancialVouchers        15        0
 finan.JournalEntryItem      finan.JournalEntryItemTable    9         0
 finan.PaymentOrder          finan.PaymentOrders            16        16
 finan.PaymentOrderItem      finan.PaymentOrderItemTable    9         125
 invoicing.FollowUpRule      invoicing.FollowUpRules        5         4
 invoicing.Item              invoicing.Items                10        18
 invoicing.Plan              invoicing.Plans                8         1
 invoicing.Tariff            invoicing.Tariffs              8         0
 invoicing.Task              invoicing.Tasks                29        1
 linod.SystemTask            linod.SystemTasks              25        5
 lists.List                  lists.Lists                    7         8
 lists.ListType              lists.ListTypes                4         3
 lists.Member                lists.Members                  5         103
 memo.Mention                memo.Mentions                  5         0
 notes.EventType             notes.EventTypes               8         1
 notes.Note                  notes.Notes                    16        100
 notes.NoteType              notes.NoteTypes                11        3
 outbox.Attachment           outbox.Attachments             4         0
 outbox.Mail                 outbox.Mails                   8         63
 outbox.Recipient            outbox.Recipients              6         63
 periods.StoredPeriod        periods.StoredPeriods          7         17
 periods.StoredYear          periods.StoredYears            5         7
 phones.ContactDetail        phones.ContactDetails          8         83
 products.Category           products.Categories            15        5
 products.PriceRule          products.PriceRules            4         0
 products.Product            products.Products              22        12
 publisher.Page              publisher.Pages                16        21
 rooms.Booking               rooms.Bookings                 24        3
 sepa.Account                sepa.Accounts                  6         25
 sessions.Session            users.Sessions                 3         ...
 storage.Component           storage.Components             4         3
 storage.DeliveryItem        storage.DeliveryItems          8         0
 storage.DeliveryNote        storage.DeliveryNotes          15        0
 storage.Filler              storage.Fillers                6         20
 storage.Movement            storage.Movements              10        315
 storage.Provision           storage.Provisions             5         0
 storage.TransferRule        storage.TransferRules          5         0
 system.SiteConfig           system.SiteConfigs             10        1
 trading.InvoiceItem         trading.InvoiceItems           16        679
 trading.PaperType           trading.PaperTypes             5         2
 trading.TradingRule         trading.TradingRules           6         82
 trading.VatProductInvoice   trading.Invoices               29        294
 uploads.Upload              uploads.Uploads                12        11
 uploads.UploadType          uploads.UploadTypes            8         1
 uploads.Volume              uploads.Volumes                4         1
 users.Authority             users.Authorities              3         0
 users.User                  users.AllUsers                 21        6
 vat.InvoiceItem             vat.InvoiceItemTable           9         187
 vat.VatAccountInvoice       vat.Invoices                   21        119
=========================== ============================== ========= =======
<BLANKLINE>



Foreign Keys and their `on_delete` setting
==========================================

Here is a list of foreign keys in :ref:`voga` and their on_delete
behaviour. See also :doc:`/dev/delete`.

>>> from lino.utils.diag import analyzer
>>> print(analyzer.show_foreign_keys())
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
- accounting.Account :
  - PROTECT : accounting.Journal.account, accounting.MatchRule.account, accounting.Movement.account, finan.BankStatement.item_account, finan.BankStatementItem.account, finan.JournalEntry.item_account, finan.JournalEntryItem.account, finan.PaymentOrder.item_account, finan.PaymentOrderItem.account, vat.InvoiceItem.account
- accounting.Journal :
  - CASCADE : accounting.MatchRule.journal, invoicing.FollowUpRule.source_journal
  - PROTECT : accounting.Voucher.journal, invoicing.Task.target_journal, storage.TransferRule.journal
- accounting.PaymentTerm :
  - PROTECT : bevats.Declaration.payment_term, courses.Course.payment_term, trading.TradingRule.payment_term, trading.VatProductInvoice.payment_term, vat.VatAccountInvoice.payment_term
- accounting.Voucher :
  - CASCADE : accounting.Movement.voucher, storage.Movement.voucher
  - PROTECT : bevats.Declaration.voucher_ptr, finan.BankStatement.voucher_ptr, finan.JournalEntry.voucher_ptr, finan.PaymentOrder.voucher_ptr, storage.DeliveryNote.voucher_ptr, trading.VatProductInvoice.voucher_ptr, vat.VatAccountInvoice.voucher_ptr
  - SET_NULL : invoicing.Item.invoice
- cal.Calendar :
  - CASCADE : cal.Subscription.calendar
  - PROTECT : cal.Room.calendar, system.SiteConfig.site_calendar
- cal.Event :
  - CASCADE : cal.Guest.event
  - PROTECT : cal.EntryRepeater.cal_entry
- cal.EventType :
  - PROTECT : cal.Event.event_type, cal.EventPolicy.event_type, cal.RecurrentEvent.event_type, courses.Line.event_type, products.PriceRule.selector, rooms.Booking.event_type, system.SiteConfig.default_event_type, users.User.event_type
- cal.GuestRole :
  - PROTECT : cal.Guest.role, courses.Line.guest_role, system.SiteConfig.pupil_guestrole
- cal.Room :
  - PROTECT : cal.Event.room, courses.Course.room, rooms.Booking.room
- contacts.Company :
  - PROTECT : accounting.Journal.partner, cal.Room.company, contacts.Role.company, courses.Line.company, excerpts.Excerpt.company, notes.Note.company, rooms.Booking.company
- contacts.CompanyType :
  - PROTECT : contacts.Company.type
- contacts.Partner :
  - CASCADE : contacts.Company.partner_ptr, contacts.Person.partner_ptr, invoicing.Item.partner, lists.Member.partner, phones.ContactDetail.partner, sepa.Account.partner, trading.TradingRule.partner
  - PROTECT : accounting.Movement.partner, bevats.Declaration.partner, finan.BankStatementItem.partner, finan.JournalEntryItem.partner, finan.PaymentOrderItem.partner, invoicing.Plan.partner, outbox.Recipient.partner, storage.DeliveryNote.partner, storage.Filler.partner, storage.Movement.partner, storage.Provision.partner, trading.TradingRule.invoice_recipient, trading.VatProductInvoice.partner, users.User.partner, vat.VatAccountInvoice.partner
- contacts.Person :
  - CASCADE : courses.Pupil.person_ptr, courses.Teacher.person_ptr
  - PROTECT : cal.Guest.partner, cal.Room.contact_person, contacts.Role.person, courses.Line.contact_person, excerpts.Excerpt.contact_person, notes.Note.contact_person, rooms.Booking.contact_person
- contacts.RoleType :
  - PROTECT : cal.Room.contact_role, contacts.Role.type, courses.Line.contact_role, excerpts.Excerpt.contact_role, notes.Note.contact_role, rooms.Booking.contact_role
- contenttypes.ContentType :
  - PROTECT : accounting.Journal.default_invoiceable_type, cal.Event.owner_type, cal.Task.owner_type, changes.Change.master_type, changes.Change.object_type, checkdata.Message.owner_type, excerpts.Excerpt.owner_type, excerpts.ExcerptType.content_type, invoicing.FollowUpRule.invoice_generator, invoicing.Item.generator_type, memo.Mention.owner_type, memo.Mention.target_type, notes.Note.owner_type, outbox.Attachment.owner_type, outbox.Mail.owner_type, storage.DeliveryItem.invoiceable_type, trading.InvoiceItem.invoiceable_type, uploads.Upload.owner_type
- countries.Country :
  - PROTECT : contacts.Partner.country, contacts.Person.birth_country, contacts.Person.nationality, countries.Place.country
- countries.Place :
  - PROTECT : contacts.Partner.city, contacts.Partner.region, countries.Place.parent
- courses.Course :
  - PROTECT : courses.Enrolment.course, invoicing.Plan.order
- courses.CourseType :
  - PROTECT : courses.Line.course_type
- courses.Line :
  - PROTECT : courses.Course.line
- courses.Pupil :
  - PROTECT : courses.Enrolment.pupil
- courses.PupilType :
  - PROTECT : courses.Pupil.pupil_type
- courses.Slot :
  - PROTECT : courses.Course.slot
- courses.Teacher :
  - PROTECT : courses.Course.teacher
- courses.TeacherType :
  - PROTECT : courses.Teacher.teacher_type
- courses.Topic :
  - PROTECT : courses.Line.topic
- excerpts.Excerpt :
  - SET_NULL : bevats.Declaration.printed_by, courses.Enrolment.printed_by, finan.BankStatement.printed_by, finan.JournalEntry.printed_by, finan.PaymentOrder.printed_by, storage.DeliveryNote.printed_by, trading.VatProductInvoice.printed_by
- excerpts.ExcerptType :
  - PROTECT : excerpts.Excerpt.excerpt_type
- finan.BankStatement :
  - CASCADE : finan.BankStatementItem.voucher
- finan.JournalEntry :
  - CASCADE : finan.JournalEntryItem.voucher
- finan.PaymentOrder :
  - CASCADE : finan.PaymentOrderItem.voucher
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
- outbox.Mail :
  - CASCADE : outbox.Attachment.mail, outbox.Recipient.mail
- periods.StoredPeriod :
  - PROTECT : accounting.Voucher.accounting_period, bevats.Declaration.end_period, bevats.Declaration.start_period
- periods.StoredYear :
  - PROTECT : accounting.Voucher.fiscal_year, periods.StoredPeriod.year
- products.Category :
  - PROTECT : courses.Line.fees_cat, courses.Line.options_cat, products.Category.parent, products.Product.category
- products.Product :
  - PROTECT : cal.Room.fee, courses.Course.fee, courses.Enrolment.fee, courses.Enrolment.option, courses.Line.fee, invoicing.Tariff.product, products.PriceRule.product, storage.Component.child, storage.Component.parent, storage.DeliveryItem.product, storage.Filler.provision_product, storage.Movement.product, storage.Provision.product, trading.InvoiceItem.product
- publisher.Page :
  - PROTECT : publisher.Page.parent, publisher.Page.previous_page, publisher.Page.translated_from
- sepa.Account :
  - PROTECT : accounting.Journal.sepa_account, finan.PaymentOrderItem.bank_account
- storage.DeliveryNote :
  - CASCADE : storage.DeliveryItem.voucher
- trading.PaperType :
  - PROTECT : courses.Course.paper_type, trading.TradingRule.paper_type, trading.VatProductInvoice.paper_type
- trading.VatProductInvoice :
  - CASCADE : trading.InvoiceItem.voucher
- uploads.Upload :
  - PROTECT : publisher.Page.main_image
- uploads.UploadType :
  - PROTECT : uploads.Upload.type
- uploads.Volume :
  - PROTECT : accounting.Journal.uploads_volume, uploads.Upload.volume
- users.User :
  - CASCADE : accounting.LedgerInfo.user, cal.Subscription.user
  - PROTECT : accounting.Voucher.user, cal.Event.assigned_to, cal.Event.user, cal.RecurrentEvent.user, cal.Task.user, changes.Change.user, checkdata.Message.user, courses.Course.user, courses.Enrolment.user, excerpts.Excerpt.user, invoicing.Plan.user, invoicing.Task.user, notes.Note.user, outbox.Mail.user, rooms.Booking.user, uploads.Upload.user, users.Authority.authorized, users.Authority.user
- vat.VatAccountInvoice :
  - CASCADE : vat.InvoiceItem.voucher
<BLANKLINE>



Here is the output of :func:`walk_menu_items
<lino.api.doctests.walk_menu_items>` for this demo project.

>>> from lino.core.roles import Explorer
>>> rt.login("robin").get_user().user_type.has_required_roles([Explorer])
True

>>> walk_menu_items('robin', severe=True)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
- Contacts --> Persons : 73
- Contacts --> Organizations : 32
- Contacts --> Partner Lists : 9
- Office --> Data problem messages assigned to me : 19
- Office --> My Notes : 34
- Office --> My Outbox : 64
- Office --> My Excerpts : ...
- Office --> My Upload files : 5
- Calendar --> My appointments : 110
- Calendar --> Overdue appointments : 25
- Calendar --> My unconfirmed appointments : 12
- Calendar --> My tasks : 1
- Calendar --> My guests : 1
- Calendar --> My presences : 1
- Calendar --> My overdue appointments : 5
- Calendar --> Upcoming events : 539
- Calendar --> Bookings : 4
- Calendar --> Calendar : (not tested)
- Activities --> Participants : 36
- Activities --> Instructors : 10
- Activities --> Courses : 24
- Activities --> Hikes : 1
- Activities --> Journeys : 4
- Activities --> Topics : 6
- Activities --> Activity lines : 11
- Activities --> Pending requested enrolments : 11
- Activities --> Pending confirmed enrolments : 78
- Sales --> My invoicing plan : (not tested)
- Sales --> Sales invoices (SLS) : (not tested)
- Sales --> Sales credit notes (SLC) : (not tested)
- Publisher --> Pages : 22
- Accounting --> Purchases --> Purchase invoices (PRC) : (not tested)
- Accounting --> Wages --> Paychecks (SAL) : (not tested)
- Accounting --> Financial --> Payment orders Bestbank (PMO) : (not tested)
- Accounting --> Financial --> Cash book (CSH) : (not tested)
- Accounting --> Financial --> Bestbank (BNK) : (not tested)
- Accounting --> VAT --> VAT declarations (VAT) : (not tested)
- Accounting --> Miscellaneous transactions --> Miscellaneous transactions (MSC) : (not tested)
- Accounting --> Miscellaneous transactions --> Preliminary transactions (PRE) : (not tested)
- Reports --> Activities --> Status Report : (not tested)
- Reports --> Sales --> Due invoices : 21
- Reports --> Accounting --> Debtors : 18
- Reports --> Accounting --> Creditors : 7
- Reports --> VAT --> Intra-Community purchases : 34
- Reports --> VAT --> Intra-Community sales : 0
- Configure --> System --> Users : 7
- Configure --> System --> Site configuration : (not tested)
- Configure --> System --> System tasks : 6
- Configure --> Places --> Countries : 11
- Configure --> Places --> Places : 81
- Configure --> Contacts --> Legal forms : 17
- Configure --> Contacts --> Functions : 6
- Configure --> Contacts --> List Types : 4
- Configure --> Calendar --> Calendars : 9
- Configure --> Calendar --> Rooms : 8
- Configure --> Calendar --> Recurring events : 17
- Configure --> Calendar --> Guest roles : 4
- Configure --> Calendar --> Calendar entry types : 11
- Configure --> Calendar --> Recurrency policies : 7
- Configure --> Calendar --> Remote Calendars : 1
- Configure --> Calendar --> Planner rows : 3
- Configure --> Activities --> Activity types : 1
- Configure --> Activities --> Instructor types : 5
- Configure --> Activities --> Participant types : 4
- Configure --> Activities --> Timetable Slots : 1
- Configure --> Fees --> Fees : 13
- Configure --> Fees --> Fee categories : 6
- Configure --> Sales --> Paper types : 3
- Configure --> Sales --> Flatrates : 1
- Configure --> Sales --> Follow-up rules : 5
- Configure --> Sales --> Invoicing tasks : 2
- Configure --> Office --> Note Types : 4
- Configure --> Office --> Event Types : 2
- Configure --> Office --> Excerpt Types : 16
- Configure --> Office --> Library volumes : 2
- Configure --> Office --> Upload types : 2
- Configure --> Publisher --> Special pages : 7
- Configure --> Accounting --> Fiscal years : 8
- Configure --> Accounting --> Accounting periods : 18
- Configure --> Accounting --> Accounts : 22
- Configure --> Accounting --> Journals : 11
- Configure --> Accounting --> Payment terms : 9
- Explorer --> System --> Authorities : 1
- Explorer --> System --> User types : 6
- Explorer --> System --> User roles : 30
- Explorer --> System --> Data checkers : 18
- Explorer --> System --> Data problem messages : 20
- Explorer --> System --> Changes : 0
- Explorer --> System --> content types : 96
- Explorer --> System --> Background procedures : 6
- Explorer --> Contacts --> Contact persons : 4
- Explorer --> Contacts --> Partners : 104
- Explorer --> Contacts --> Contact detail types : 6
- Explorer --> Contacts --> Contact details : 84
- Explorer --> Contacts --> List memberships : 104
- Explorer --> Calendar --> Calendar entries : 857
- Explorer --> Calendar --> Tasks : 1
- Explorer --> Calendar --> Presences : 1
- Explorer --> Calendar --> Subscriptions : 36
- Explorer --> Calendar --> Entry states : 4
- Explorer --> Calendar --> Presence states : 5
- Explorer --> Calendar --> Task states : 5
- Explorer --> Calendar --> Planner columns : 2
- Explorer --> Calendar --> Display colors : 26
- Explorer --> Activities --> Activities : 27
- Explorer --> Activities --> Enrolments : 88
- Explorer --> Activities --> Enrolment states : 4
- Explorer --> Activities --> Course layouts : 3
- Explorer --> Activities --> Activity states : 4
- Explorer --> Sales --> Price factors : 0
- Explorer --> Sales --> Trading rules : 83
- Explorer --> Sales --> Trading invoices : 295
- Explorer --> Sales --> Trading invoice items : 679
- Explorer --> Sales --> Invoicing plans : 2
- Explorer --> Financial --> Bank statements : 22
- Explorer --> Financial --> Journal entries : 1
- Explorer --> Financial --> Payment orders : 17
- Explorer --> SEPA --> Bank accounts : 26
- Explorer --> Office --> Notes : 101
- Explorer --> Office --> Outgoing messages : 64
- Explorer --> Office --> Attachments : 1
- Explorer --> Office --> Mentions : 0
- Explorer --> Office --> Excerpts : ...
- Explorer --> Office --> Upload files : 12
- Explorer --> Office --> Upload areas : 1
- Explorer --> Accounting --> Common accounts : 22
- Explorer --> Accounting --> Match rules : 34
- Explorer --> Accounting --> Vouchers : 465
- Explorer --> Accounting --> Voucher types : 7
- Explorer --> Accounting --> Movements : 1561
- Explorer --> Accounting --> Trade types : 6
- Explorer --> Accounting --> Journal groups : 6
- Explorer --> VAT --> Special Belgian VAT declarations : 16
- Explorer --> VAT --> Declaration fields : 11
- Explorer --> VAT --> VAT areas : 3
- Explorer --> VAT --> VAT regimes : 4
- Explorer --> VAT --> VAT classes : 8
- Explorer --> VAT --> VAT columns : 8
- Explorer --> VAT --> Ledger invoices : 120
- Explorer --> VAT --> VAT rules : 10
- Site --> About : (not tested)
- Site --> User sessions : ...
<BLANKLINE>


Don't read me
=============

The snippets in this section are just for testing.

>>> pprint(settings.SITE.installed_plugins)
... #doctest: +REPORT_UDIFF +NORMALIZE_WHITESPACE
(<lino.core.plugin.Plugin lino>,
 <lino.modlib.about.Plugin lino.modlib.about>,
 <lino.modlib.jinja.Plugin lino.modlib.jinja(needed by lino_react.react)>,
 <lino_react.react.Plugin lino_react.react(needs ['lino.modlib.jinja'])>,
 <lino.modlib.printing.Plugin lino.modlib.printing(needed by lino.modlib.system)>,
 <lino.modlib.system.Plugin lino.modlib.system(needed by lino.modlib.help, needs ['lino.modlib.printing'])>,
 <lino.modlib.help.Plugin lino.modlib.help(needs ['lino.modlib.system'])>,
 <lino.modlib.users.Plugin lino.modlib.users(needs ['lino.modlib.system'])>,
 <lino.modlib.office.Plugin lino.modlib.office(needed by lino_xl.lib.countries)>,
 <lino.core.plugin.Plugin lino_xl.lib.xl(needed by lino_xl.lib.countries)>,
 <lino_xl.lib.countries.Plugin lino_xl.lib.countries(needs ['lino.modlib.office', 'lino_xl.lib.xl'])>,
 <lino_voga.lib.contacts.Plugin lino_voga.lib.contacts(needs ['lino_xl.lib.countries', 'lino.modlib.system'])>,
 <lino_xl.lib.phones.Plugin lino_xl.lib.phones>,
 <lino_xl.lib.lists.Plugin lino_xl.lib.lists>,
 <lino_xl.lib.beid.Plugin lino_xl.lib.beid>,
 <lino.core.plugin.Plugin django.contrib.contenttypes(needed by lino.modlib.gfks)>,
 <lino.modlib.gfks.Plugin lino.modlib.gfks(needed by lino.modlib.checkdata, needs ['lino.modlib.system', 'django.contrib.contenttypes'])>,
 <lino.modlib.linod.Plugin lino.modlib.linod(needed by lino.modlib.checkdata)>,
 <lino.modlib.checkdata.Plugin lino.modlib.checkdata(needs ['lino.modlib.users', 'lino.modlib.gfks', 'lino.modlib.office', 'lino.modlib.linod'])>,
 <lino_voga.lib.cal.Plugin lino_voga.lib.cal(needs ['lino.modlib.gfks', 'lino.modlib.printing', 'lino_xl.lib.xl'])>,
 <lino_voga.lib.roger.courses.Plugin lino_voga.lib.roger.courses(needs ['lino_xl.lib.cal'])>,
 <lino_voga.lib.products.Plugin lino_voga.lib.products(needs ['lino_xl.lib.xl'])>,
 <lino_voga.lib.rooms.Plugin lino_voga.lib.rooms>,
 <lino.modlib.memo.Plugin lino.modlib.memo(needed by lino_voga.lib.trading, needs ['lino.modlib.office', 'lino.modlib.gfks'])>,
 <lino_xl.lib.excerpts.Plugin lino_xl.lib.excerpts(needed by lino_xl.lib.vat, needs ['lino.modlib.gfks', 'lino.modlib.printing', 'lino.modlib.office', 'lino_xl.lib.xl'])>,
 <lino.modlib.periods.Plugin lino.modlib.periods(needed by lino_xl.lib.accounting)>,
 <lino.modlib.weasyprint.Plugin lino.modlib.weasyprint(needed by lino_xl.lib.accounting, needs ['lino.modlib.jinja'])>,
 <lino.modlib.uploads.Plugin lino.modlib.uploads(needed by lino_xl.lib.accounting)>,
 <lino_xl.lib.accounting.Plugin lino_xl.lib.accounting(needed by lino_xl.lib.vat, needs ['lino.modlib.periods', 'lino.modlib.weasyprint', 'lino_xl.lib.xl', 'lino.modlib.uploads'])>,
 <lino_xl.lib.bevats.Plugin lino_xl.lib.bevats(needed by lino_xl.lib.vat, needs ['lino_xl.lib.vat'])>,
 <lino_xl.lib.vat.Plugin lino_xl.lib.vat(needed by lino_voga.lib.trading, needs ['lino.modlib.checkdata', 'lino_xl.lib.excerpts'])>,
 <lino_xl.lib.trading.Plugin lino_voga.lib.trading(needs ['lino.modlib.memo', 'lino_xl.lib.products', 'lino_xl.lib.vat'])>,
 <lino.modlib.summaries.Plugin lino.modlib.summaries(needed by lino_xl.lib.storage)>,
 <lino_xl.lib.storage.Plugin lino_xl.lib.storage(needs ['lino_xl.lib.products', 'lino.modlib.summaries'])>,
 <lino_xl.lib.invoicing.Plugin lino_xl.lib.invoicing(needs ['lino_xl.lib.trading'])>,
 <lino_xl.lib.finan.Plugin lino_xl.lib.finan(needs ['lino_xl.lib.accounting'])>,
 <lino_xl.lib.sepa.Plugin lino_xl.lib.sepa>,
 <lino_xl.lib.notes.Plugin lino_xl.lib.notes(needs ['lino.modlib.memo'])>,
 <lino_xl.lib.outbox.Plugin lino_xl.lib.outbox(needs ['lino.modlib.uploads'])>,
 <lino_voga.lib.voga.Plugin lino_voga.lib.voga>,
 <lino.modlib.export_excel.Plugin lino.modlib.export_excel>,
 <lino_xl.lib.calview.Plugin lino_xl.lib.calview(needs ['lino_xl.lib.cal'])>,
 <lino.modlib.wkhtmltopdf.Plugin lino.modlib.wkhtmltopdf>,
 <lino_xl.lib.appypod.Plugin lino_xl.lib.appypod>,
 <lino.modlib.changes.Plugin lino.modlib.changes(needs ['lino.modlib.users', 'lino.modlib.gfks'])>,
 <lino.modlib.bootstrap3.Plugin lino.modlib.bootstrap3(needed by lino.modlib.publisher, needs ['lino.modlib.jinja'])>,
 <lino.modlib.publisher.Plugin lino.modlib.publisher(needs ['lino.modlib.system', 'lino.modlib.linod', 'lino.modlib.jinja', 'lino.modlib.bootstrap3'])>,
 <lino.core.plugin.Plugin django.contrib.staticfiles>,
 <lino.core.plugin.Plugin django.contrib.sessions>)

>>> rt.show(checkdata.Messages)  #doctest: +NORMALIZE_WHITESPACE
============= ================================================= ============================================================== ==============================
 Responsible   Database object                                   Message text                                                   Checker
------------- ------------------------------------------------- -------------------------------------------------------------- ------------------------------
 Robin Rood    `Recurring event #4 Assumption of Mary <…>`__     Event conflicts with Activity #1 001  1.                       cal.ConflictingEventsChecker
 Robin Rood    `Recurring event #11 Ascension of Jesus <…>`__    Event conflicts with Mittagessen (14.05.2015 11:10).           cal.ConflictingEventsChecker
 Robin Rood    `Recurring event #12 Pentecost <…>`__             Event conflicts with 4 other events.                           cal.ConflictingEventsChecker
 Rolf Rompen   `Mittagessen (14.05.2015 11:10) <…>`__            Event conflicts with Recurring event #11 Ascension of Jesus.   cal.ConflictingEventsChecker
 Robin Rood    `First meeting (25.05.2015 13:30) <…>`__          Event conflicts with Recurring event #12 Pentecost.            cal.ConflictingEventsChecker
 Robin Rood    `Absent for private reasons (25.05.2015) <…>`__   Event conflicts with Recurring event #12 Pentecost.            cal.ConflictingEventsChecker
 Robin Rood    `Karl Kaivers (MEC) <…>`__                        Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Josefine Leffin (ME) <…>`__                      Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Erna Emonts-Gast (ME) <…>`__                     Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Alfons Radermacher (MEC) <…>`__                  Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Edgard Radermacher (ME) <…>`__                   Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Hedi Radermacher (ME) <…>`__                     Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Didier di Rupo (MEL) <…>`__                      Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Otto Östges (ME) <…>`__                          Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Mark Martelaer (ME) <…>`__                       Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Marie-Louise Vandenmeulenbos (MEL) <…>`__        Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Lisa Lahm (ME) <…>`__                            Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Bernd Brecht (MEC) <…>`__                        Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Jérôme Jeanémart (ME) <…>`__                     Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Source document PRC_29_2015.pdf <…>`__           Upload entry uploads/2015/05/PRC_29_2015.pdf has no file       uploads.UploadChecker
============= ================================================= ============================================================== ==============================
<BLANKLINE>



..
  >>> dbhash.check_virgin()
