.. doctest docs/apps/noi/db.rst
.. _noi.specs.db:

===========================
Lino Noi database structure
===========================

This document describes the database structure.


.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *


Complexity factors
==================

>>> print(analyzer.show_complexity_factors())
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- 62 plugins
- 112 models
- 5 user types
- 376 views
- 27 dialog actions
<BLANKLINE>


The database models
===================


>>> analyzer.show_db_overview()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
62 plugins: lino, printing, system, contenttypes, gfks, help, office, xl, countries, contacts, social_django, users, noi, cal, calview, topics, excerpts, memo, comments, tickets, nicknames, summaries, channels, daphne, linod, checkdata, working, lists, changes, notify, uploads, export_excel, tinymce, smtpd, jinja, weasyprint, appypod, dashboard, inbox, userstats, groups, products, periods, accounting, vat, trading, storage, invoicing, subscriptions, sepa, peppol, about, bootstrap3, extjs, rest_framework, restful, addresses, phones, google, search, staticfiles, sessions.
112 models:
================================== =================================== ========= =======
 Name                               Default table                       #fields   #rows
---------------------------------- ----------------------------------- --------- -------
 accounting.Account                 accounting.Accounts                 18        20
 accounting.Journal                 accounting.Journals                 30        4
 accounting.LedgerInfo              accounting.LedgerInfoTable          2         0
 accounting.MatchRule               accounting.MatchRules               3         0
 accounting.Movement                accounting.Movements                11        100
 accounting.PaymentTerm             accounting.PaymentTerms             12        8
 accounting.Voucher                 accounting.AllVouchers              9         110
 addresses.Address                  addresses.Addresses                 16        124
 cal.Calendar                       cal.Calendars                       8         1
 cal.EntryRepeater                  cal.EntryRepeaterTable              17        0
 cal.Event                          cal.Events                          29        113
 cal.EventPolicy                    cal.EventPolicies                   20        6
 cal.EventType                      cal.EventTypes                      24        4
 cal.Guest                          cal.Guests                          6         0
 cal.GuestRole                      cal.GuestRoles                      5         0
 cal.RecurrentEvent                 cal.RecurrentEvents                 22        15
 cal.RemoteCalendar                 cal.RemoteCalendars                 7         0
 cal.Room                           cal.Rooms                           10        0
 cal.Subscription                   cal.Subscriptions                   4         0
 cal.Task                           cal.Tasks                           16        0
 calview.DailyPlannerRow            calview.DailyPlannerRows            7         2
 changes.Change                     changes.Changes                     10        0
 checkdata.Message                  checkdata.Messages                  6         ...
 comments.Comment                   comments.Comments                   12        504
 comments.CommentType               comments.CommentTypes               4         0
 comments.Reaction                  comments.Reactions                  6         0
 contacts.Company                   contacts.Companies                  27        26
 contacts.CompanyType               contacts.CompanyTypes               7         16
 contacts.Partner                   contacts.Partners                   25        95
 contacts.Person                    contacts.Persons                    32        69
 contacts.Role                      contacts.Roles                      4         8
 contacts.RoleType                  contacts.RoleTypes                  5         5
 contenttypes.ContentType           gfks.ContentTypes                   3         112
 countries.Country                  countries.Countries                 6         10
 countries.Place                    countries.Places                    9         80
 dashboard.Widget                   dashboard.Widgets                   5         0
 excerpts.Excerpt                   excerpts.Excerpts                   11        3
 excerpts.ExcerptType               excerpts.ExcerptTypes               17        5
 google.CalendarSubscription        google.CalendarSubscriptionTable    6         0
 google.CalendarSyncToken           google.CalendarSyncTokenTable       6         0
 google.Contact                     google.Contacts                     5         0
 google.ContactSyncToken            google.ContactSyncTokenTable        6         0
 google.DeletedContact              google.DeletedContacts              3         0
 google.DeletedEntry                google.DeletedEntries               5         0
 google.EventSyncToken              google.EventSyncTokenTable          7         0
 google.FailedForeignItem           google.FailedForeignItemTable       4         0
 google.SyncSummary                 google.SyncSummaries                5         0
 groups.Group                       groups.Groups                       7         3
 groups.Membership                  groups.Memberships                  4         7
 invoicing.FollowUpRule             invoicing.FollowUpRules             5         4
 invoicing.Item                     invoicing.Items                     10        1
 invoicing.Plan                     invoicing.Plans                     8         1
 invoicing.Tariff                   invoicing.Tariffs                   8         0
 invoicing.Task                     invoicing.Tasks                     29        3
 linod.SystemTask                   linod.SystemTasks                   25        10
 lists.List                         lists.Lists                         7         8
 lists.ListType                     lists.ListTypes                     4         3
 lists.Member                       lists.Members                       5         95
 memo.Mention                       memo.Mentions                       5         153
 nicknames.Naming                   nicknames.Namings                   4         21
 notify.Message                     notify.Messages                     12        260
 notify.Subscription                notify.SubscriptionTable            7         0
 peppol.Supplier                    peppol.Suppliers                    8         10
 periods.StoredPeriod               periods.StoredPeriods               7         40
 periods.StoredYear                 periods.StoredYears                 5         9
 phones.ContactDetail               phones.ContactDetails               8         25
 products.Category                  products.Categories                 15        0
 products.PriceRule                 products.PriceRules                 4         0
 products.Product                   products.Products                   22        10
 sepa.Account                       sepa.Accounts                       6         19
 sessions.Session                   users.Sessions                      3         ...
 social_django.Association          social_django.AssociationTable      7         0
 social_django.Code                 social_django.CodeTable             5         0
 social_django.Nonce                social_django.NonceTable            4         0
 social_django.Partial              social_django.PartialTable          6         0
 social_django.UserSocialAuth       users.SocialAuths                   7         0
 storage.Component                  storage.Components                  4         4
 storage.DeliveryItem               storage.DeliveryItems               8         625
 storage.DeliveryNote               storage.DeliveryNotes               15        55
 storage.Filler                     storage.Fillers                     6         5
 storage.Movement                   storage.Movements                   10        94
 storage.Provision                  storage.Provisions                  5         5
 storage.TransferRule               storage.TransferRules               5         2
 subscriptions.Subscription         subscriptions.Subscriptions         21        5
 subscriptions.SubscriptionItem     subscriptions.SubscriptionItems     8         15
 subscriptions.SubscriptionPeriod   subscriptions.SubscriptionPeriods   5         10
 system.SiteConfig                  system.SiteConfigs                  8         1
 tickets.CheckListItem              tickets.CheckListItems              4         0
 tickets.Ticket                     tickets.Tickets                     30        116
 tickets.TicketType                 tickets.TicketTypes                 5         4
 tinymce.TextFieldTemplate          tinymce.TextFieldTemplates          5         2
 topics.Interest                    topics.Interests                    4         0
 topics.Tag                         topics.Tags                         4         117
 topics.Topic                       topics.Topics                       4         5
 trading.InvoiceItem                trading.InvoiceItems                16        127
 trading.PaperType                  trading.PaperTypes                  5         2
 trading.TradingRule                trading.TradingRules                6         82
 trading.VatProductInvoice          trading.Invoices                    29        50
 uploads.Upload                     uploads.Uploads                     12        3
 uploads.UploadType                 uploads.UploadTypes                 8         1
 uploads.Volume                     uploads.Volumes                     4         2
 users.Authority                    users.Authorities                   3         0
 users.User                         users.AllUsers                      25        7
 userstats.UserStat                 userstats.UserStats                 4         36
 vat.InvoiceItem                    vat.InvoiceItemTable                9         0
 vat.VatAccountInvoice              vat.Invoices                        21        0
 working.Contract                   working.Contracts                   5         4
 working.OrderSummary               working.OrderSummaries              8         15
 working.ReportingRule              working.ReportingRules              5         3
 working.Session                    working.Sessions                    15        2384
 working.SessionType                working.SessionTypes                4         1
 working.UserSummary                working.UserSummaries               6         1092
================================== =================================== ========= =======
<BLANKLINE>


..
  >>> dbhash.check_virgin()
