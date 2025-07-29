.. doctest docs/projects/cosi1.rst
.. _cosi.tested.demo:
.. _specs.cosi.cosi1:

==================================================
``cosi1`` : A Lino Così for Belgium (DE)
==================================================

This :term:`demo project` is used by the following documents:
:doc:`/plugins/peppol`, :doc:`/dev/config_dirs`, :doc:`/dev/display_modes` and
many more.

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *

>>> ses = rt.login('robin')


Overview
========

>>> print(analyzer.show_complexity_factors())
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- 40 plugins
- 64 models
- 3 user types
- 216 views
- 20 dialog actions
<BLANKLINE>


>>> rt.show(accounting.JournalsOverview)
| **SLS** |  129 Verkaufsrechnungen |
|---------|-------------------------|
| **SLC** |  0 Gutschriften Verkauf |
|---------|-------------------------|
| **PRC** |  189 Einkaufsrechnungen |
|---------|-------------------------|
| **PMO** |  26 Zahlungsaufträge Bestbank |
|---------|-------------------------------|
| **CSH** |  0 Kassenbuch |
|---------|---------------|
| **BNK** |  26 Bestbank |
|---------|--------------|
| **MSC** |  0 Diverse Buchungen |
|---------|----------------------|
| **PRE** |  1 Preliminary transactions |
|---------|-----------------------------|
| **SAL** |  0 Lohnscheine |
|---------|----------------|
| **VAT** |  26 MwSt.-Erklärungen |
|---------|-----------------------|
| **INB** |  0 Eingangsdokumente |
|---------|----------------------|


>>> rt.show(invoicing.Tasks)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF +ELLIPSIS
===== ===================================== ============== =========== =============...========
 Nr.   Name                                  Abgeschaltet   Wann        Status
----- ------------------------------------- -------------- ----------- -------------...--------
 1     Verkaufsrechnungen (SLS) generieren   Nein           Jeden Tag   Geplant für ...
===== ===================================== ============== =========== =============...========
<BLANKLINE>



Implementation details
======================

>>> print(settings.SETTINGS_MODULE)
lino_book.projects.cosi1.settings

>>> print(' '.join([lng.name for lng in settings.SITE.languages]))
de fr en

The demo database contains 69 persons and 23 companies.

>>> contacts.Person.objects.count()
69
>>> contacts.Company.objects.count()
27
>>> contacts.Partner.objects.count()
96


>>> print(' '.join(settings.SITE.demo_fixtures))
std minimal_ledger furniture demo demo_bookings payments demo2 demo3 checkdata



The application menu
====================

Robin is the system administrator, he has a complete menu:

>>> show_menu('rolf')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- Kontakte : Personen, Organisationen
- Büro : Meine Auszüge, Meine Upload-Dateien, Meine Benachrichtigungen
- Verkauf : Verkaufsrechnungen (SLS), Gutschriften Verkauf (SLC), Mein Fakturationsplan
- Buchhaltung :
  - Einkauf : Einkaufsrechnungen (PRC), Eingangsdokumente (INB)
  - Löhne und Gehälter : Lohnscheine (SAL)
  - Finanzjournale : Zahlungsaufträge Bestbank (PMO), Kassenbuch (CSH), Bestbank (BNK)
  - MwSt. : MwSt.-Erklärungen (VAT)
  - Diverse Buchungen : Diverse Buchungen (MSC), Preliminary transactions (PRE)
  - Peppol : Rechnungseingang, Empfangene Rechnungen, Rechnungsausgang
- Berichte :
  - Buchhaltung : Schuldner, Gläubiger, Buchhaltungsbericht
  - Verkauf : Offene Rechnungen
  - MwSt. : Intra-Community purchases, Intra-Community sales
- Konfigurierung :
  - System : Benutzer, Site-Konfiguration, Systemaufgaben
  - Orte : Länder, Orte
  - Kontakte : Rechtsformen, Funktionen
  - Büro : Auszugsarten, Dateibibliotheken, Upload-Arten
  - Buchhaltung : Konten, Journale, Zahlungsbedingungen, Jahresberichtspositionen, Geschäftsjahre, Buchungsperioden
  - Verkauf : Produkte, Produktkategorien, Preisregeln, Papierarten, Pauschalen, Folgeregeln, Fakturierungsaufgaben
