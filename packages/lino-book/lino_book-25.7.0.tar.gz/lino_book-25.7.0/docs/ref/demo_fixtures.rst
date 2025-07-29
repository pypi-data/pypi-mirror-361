===================================
Loading order of the demo fixtures
===================================

The :term:`application developer` is responsible for specifying a meaningful
list of names in the :attr:`demo_fixtures <lino.core.site.Site.demo_fixtures>`
setting. This can be challenging because the loading order of fixtures can be
important when one fixture depends on data that has been loaded by another
fixture.

.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst


>>> from lino import startup
>>> startup('lino_book.projects.cosi4.settings')
>>> from lino.api.doctest import *

We recommend to define the following names of demo fixtures::

    std minimal_ledger demo demo_bookings payments demo2 demo3 checksummaries checkdata

:fixture:`std`
:fixture:`minimal_ledger`
:fixture:`demo`
:fixture:`demo_bookings`
:fixture:`payments`
:fixture:`demo2`
:fixture:`demo3`
:fixture:`checksummaries`
:fixture:`checkdata`
:fixture:`linod`

With this convention we can see each fixture name as a **loading phase**.

The loading order of demo data is important because the fixtures of the
:ref:`xl` are inter-dependent.  They create users, cities, journals, contacts,
invoices, payments, reports, notifications, ...  you cannot write invoices if
you have no customers, and an accounting report makes no sense if bank
statements haven't been entered.

Lino basically uses Django's approach of finding demo fixtures: When Django
gets a series of fixture names to load, it will load them in the specified
order, and for each fixture will ask each plugin to load that fixture.  If a
plugin doesn't define a fixture of that name, it simply does nothing.


all_countries
=============

.. fixture:: all_countries

The :fixture:`all_countries` fixture defines 224 countries, 195 of which have a
2-letter ISO code and 29 have a 4-letter ISO code because they no longer exist.

The :fixture:`all_countries` fixture is not part of the default list because
:fixture:`few_countries` is more practical for testing and manipulating.

Until 2024-03-10 it defined 46 more "countries" like
`NF Norfolk Island <https://en.wikipedia.org/wiki/Norfolk_Island>`__,
`MQ Martinique <https://en.wikipedia.org/wiki/Martinique>`__ and
`NC New Caledonia <https://en.wikipedia.org/wiki/New_Caledonia>`__.


>>> qs = countries.Country.objects.all()
>>> qs.count()
224
>>> n = 0
>>> for o in qs:
...    if len(o.isocode) == 2:
...        print(o.pk, o.name)
...        n += 1
... #doctest: +REPORT_UDIFF +ELLIPSIS +NORMALIZE_WHITESPACE
AD Andorra
AE United Arab Emirates
AF Afghanistan
AG Antigua and Barbuda
AL Albania
AM Armenia
AO Angola
AR Argentina
AT Austria
AU Australia
AZ Azerbaijan
BA Bosnia and Herzegovina
BB Barbados
BD Bangladesh
BE Belgium
BF Burkina Faso
BG Bulgaria
BH Bahrain
BI Burundi
BJ Benin
BN Brunei
BO Bolivia
BR Brazil
BS The Bahamas
BT Bhutan
BW Botswana
BY Belarus
BZ Belize
CA Canada
CD Democratic Republic of the Congo
CF Central African Republic
CG Republic of the Congo
CH Switzerland
CI Ivory Coast
CL Chile
CM Cameroon
CN People's Republic of China
CO Colombia
CR Costa Rica
CU Cuba
CV Cape Verde
CY Cyprus
CZ Czech Republic
DE Germany
DJ Djibouti
DM Dominica
DO Dominican Republic
DZ Algeria
EC Ecuador
EE Estonia
EG Egypt
ER Eritrea
ES Spain
ET Ethiopia
FI Finland
FJ Fiji
FM Federated States of Micronesia
FR France
GA Gabon
GB United Kingdom
GD Grenada
GE Georgia
GH Ghana
GM ...Gambia
GN Guinea
GQ Equatorial Guinea
GR Greece
GT Guatemala
GW Guinea-Bissau
GY Guyana
HN Honduras
HR Croatia
HT Haiti
HU Hungary
ID Indonesia
IE Ireland
IL Israel
IN India
IQ Iraq
IR Iran
IS Iceland
IT Italy
JM Jamaica
JO Jordan
JP Japan
KE Kenya
KG Kyrgyzstan
KH Cambodia
KI Kiribati
KM Comoros
KN Saint Kitts and Nevis
KP North Korea
KR South Korea
KW Kuwait
KZ Kazakhstan
LA Laos
LB Lebanon
LC Saint Lucia
LI Liechtenstein
LK Sri Lanka
LR Liberia
LS Lesotho
LT Lithuania
LU Luxembourg
LV Latvia
LY Libya
MA Morocco
MC Monaco
MD Moldova
ME Montenegro
MG Madagascar
MH Marshall Islands
MK North Macedonia
ML Mali
MM Myanmar
MN Mongolia
MR Mauritania
MT Malta
MU Mauritius
MV Maldives
MW Malawi
MX Mexico
MY Malaysia
MZ Mozambique
NA Namibia
NE Niger
NG Nigeria
NI Nicaragua
NL Kingdom of the Netherlands
NO Norway
NP Nepal
NR Nauru
NZ New Zealand
OM Oman
PA Panama
PE Peru
PG Papua New Guinea
PH Philippines
PK Pakistan
PL Poland
PS Palestine
PT Portugal
PW Palau
PY Paraguay
QA Qatar
RO Romania
RS Serbia
RU Russia
RW Rwanda
SA Saudi Arabia
SB Solomon Islands
SC Seychelles
SD Sudan
SE Sweden
SG Singapore
SI Slovenia
SK Slovakia
SL Sierra Leone
SM San Marino
SN Senegal
SO Somalia
SR Suriname
SS South Sudan
ST São Tomé and Príncipe
SV El Salvador
SY Syria
SZ Eswatini
TD Chad
TG Togo
TH Thailand
TJ Tajikistan
TL Timor-Leste
TM Turkmenistan
TN Tunisia
TO Tonga
TR Turkey
TT Trinidad and Tobago
TV Tuvalu
TW Taiwan
TZ Tanzania
UA Ukraine
UG Uganda
US United States
UY Uruguay
UZ Uzbekistan
VA Vatican City
VC Saint Vincent and the Grenadines
VE Venezuela
VN Vietnam
VU Vanuatu
WS Samoa
YE Yemen
ZA South Africa
ZM Zambia
ZW Zimbabwe

