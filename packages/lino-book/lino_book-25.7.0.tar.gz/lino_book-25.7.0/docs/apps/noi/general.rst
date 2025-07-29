.. doctest docs/apps/noi/general.rst
.. _noi.specs.general:

=================
Lino Noi Overview
=================

The goal of Lino Noi is managing **tickets** (problems reported by customers or
other users) and registering the **working time** needed by developers or other
users to work on these tickets. It is then possible to publish **service
reports**. It is also used for managing agile development projects.



.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *


Configuration options
=====================

Lino Noi defines two application options:
:attr:`with_accounting <lino_noi.lib.noi.settings.Site.with_accounting>`
and
:attr:`with_cms <lino_noi.lib.noi.settings.Site.with_cms>`.



Plugin dependencies
===================

>>> dd.is_installed('products')
True

>>> dd.plugins.tickets
<lino_noi.lib.tickets.Plugin lino_noi.lib.tickets(needs ['lino_xl.lib.excerpts', 'lino.modlib.comments', 'lino_noi.lib.noi'])>

>>> dd.plugins.working
<lino_xl.lib.working.Plugin lino_xl.lib.working(needs ['lino.modlib.summaries', 'lino.modlib.checkdata'])>

>>> dd.plugins.cal
<lino_noi.lib.cal.Plugin lino_noi.lib.cal(needs ['lino.modlib.gfks', 'lino.modlib.printing', 'lino_xl.lib.xl', 'lino_noi.lib.noi'])>


Ticket management versus worktime tracking
==========================================

Lino Noi uses both :mod:`lino_xl.lib.tickets` (Ticket management) and
:mod:`lino_xl.lib.working` (Worktime tracking).

But :mod:`lino_xl.lib.tickets` is an independent plugin that might be reused by
other applications that have no worktime tracking.  Lino Noi uses them both and
extends the "library" version of tickets:

- :mod:`lino_noi.lib.tickets`

>>> sc = rt.models.checkdata.Checkers.get_by_value('working.SessionChecker')
>>> sc.get_checkable_models()
[<class 'lino_xl.lib.working.models.Session'>]
>>> m = sc.get_checkable_models()[0]
>>> m._meta.abstract
False

Countries
=========

>>> rt.show(countries.Countries)
============================= ================================ ================================= ==========
 Designation                   Designation (de)                 Designation (fr)                  ISO code
----------------------------- -------------------------------- --------------------------------- ----------
 Bangladesh                    Bangladesh                       Bangladesh                        BD
 Belgium                       Belgien                          Belgique                          BE
 Congo (Democratic Republic)   Kongo (Demokratische Republik)   Congo (République democratique)   CD
 Estonia                       Estland                          Estonie                           EE
 France                        Frankreich                       France                            FR
 Germany                       Deutschland                      Allemagne                         DE
 Maroc                         Marokko                          Maroc                             MA
 Netherlands                   Niederlande                      Pays-Bas                          NL
 Russia                        Russland                         Russie                            RU
 United States                 United States                    United States                     US
============================= ================================ ================================= ==========
<BLANKLINE>


.. just another test:

    >>> json_fields = 'count rows title success no_data_text'
    >>> kwargs = dict(fmt='json', limit=10, start=0)
    >>> demo_get('robin', 'api/countries/Countries', json_fields, 11, **kwargs)



Lino Noi and Scrum
==================

- Every sprint is registered as a project
- Usually there is at least one ticket per project for planning and
  discussion.
- Every backlog item is registered as a ticket on that project
- The detail view of a project is the equivalent of a backlog

>>> show_fields(system.SiteConfig)
... #doctest: +REPORT_UDIFF
- Default build method (default_build_method) : The default build method to use when rendering printable documents.
- Simulated date (simulate_today) : A constant user-defined date to be substituted as current system date.
- Default Event Type (default_event_type) : The default type of events on this site.
- Site Calendar (site_calendar) : The default calendar of this site.
- Max automatic events (max_auto_events) : Maximum number of automatic events to be generated.
- Hide events before (hide_events_before) : If this is not empty, any calendar events before that date are being hidden in certain places.
- None (navigation_panel) : A virtual field that displays the navigation panel for this row. This may be included in a detail layout, usually either on the left or the right side with full height.
- Workflow (workflow_buttons) : Shows the current workflow state of this database row and a list of available workflow actions.
- None (overview) : A multi-paragraph representation of this database row.


On 20211014 we had a :message:`TypeError: get_requirements() takes 1 positional
argument but 2 were given`. This is now covered for Noi by the following
snippet:

>>> settings.SITE.get_requirements()  #doctest: +NORMALIZE_WHITESPACE
['appy', 'atelier', 'beautifulsoup4', 'channels', 'channels_redis', 'daphne',
'djangorestframework', 'google-api-python-client', 'google-auth',
'google-auth-httplib2', 'google-auth-oauthlib', 'imagesize', 'num2words',
'odfpy', 'openpyxl', 'pywebpush', 'social-auth-app-django']


>>> show_choicelists()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=========================== ======== ================= ============================ ========================== ============================
 name                        #items   preferred_width   en                           de                         fr