- Explorer :
  - System : Vollmachten, Benutzerarten, Benutzerrollen, Datenbankmodelle, Benachrichtigungen, Background procedures, Datentests, Datenproblemmeldungen
  - Kontakte : Kontaktpersonen, Partner, Kontaktangabenarten, Kontaktangaben
  - Büro : Auszüge, Upload-Dateien, Upload-Bereiche, Erwähnungen
  - Buchhaltung : Gemeinkonten, Begleichungsregeln, Belege, Belegarten, Bewegungen, Handelsarten, Journalgruppen, Accounting Reports, Allgemeine Jahresberichtspositionen, General account balances, Analytic accounts balances, Partner balances, Sheet item entries
  - SEPA : Bankkonten
  - Verkauf : Preisfaktoren, Handelsregeln, Handelsrechnungen, Handelsrechnungspositionen, Fakturationspläne
  - Finanzjournale : Kontoauszüge, Diverse Buchungen, Zahlungsaufträge
  - MwSt. : Belgische MwSt.-Erklärungen, Deklarationsfelder, MWSt-Zonen, MwSt.-Regimes, MwSt.-Klassen, MWSt-Kolonnen, Hauptbuchrechnungen, MwSt-Regeln
- Site : Info, Benutzersitzungen


Database structure
==================

>>> from lino.utils.diag import analyzer
>>> print analyzer.show_database_structure()
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF +ELLIPSIS +SKIP


.. _internal_clearings:

Internal clearings
==================

An **internal clearing** is when an employee acts as a temporary cashier by
paying purchase invoices or taking money for sales invoices.

When a site has a non-empty :attr:`payer_model
<lino_xl.lib.accounting.Plugin.payer_model>`,  Lino adds a field :attr:`payer
<lino_xl.lib.accounting.PaymentTerm.payer>` to each payment term.

When an invoice is registered with a payment term having a :attr:`payer
<lino_xl.lib.accounting.PaymentTerm.payer>`, Lino will book two additional
movements: one that cleans the debit (credit) on the customer (provider) by
booking back the total amount, and a second to book the total amount as a
debit or credit on the payer (using the :attr:`main_account
<lino_xl.lib.accounting.TradeType.main_account>` for :attr:`TradeTypes.clearings
<lino_xl.lib.accounting.TradeTypes.clearings>`).


>>> rt.show(accounting.PaymentTerms, language="en", column_names="ref name_en months days payer")
==================== ======================================= ======== ========= =================
 Reference            Designation (en)                        Months   Days      Payer
-------------------- --------------------------------------- -------- --------- -----------------
 07                   Payment seven days after invoice date   0        7
 10                   Payment ten days after invoice date     0        10
 30                   Payment 30 days after invoice date      0        30
 60                   Payment 60 days after invoice date      0        60
 90                   Payment 90 days after invoice date      0        90
 EOM                  Payment end of month                    0        0
 P30                  Prepayment 30%                          0        30
 PIA                  Payment in advance                      0        0
 robin                Cash Robin                              0        0         Mr Robin Dubois
 **Total (9 rows)**                                           **0**    **227**
==================== ======================================= ======== ========= =================
<BLANKLINE>

>>> dd.plugins.accounting.payer_model
<class 'lino_xl.lib.contacts.models.Person'>

And as we can see, our worker Robin owes us 16827 € because he took money for 12
sales invoices:

>>> robin = dd.plugins.accounting.payer_model.objects.get(first_name="Robin")
>>> rt.show(accounting.MovementsByPartner, master_instance=robin)
**12 offene Bewegungen (-16827.71 €)**


>>> rt.show(accounting.MovementsByPartner, master_instance=robin, nosummary=True)
========== ===================== =========================================================================================== =============== ============ ============= ===========
 Valuta     Beleg                 Beschreibung                                                                                Debit           Kredit       Match         Beglichen