>>> n
195

std
===

.. fixture:: std

The :fixture:`std` fixtures should add default database content expected to be
in a virgin database even when no "demo data" is requested. This should always
be the first fixture of your :attr:`demo_fixtures
<lino.core.site.Site.demo_fixtures>` setting.  It is provided by the following
plugins:

- :mod:`lino.modlib.users`
  Create an excerpt type "Welcome letter" (when appypod and excerpts are installed)

- :mod:`lino.modlib.tinymce`
- :mod:`lino.modlib.gfks`
- :mod:`lino_xl.lib.cv`
- :mod:`lino_xl.lib.coachings`
- :mod:`lino_xl.lib.bevat` creates an excerpt type for the VAT declaration.
- :mod:`lino_xl.lib.bevats` does nothing
- :mod:`lino_xl.lib.eevat` does nothing
- :mod:`lino_xl.lib.contacts` adds a series of default company types.

- :mod:`lino_xl.lib.deploy`
- :mod:`lino.modlib.publisher`

- :mod:`lino_xl.lib.accounting` creates some *payment terms*.
  Creates an *account* for every item of
  :class:`CommonAccounts <lino_xl.lib.accounting.CommonAccounts>`, which results in a minimal
  accounts chart.

- :mod:`lino_xl.lib.sheets`
  creates common sheet items and assigns them to their accounts.

- :mod:`lino_xl.lib.households` adds some household member roles.

- :mod:`lino_xl.lib.cal` installs standard calendar entry types, including a
  set of holidays.  (TODO: make them more configurable.)
  The default value of
  :attr:`lino.modlib.system.SiteConfig.hide_events_before` is set to
  January 1st (of the current year when demo_date is after April and of
  the previous year when demo_date is before April).
  See also :ref:`xl.specs.holidays`.

- :mod:`lino_xl.lib.trading` creates some common paper types.

- :mod:`lino_xl.lib.working`
- :mod:`lino_xl.lib.polls`
- :mod:`lino_xl.lib.notes`
- :mod:`lino_xl.lib.excerpts`

minimal_ledger
==============

.. fixture:: minimal_ledger

Add minimal config data.
Should come after :fixture:`std` and before :fixture:`demo`.
Some day we should rename this to "predemo"

- :mod:`lino_xl.lib.accounting` adds a minimal set of journals and match rules.

- :mod:`lino_xl.lib.vat` sets VAT column for common accounts

- :mod:`lino_xl.lib.ana` creates analytic accounts and
  assigns one of them to each general account with :attr:`needs_ana` True

demo
====

.. fixture:: demo

Adds master demo data.

- The application plugins of applications with :mod:`lino_xl.lib.invoicing`
  (:mod:`lino_noi.lib.noi`, :mod:`lino_voga.lib.voga`,
  :mod:`lino_tera.lib.tera`, etc...) define :term:`invoicing tasks <invoicing
  task>` and follow-up rules.