--------------------------- -------- ----------------- ---------------------------- -------------------------- ----------------------------
 about.DateFormats           4        8                 Date formats                 Date formats               Date formats
 about.TimeZones             4        15                Time zones                   Zeitzonen                  Time zones
 accounting.CommonAccounts   21       23                Common accounts              Gemeinkonten               Comptes communs
 accounting.DC               2        6                 Booking directions           Buchungsrichtungen         Directions d'imputation
 accounting.JournalGroups    6        26                Journal groups               Journalgruppen             Groupes de journaux
 accounting.TradeTypes       6        19                Trade types                  Handelsarten               Types de commerce
 accounting.VoucherStates    3        10                Voucher states               Belegzustände              Voucher states
 accounting.VoucherTypes     4        51                Voucher types                Belegarten                 Types de pièce
 addresses.AddressTypes      6        18                Address types                Adressenarten              Types d'adresses
 addresses.DataSources       2        16                Data sources                 Datenquellen               Sources de données
 cal.EntryStates             6        10                Entry states                 Kalendereintrag-Zustände   Entry states
 cal.EventEvents             2        8                 Observed events              Beobachtungskriterien      Évènements observés
 cal.GuestStates             5        9                 Presence states              Anwesenheits-Zustände      Presence states
 cal.NotifyBeforeUnits       4        7                 Notify Units                 Notify Units               Notify Units
 cal.PlannerColumns          2        8                 Planner columns              Tagesplanerkolonnen        Colonnes planificateur
 cal.ReservationStates       0        4                 States                       Zustände                   États
 cal.TaskStates              5        9                 Task states                  Aufgaben-Zustände          Task states
 cal.YearMonths              12       9                 None                         None                       None
 calview.Planners            1        8                 None                         None                       None
 changes.ChangeTypes         6        12                Change Types                 Änderungsarten             Change Types
 checkdata.Checkers          19       33                Data checkers                Datentests                 Tests de données
 comments.CommentEvents      2        8                 Observed events              Beobachtungskriterien      Évènements observés
 comments.Emotions           3        8                 Emotions                     Emotionen                  Emotions
 contacts.CivilStates        7        18                Civil states                 Zivilstände                Etats civils
 contacts.PartnerEvents      1        18                Observed events              Beobachtungskriterien      Évènements observés
 countries.PlaceTypes        23       14                None                         None                       None
 excerpts.Shortcuts          0        4                 Excerpt shortcuts            Excerpt shortcuts          Excerpt shortcuts
 google.AccessRoles          4        16                None                         None                       None
 invoicing.Periodicities     4        9                 Subscription periodicities   Abonnementperiodizitäten   Subscription periodicities
 linod.LogLevels             5        8                 Logging levels               Logging levels             Logging levels
 linod.Procedures            11       28                Background procedures        Background procedures      Background procedures
 notify.MailModes            5        19                Notification modes           Benachrichtigungsmodi      Modes de notification
 notify.MessageTypes         4        14                Message Types                Message Types              Types de message
 peppol.OnboardingStates     6        10                Onboarding states            Onboarding states          Onboarding states
 periods.PeriodStates        2        6                 States                       Zustände                   États
 periods.PeriodTypes         4        9                 Period types                 Period types               Period types
 phones.ContactDetailTypes   6        7                 Contact detail types         Kontaktangabenarten        Contact detail types
 printing.BuildMethods       10       20                None                         None                       None
 products.BarcodeDrivers     2        4                 Barcode drivers              Barcode drivers            Barcode drivers
 products.DeliveryUnits      13       13                Delivery units               Liefereinheiten            Unités de livraison
 products.PriceFactors       0        4                 Price factors                Preisfaktoren              Price factors
 products.ProductTypes       1        8                 Product types                Product types              Product types
 storage.ProvisionStates     1        9                 Provision states             Provision states           Provision states
 system.DisplayColors        26       10                Display colors               Display colors             Display colors
 system.DurationUnits        7        7                 None                         None                       None
 system.Genders              3        9                 Genders                      Geschlechter               Sexes
 system.PeriodEvents         3        9                 Observed events              Beobachtungskriterien      Évènements observés
 system.Recurrences          11       18                Recurrences                  Wiederholungen             Récurrences
 system.Weekdays             7        9                 None                         None                       None
 system.YesNo                2        12                Yes or no                    Ja oder Nein               Oui ou non
 tickets.TicketEvents        3        18                Observed events              Beobachtungskriterien      Évènements observés
 tickets.TicketStates        9        8                 Ticket states                Ticketzustände             Ticket states
 uploads.Shortcuts           1        15                Upload shortcuts             Upload shortcuts           Upload shortcuts
 uploads.UploadAreas         1        7                 Upload areas                 Upload-Bereiche            Domaines de téléchargement
 users.UserTypes             5        19                User types                   Benutzerarten              Types d'utilisateur
 vat.DeclarationFieldsBase   0        4                 Declaration fields           Deklarationsfelder         Declaration fields
 vat.VatAreas                3        13                VAT areas                    MWSt-Zonen                 Zones TVA
 vat.VatClasses              8        25                VAT classes                  MwSt.-Klassen              Classes TVA
 vat.VatColumns              0        4                 VAT columns                  MWSt-Kolonnen              VAT columns
 vat.VatRegimes              1        6                 VAT regimes                  MwSt.-Regimes              VAT regimes
 vat.VatRules                1        38                VAT rules                    MwSt-Regeln                VAT rules
 working.ReportingTypes      2        7                 Reporting types              Reporting types            Reporting types
 xl.Priorities               5        8                 Priorities                   Prioritäten                Priorités
=========================== ======== ================= ============================ ========================== ============================
<BLANKLINE>


Display modes
=============

>>> show_display_modes()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF +SKIP