---------- --------------------- ------------------------------------------------------------------------------------------- --------------- ------------ ------------- -----------
 09.02.25   `SLS 9/2025 <…>`__    `(4800) Interne Begleichungen <…>`__ | `Bastiaensen Laurent <…>`__ | `Dubois Robin <…>`__   3 811,15                     SLS 9/2025    Nein
 13.12.24   `SLS 56/2024 <…>`__   `(4800) Interne Begleichungen <…>`__ | `Hans Flott & Co <…>`__ | `Dubois Robin <…>`__       379,81                       SLS 56/2024   Nein
 21.08.24   `BNK 8/2024 <…>`__    `(4000) Kunden <…>`__ | `Dubois Robin <…>`__                                                6,77                         SLS 29/2024   Ja
 21.07.24   `BNK 7/2024 <…>`__    `(4000) Kunden <…>`__ | `Dubois Robin <…>`__                                                                345,45       SLS 29/2024   Ja
 12.07.24   `SLS 31/2024 <…>`__   `(4800) Interne Begleichungen <…>`__ | `Denon Denis <…>`__ | `Dubois Robin <…>`__           267,90                       SLS 31/2024   Nein
 11.07.24   `SLS 30/2024 <…>`__   `(4800) Interne Begleichungen <…>`__ | `Denon Denis <…>`__ | `Dubois Robin <…>`__           1 197,90                     SLS 30/2024   Nein
 10.07.24   `SLS 29/2024 <…>`__   `(4000) Kunden <…>`__ | `Dubois Robin <…>`__                                                338,68                       SLS 29/2024   Ja
 07.05.24   `SLS 21/2024 <…>`__   `(4800) Interne Begleichungen <…>`__ | `Dupont Jean <…>`__ | `Dubois Robin <…>`__           2 433,85                     SLS 21/2024   Nein
 08.03.24   `SLS 11/2024 <…>`__   `(4800) Interne Begleichungen <…>`__ | `Radermacher Inge <…>`__ | `Dubois Robin <…>`__      2 468,18                     SLS 11/2024   Nein
 07.01.24   `SLS 1/2024 <…>`__    `(4800) Interne Begleichungen <…>`__ | `Radermacher Alfons <…>`__ | `Dubois Robin <…>`__    38,62                        SLS 1/2024    Nein
 07.11.23   `SLS 49/2023 <…>`__   `(4800) Interne Begleichungen <…>`__ | `Lazarus Line <…>`__ | `Dubois Robin <…>`__          453,75                       SLS 49/2023   Nein
 10.09.23   `SLS 38/2023 <…>`__   `(4800) Interne Begleichungen <…>`__ | `Ingels Irene <…>`__ | `Dubois Robin <…>`__          726,00                       SLS 38/2023   Nein
 11.06.23   `SLS 29/2023 <…>`__   `(4800) Interne Begleichungen <…>`__ | `Evertz Bernd <…>`__ | `Dubois Robin <…>`__          2 782,77                     SLS 29/2023   Nein
 07.05.23   `SLS 19/2023 <…>`__   `(4800) Interne Begleichungen <…>`__ | `Bastiaensen Laurent <…>`__ | `Dubois Robin <…>`__   1 451,82                     SLS 19/2023   Nein
 10.02.23   `SLS 9/2023 <…>`__    `(4800) Interne Begleichungen <…>`__ | `Hans Flott & Co <…>`__ | `Dubois Robin <…>`__       815,96                       SLS 9/2023    Nein
                                  **Saldo 16827.71 (15 Bewegungen)**                                                          **17 173,16**   **345,45**
========== ===================== =========================================================================================== =============== ============ ============= ===========
<BLANKLINE>


Due invoices
============

This site shows a series of due sales invoices
(:class:`lino_xl.lib.trading.DueInvoices`).

>>> rt.show(trading.DueInvoices, language="en")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
===================== =========== ========= =================================== =============== ================ ================
 Due date              Reference   No.       Partner                             TotIncl         Balance before   Balance to pay