- :mod:`lino.modlib.users`
  adds fictive root users (administrators), one for
  each language.  These names are being used by the online demo
  sites.
  We are trying to sound realistic without actually hitting any real
  person.

- :mod:`lino_xl.lib.humanlinks` creates two fictive families (Hubert & Gaby
  Frisch-Frogemuth with their children and grand-children).


- :mod:`lino_xl.lib.sepa` adds some commonly known companies and their bank
  accounts. These are real data collected from Internet.

- :mod:`lino_xl.lib.countries` adds
  :mod:`few_countries <lino_xl.lib.countries.fixtures.few_countries>`
  and
  :mod:`few_cities <lino_xl.lib.countries.fixtures.few_cities>`.

- :mod:`lino_xl.lib.contacts`
  adds a series of fictive persons and companies.

- :mod:`lino_xl.lib.mailbox`
  Adds a mailbox named "team".

- :mod:`lino_xl.lib.accounting`
  sets :attr:`lino_xl.lib.contacts.Partner.payment_term` of all partners.

- :mod:`lino_xl.lib.vat`
  Sets fictive VAT id for all companies and then a VAT regime for all partners.

- :mod:`lino_xl.lib.sheets`
  adds an excerpt type to print a sheets.Report

- :mod:`lino_xl.lib.households`
  creates some households by marrying a few Persons.
  Every third household gets divorced: we put an `end_date` to that
  membership and create another membership for the same person with
  another person.

- :mod:`lino_xl.lib.lists`

- :mod:`lino_xl.lib.groups`
  creates some user groups and users Andy, Bert and Chloé.

- :mod:`lino_xl.lib.notes`

demo_bookings
=============

.. fixture:: demo_bookings

Adds more demo data (originally "bookings").
Should come after :fixture:`demo`.

- :mod:`lino_xl.lib.invoicing`
  creates monthly invoicing plans and executes them.
  Starts a January 1st of :attr:`lino_xl.lib.accounting.Plugin.start_year`.
  Stops 2 months before today (we "forgot" to run invoicing the last two months)
  because we want to have something in our invoicing plan.

- :mod:`lino_xl.lib.accounting`
  Creates fictive monthly purchase invoices.
  For some of them it creates a dummy upload file that represents the source document.

- :mod:`lino_xl.lib.trading` creates fictive monthly sales.

payments
========

.. fixture:: payments

Adds even more demo data (originally "payments").
Should come after :fixture:`demo_bookings`.

- :mod:`lino_xl.lib.bevat`
  creates a Belgian VAT office and some VAT declarations.

- :mod:`lino_xl.lib.bevats`
  creates a Belgian VAT office and some VAT declarations.

- :mod:`lino_xl.lib.eevat`
  creates an Estonian VAT office and some VAT declarations.

- :mod:`lino_xl.lib.finan` creates automatic monthly payment orders and bank
  statements.  Bank statements of last month are not yet entered into database

demo2
=====

.. fixture:: demo2

Add final demo data.

- :mod:`lino.modlib.users` sets password 1234 for all users.

- :mod:`lino.modlib.comments` adds some fictive comments.

- :mod:`lino.modlib.notify`
  sends a notification "The database has been initialized" to every user.

- :mod:`lino_xl.lib.addresses`
  adds some additional non-primary addresses to some partners.

- :mod:`lino_xl.lib.sheets`
  creates some accounting reports (one per year).

- :mod:`lino_xl.lib.cal`
  generates 60 fictive appointments and 10 absences "for private reasons".

- :mod:`lino_xl.lib.phones`
  runs :meth:`propagate_contact_details` for each partner.

- :mod:`lino_xl.lib.groups`
  creates a membership for every user in one or two groups and a welcome comment
  for each membership.

- :mod:`lino_xl.lib.polls`
  creates a response for every poll.

- :mod:`lino_xl.lib.votes.fixtures.demo2`
- :mod:`lino_xl.lib.dupable_partners.fixtures.demo2`
- :mod:`lino_xl.lib.excerpts.fixtures.demo2`

demo3
=====

.. fixture:: demo3

- :mod:`lino.modlib.uploads` creates an orphan file :file:`foo.pdf` in uploads
  folder and removes the file of one first upload entry to simulate some data
  issues to detect by :fixture:`checkdata`.

checksummaries
==============

.. fixture:: checksummaries

- :mod:`lino.modlib.summaries` runs the :cmd:`pm checksummaries` command.

checkdata
=========

.. fixture:: checkdata

Should come after :fixture:`demo2`.

This fixture should always be the last in your :attr:`demo_fixtures
<lino.core.site.Site.demo_fixtures>` setting.