--------------------- ----------- --------- ----------------------------------- --------------- ---------------- ----------------
 10/02/2023            SLS         9/2023    Hans Flott & Co                     815,96
 07/05/2023            SLS         19/2023   Bastiaensen Laurent                 1 451,82
 11/06/2023            SLS         29/2023   Evertz Bernd                        2 782,77
 10/09/2023            SLS         38/2023   Ingels Irene                        726,00
 07/11/2023            SLS         49/2023   Lazarus Line                        453,75
 07/01/2024            SLS         1/2024    Radermacher Alfons                  38,62
 08/03/2024            SLS         11/2024   Radermacher Inge                    2 468,18
 07/05/2024            SLS         21/2024   Dupont Jean                         2 433,85
 11/07/2024            SLS         30/2024   Denon Denis                         1 197,90
 12/07/2024            SLS         31/2024   Denon Denis                         267,90
 13/12/2024            SLS         56/2024   Hans Flott & Co                     379,81
 18/01/2025            SLS         2/2025    Moulin Rouge                        310,20                           310,20
 09/02/2025            SLS         9/2025    Bastiaensen Laurent                 3 811,15
 18/02/2025            SLS         11/2025   Charlier Ulrike                     780,45                           780,45
 17/03/2025            SLS         12/2025   Chantraine Marc                     859,95                           859,95
 07/04/2025            SLS         13/2025   Dericum Daniel                      21,00                            21,00
 12/04/2025            SLS         6/2025    Arens Annette                       931,70                           931,70
 08/05/2025            SLS         14/2025   Demeulenaere Dorothée               3 387,78                         3 387,78
 08/06/2025            SLS         15/2025   Dobbelstein-Demeulenaere Dorothée   2 129,25                         2 129,25
 **Total (19 rows)**                                                             **25 248,04**                    **8 420,33**
===================== =========== ========= =================================== =============== ================ ================
<BLANKLINE>


>>> show_choicelists()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=========================== ======== ================= ===================================== ===================================== ============================
 name                        #items   preferred_width   de                                    fr                                    en
--------------------------- -------- ----------------- ------------------------------------- ------------------------------------- ----------------------------
 about.DateFormats           4        8                 Date formats                          Date formats                          Date formats
 about.TimeZones             1        4                 Zeitzonen                             Zeitzonen                             Time zones
 accounting.CommonAccounts   21       29                Gemeinkonten                          Comptes communs                       Common accounts
 accounting.DC               2        6                 Buchungsrichtungen                    Directions d'imputation               Booking directions
 accounting.JournalGroups    6        18                Journalgruppen                        Groupes de journaux                   Journal groups
 accounting.TradeTypes       6        18                Handelsarten                          Types de commerce                     Trade types
 accounting.VoucherStates    3        11                Belegzustände                         Belegzustände                         Voucher states
 accounting.VoucherTypes     7        55                Belegarten                            Types de pièce                        Voucher types
 bevat.DeclarationFields     29       4                 Deklarationsfelder                    Deklarationsfelder                    Declaration fields
 checkdata.Checkers          12       33                Datentests                            Tests de données                      Data checkers
 contacts.CivilStates        7        27                Zivilstände                           Etats civils                          Civil states
 contacts.PartnerEvents      1        18                Beobachtungskriterien                 Évènements observés                   Observed events
 countries.PlaceTypes        23       16                None                                  None                                  None
 excerpts.Shortcuts          0        4                 Excerpt shortcuts                     Excerpt shortcuts                     Excerpt shortcuts
 invoicing.Periodicities     4        15                Abonnementperiodizitäten              Abonnementperiodizitäten              Subscription periodicities
 linod.LogLevels             5        8                 Logging levels                        Logging levels                        Logging levels
 linod.Procedures            6        25                Background procedures                 Background procedures                 Background procedures
 notify.MailModes            5        24                Benachrichtigungsmodi                 Modes de notification                 Notification modes
 notify.MessageTypes         2        14                Message Types                         Types de message                      Message Types
 peppol.OutboundStates       8        13                Ausgangszustände                      Ausgangszustände                      Outbound document states
 periods.PeriodStates        2        14                Zustände                              États                                 States
 periods.PeriodTypes         4        9                 Period types                          Period types                          Period types
 phones.ContactDetailTypes   6        8                 Kontaktangabenarten                   Kontaktangabenarten                   Contact detail types
 printing.BuildMethods       6        20                None                                  None                                  None
 products.BarcodeDrivers     2        4                 Barcode drivers                       Barcode drivers                       Barcode drivers
 products.DeliveryUnits      13       13                Liefereinheiten                       Unités de livraison                   Delivery units
 products.PriceFactors       0        4                 Preisfaktoren                         Preisfaktoren                         Price factors
 products.ProductTypes       1        8                 Product types                         Product types                         Product types
 sheets.CommonItems          29       49                Allgemeine Jahresberichtspositionen   Allgemeine Jahresberichtspositionen   Common sheet items
 sheets.SheetTypes           2        23                Jahresbericht-Arten                   Jahresbericht-Arten                   Sheet types
 system.DisplayColors        26       10                Display colors                        Display colors                        Display colors
 system.DurationUnits        7        8                 None                                  None                                  None
 system.Genders              3        10                Geschlechter                          Sexes                                 Genders
 system.PeriodEvents         3        9                 Beobachtungskriterien                 Évènements observés                   Observed events
 system.Recurrences          11       20                Wiederholungen                        Récurrences                           Recurrences
 system.Weekdays             7        10                None                                  None                                  None
 system.YesNo                2        12                Ja oder Nein                          Oui ou non                            Yes or no
 uploads.Shortcuts           1        16                Upload shortcuts                      Upload shortcuts                      Upload shortcuts
 uploads.UploadAreas         1        7                 Upload-Bereiche                       Domaines de téléchargement            Upload areas
 users.UserTypes             3        15                Benutzerarten                         Types d'utilisateur                   User types
 vat.DeclarationFieldsBase   0        4                 Deklarationsfelder                    Deklarationsfelder                    Declaration fields
 vat.VatAreas                3        13                MWSt-Zonen                            Zones TVA                             VAT areas
 vat.VatClasses              6        37                MwSt.-Klassen                         Classes TVA                           VAT classes
 vat.VatColumns              10       34                MWSt-Kolonnen                         MWSt-Kolonnen                         VAT columns
 vat.VatRegimes              12       24                MwSt.-Regimes                         MwSt.-Regimes                         VAT regimes
 vat.VatRules                28       192               MwSt-Regeln                           MwSt-Regeln                           VAT rules
 xl.Priorities               5        8                 Prioritäten                           Priorités                             Priorities
=========================== ======== ================= ===================================== ===================================== ============================
<BLANKLINE>


Verify whether :ticket:`3657` is fixed:

>>> print(rt.find_config_file("logo.jpg", "weasyprint"))  #doctest: +ELLIPSIS
/.../lino_book/projects/cosi1/config/weasyprint/logo.jpg

Verify whether :ticket:`3705` is fixed:

>>> for cd in settings.SITE.confdirs.config_dirs:
...     print(cd.name)  #doctest: +ELLIPSIS
/.../lino_book/projects/cosi1/config
/.../lino_xl/lib/sheets/config
...
/.../lino/modlib/jinja/config
/.../lino/config


List of all the actors, sorted alphabetically:

>>> from lino.core import actors
>>> print("\n".join(sorted([str(a) for a in actors.actors_list if not a.is_abstract()])))
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
about.About
about.DateFormats
about.TimeZones
accounting.Accounts
accounting.AllMovements
accounting.AllVouchers
accounting.CommonAccounts
accounting.Creditors
accounting.DC
accounting.Debtors
accounting.DebtsByAccount
accounting.DebtsByPartner
accounting.ExpectedMovements
accounting.GeneralAccountBalances
accounting.JournalGroups
accounting.Journals
accounting.JournalsOverview
accounting.LedgerInfoTable
accounting.MatchRules
accounting.MatchRulesByAccount
accounting.MatchRulesByJournal
accounting.Movements
accounting.MovementsByAccount
accounting.MovementsByMatch
accounting.MovementsByPartner
accounting.MovementsByVoucher
accounting.MyMovements
accounting.PartnerVouchers
accounting.PaymentTerms
accounting.TradeTypes
accounting.VoucherStates
accounting.VoucherTypes
bevat.DeclarationFields
bevat.Declarations
bevat.DeclarationsByJournal
checkdata.AllMessages
checkdata.Checkers
checkdata.Messages
checkdata.MessagesByChecker
checkdata.MessagesByOwner
checkdata.MyMessages
contacts.CivilStates
contacts.Companies
contacts.CompanyTypes
contacts.PartnerEvents
contacts.Partners
contacts.PartnersByCity
contacts.PartnersByCountry
contacts.Persons
contacts.RoleTypes
contacts.Roles
contacts.RolesByCompany
contacts.RolesByPerson
countries.Countries
countries.PlaceTypes
countries.Places
countries.PlacesByCountry
countries.PlacesByPlace
excerpts.AllExcerpts
excerpts.ExcerptTypes
excerpts.Excerpts
excerpts.ExcerptsByOwner
excerpts.ExcerptsByType
excerpts.MyExcerpts
excerpts.Shortcuts
finan.AllBankStatements
finan.AllJournalEntries
finan.AllPaymentOrders
finan.BankStatementItemTable
finan.BankStatements
finan.BankStatementsByJournal
finan.FinancialVouchers
finan.ItemsByBankStatement
finan.ItemsByJournalEntry
finan.ItemsByPaymentOrder
finan.JournalEntries
finan.JournalEntriesByJournal
finan.JournalEntryItemTable
finan.PaymentOrderItemTable
finan.PaymentOrders
finan.PaymentOrdersByJournal
finan.SuggestionsByBankStatement
finan.SuggestionsByBankStatementItem
finan.SuggestionsByJournalEntry
finan.SuggestionsByPaymentOrder
finan.SuggestionsByPaymentOrderItem
finan.SuggestionsByVoucher
finan.SuggestionsByVoucherItem
gfks.BrokenGFKs
gfks.BrokenGFKsByModel
gfks.ContentTypes
invoicing.AllPlans
invoicing.FollowUpRules
invoicing.Items
invoicing.ItemsByPlan
invoicing.MyPlan
invoicing.Periodicities
invoicing.Plans
invoicing.RulesByTask
invoicing.Tariffs
invoicing.Tasks
linod.LogLevels
linod.Procedures
linod.SystemTasks
memo.Mentions
memo.MentionsByTarget
notify.AllMessages
notify.MailModes
notify.MessageTypes
notify.Messages
notify.MyMessages
notify.SubscriptionTable
peppol.Archive
peppol.InboundDocumentTable
peppol.Inbox
peppol.OutboundDocuments
peppol.OutboundStates
peppol.Outbox
peppol.ReceivedInvoicesByJournal
peppol.SyncPeppol
periods.PeriodStates
periods.PeriodTypes
periods.StoredPeriods
periods.StoredYears
phones.ContactDetailTypes
phones.ContactDetails
phones.ContactDetailsByPartner
printing.BuildMethods
products.BarcodeDrivers
products.Categories
products.DeliveryUnits
products.PriceFactors
products.PriceRules
products.ProductTypes
products.Products
products.ProductsByCategory
sepa.Accounts
sepa.AccountsByPartner
sheets.AccountEntries
sheets.AccountEntriesByReport
sheets.AnaAccountEntries
sheets.AnaAccountEntriesByReport
sheets.BalanceEntriesByReport
sheets.CommonItems
sheets.ItemEntries
sheets.Items
sheets.MovementsByItemEntry
sheets.PartnerEntries
sheets.PartnerEntriesByReport
sheets.Reports
sheets.ResultsEntriesByReport
sheets.SheetTypes
system.Dashboard
system.DisplayColors
system.DurationUnits
system.Genders
system.PeriodEvents
system.Recurrences
system.SiteConfigs
system.Weekdays
system.YesNo
trading.DocumentsToSign
trading.DueInvoices
trading.InvoiceItems
trading.InvoiceItemsByGenerator
trading.InvoiceItemsByProduct
trading.Invoices
trading.InvoicesByJournal
trading.InvoicesByPartner
trading.ItemsByInvoice
trading.ItemsByInvoicePrint
trading.ItemsByInvoicePrintNoQtyColumn
trading.PaperTypes
trading.PartnersByInvoiceRecipient
trading.PrintableInvoicesByJournal
trading.RulesByPartner
trading.TradingRules
uploads.AllUploads
uploads.AreaUploads
uploads.MyUploads
uploads.Shortcuts
uploads.UploadAreas
uploads.UploadTypes
uploads.Uploads
uploads.UploadsByController
uploads.UploadsByType
uploads.UploadsByVolume
uploads.Volumes
users.AllUsers
users.Authorities
users.AuthoritiesGiven
users.AuthoritiesTaken
users.Me
users.Sessions
users.UserRoles
users.UserTypes
users.UsersOverview
vat.DeclarationFieldsBase
vat.IntracomPurchases
vat.IntracomSales
vat.InvoiceItemTable
vat.Invoices
vat.InvoicesByJournal
vat.ItemsByInvoice
vat.MovementsByDeclaration
vat.MovementsByVoucher
vat.PrintableInvoicesByJournal
vat.PurchasesByDeclaration
vat.SalesByDeclaration
vat.VatAreas
vat.VatClasses
vat.VatColumns
vat.VatRegimes
vat.VatRules
vat.VouchersByPartner
xl.Priorities


Don't read me
=============


rt.models.trading.InvoicesByJournal.detail_layout
