.. doctest docs/projects/noi1r.rst
.. _dg.projects.noi1r:

=========================================
``noi1r`` : `noi1e` with React front end
=========================================

>>> from lino_book.projects.noi1r.startup import *

>>> ses = rt.login('robin')

>>> dd.plugins.accounting.sales_method
'direct'


20250615
========

You can configure the plugin setting :data:`vat.default_vat_class`.

>>> dd.plugins.vat.default_vat_class
<vat.VatClasses.services:100>

>>> prod = products.Product.objects.get(name="Hourly rate")
>>> partner = contacts.Company.objects.get(name="Garage Mergelsberg")
>>> prod
Product #2 ('Hourly rate')
>>> partner
Company #5 ('Garage Mergelsberg')

>>> invoice = trading.VatProductInvoice.objects.get(partner=partner, fiscal_year__ref="2015", journal__ref="SLS", number=10)
>>> invoice
VatProductInvoice #106 ('SLS 10/2015')

>>> line = trading.InvoiceItem.objects.get(voucher=invoice, product=prod)
>>> line.qty
Duration('14:13')

>>> tt = line.get_trade_type()
>>> tt
<accounting.TradeTypes.sales:S>

>>> line.get_default_vat_class(tt)
<vat.VatClasses.services:100>

>>> rule = line.get_vat_rule(tt)
>>> str(rule)
'VAT rule 1:\napply 0 %\nand book to None'

That's because noi1e and noi1r have no :data:`vat.declaration_plugin`.

>>> print(dd.plugins.vat.declaration_plugin)
None



Overview
========

.. module::  lino_book.projects.noi1r

The :mod:`lino_book.projects.noi1r` demo project is a :term:`satellite site` of the
:mod:`lino_book.projects.noi1e` demo project, but using the :term:`React front
end` instead of :term:`ExtJS <ExtJS front end>`.

Here is the output of :func:`walk_menu_items
<lino.api.doctests.walk_menu_items>` for this site:

>>> walk_menu_items('robin', severe=False)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
- Contacts --> Persons : 70
- Contacts --> Organizations : 27
- Contacts --> Partner Lists : 9
- Contacts --> Ibanity suppliers : 11
- Calendar --> My appointments : 1
- Calendar --> Overdue appointments : 1
- Calendar --> My unconfirmed appointments : 1
- Calendar --> My tasks : 1
- Calendar --> My guests : 1
- Calendar --> My presences : 1
- Calendar --> My overdue appointments : 1
- Calendar --> Calendar : (not tested)
- Working time --> My Tickets : 10
- Working time --> Active tickets : 66
- Working time --> All tickets : 117
- Working time --> Unassigned Tickets : 8
- Working time --> Reference Tickets : 1
- Working time --> Tickets to work : 4
- Working time --> My sessions : 0
- Working time --> Worked hours : 7
- Working time --> Working contracts : 5
- Office --> My Notification messages : 38
- Office --> My Upload files : 2
- Office --> My Excerpts : 0
- Office --> My Comments : 73
- Office --> Recent comments : 504
- Office --> Data problem messages assigned to me : 0
- Google Contacts : 1
- Sales --> Sales invoices (SLS) : (not tested)
- Sales --> Subscription invoices (SUB) : (not tested)
- Sales --> Service reports (SRV) : (not tested)
- Sales --> Service Level Agreements (SLA) : (not tested)
- Sales --> My invoicing plan : (not tested)
- Configure --> System --> Site configuration : (not tested)
- Configure --> System --> Users : 8
- Configure --> System --> Teams : 4
- Configure --> System --> System tasks : 11
- Configure --> Contacts --> Legal forms : 17
- Configure --> Contacts --> Functions : 6
- Configure --> Contacts --> List Types : 4
- Configure --> Calendar --> Calendars : 2
- Configure --> Calendar --> Rooms : 1
- Configure --> Calendar --> Recurring events : 16
- Configure --> Calendar --> Guest roles : 1
- Configure --> Calendar --> Calendar entry types : 5
- Configure --> Calendar --> Recurrency policies : 7
- Configure --> Calendar --> Remote Calendars : 1
- Configure --> Calendar --> Planner rows : 3
- Configure --> Topics --> Topics : 6
- Configure --> Working time --> Ticket types : 5
- Configure --> Working time --> Session Types : 2
- Configure --> Working time --> Reporting rules : 4
- Configure --> Working time --> Working contracts : 5
- Configure --> Office --> Library volumes : 3
- Configure --> Office --> Upload types : 2
- Configure --> Office --> Excerpt Types : 6
- Configure --> Office --> Comment Types : 1
- Configure --> Products --> Services : 11
- Configure --> Products --> Product Categories : 1
- Configure --> Products --> Price rules : 1
- Configure --> Products --> Transfer rules : 3
- Configure --> Sales --> Paper types : 3
- Configure --> Sales --> Flatrates : 1
- Configure --> Sales --> Follow-up rules : 5
- Configure --> Sales --> Invoicing tasks : 4
- Configure --> Places --> Countries : 11
- Configure --> Places --> Places : 81
- Configure --> Accounting --> Fiscal years : 10
- Configure --> Accounting --> Accounting periods : 41
- Configure --> Accounting --> Accounts : 21
- Configure --> Accounting --> Journals : 5
- Configure --> Accounting --> Payment terms : 9
- Explorer --> System --> content types : 113
- Explorer --> System --> Authorities : 1
- Explorer --> System --> User types : 5
- Explorer --> System --> User roles : 39
- Explorer --> System --> Third-party authorizations : 1
- Explorer --> System --> Changes : 0
- Explorer --> System --> Notification messages : 261
- Explorer --> System --> All dashboard widgets : 1
- Explorer --> System --> User Statistics : 37
- Explorer --> System --> Group memberships : 8
- Explorer --> System --> Background procedures : 11
- Explorer --> System --> Data checkers : 19
- Explorer --> System --> Data problem messages : 0
- Explorer --> Contacts --> Contact persons : 9
- Explorer --> Contacts --> Partners : 96
- Explorer --> Contacts --> List memberships : 96
- Explorer --> Contacts --> Address types : 6
- Explorer --> Contacts --> Addresses : 125
- Explorer --> Contacts --> Contact detail types : 6
- Explorer --> Contacts --> Contact details : 26
- Explorer --> Calendar --> Calendar entries : 84
- Explorer --> Calendar --> Tasks : 1
- Explorer --> Calendar --> Subscriptions : 1
- Explorer --> Calendar --> Entry states : 6
- Explorer --> Calendar --> Presence states : 5
- Explorer --> Calendar --> Task states : 5
- Explorer --> Calendar --> Planner columns : 2
- Explorer --> Calendar --> Display colors : 26
- Explorer --> Topics --> Tags : 118
- Explorer --> Topics --> Interests : 1
- Explorer --> Working time --> Ticket states : 9
- Explorer --> Working time --> Checks : 1
- Explorer --> Working time --> Nicknamings : 22
- Explorer --> Working time --> Working sessions : 2384
- Explorer --> Working time --> Order summaries : 15
- Explorer --> Working time --> User summaries : 1092
- Explorer --> Working time --> Reporting types : 2
- Explorer --> Office --> Upload files : 4
- Explorer --> Office --> Upload areas : 1
- Explorer --> Office --> Excerpts : 3
- Explorer --> Office --> Mentions : 153
- Explorer --> Office --> Comments : 505
- Explorer --> Office --> Reactions : 0
- Explorer --> Products --> Price factors : 0
- Explorer --> Products --> Provision states : 1
- Explorer --> Products --> Storage fillers : 6
- Explorer --> Products --> Delivery notes : 56
- Explorer --> Products --> Delivery items : 625
- Explorer --> Products --> Storage movements : 94
- Explorer --> Products --> Provisions : 6
- Explorer --> Products --> Components : 5
- Explorer --> Sales --> Trading rules : 83
- Explorer --> Sales --> Trading invoices : 51
- Explorer --> Sales --> Trading invoice items : 127
- Explorer --> Sales --> All subscriptions : 6
- Explorer --> Sales --> Subscription periods : 11
- Explorer --> Sales --> Invoicing plans : 2
- Explorer --> Google API --> Syncable Contacts : 0
- Explorer --> Google API --> Syncable Events : 0
- Explorer --> Google API --> Deleted Contacts : 0
- Explorer --> Google API --> Deleted Cal Entries : 0
- Explorer --> Google API --> Sync Summaries : 0
- Explorer --> Accounting --> Common accounts : 21
- Explorer --> Accounting --> Match rules : 1
- Explorer --> Accounting --> Vouchers : 110
- Explorer --> Accounting --> Voucher types : 4
- Explorer --> Accounting --> Movements : 100
- Explorer --> Accounting --> Trade types : 6
- Explorer --> Accounting --> Journal groups : 6
- Explorer --> VAT --> VAT areas : 3
- Explorer --> VAT --> VAT regimes : 1
- Explorer --> VAT --> VAT classes : 8
- Explorer --> VAT --> VAT columns : 0
- Explorer --> VAT --> Ledger invoices : 1
- Explorer --> VAT --> VAT rules : 1
- Site --> User sessions : ...
- Site --> About : (not tested)
<BLANKLINE>


Dependencies
============

This project needs a bit more Python packages installed than usual. They should
have been installed automatically into your :term:`developer environment`. In
case of doubt you can also run :manage:`install` command manually:

>>> from django.core.management import call_command
>>> call_command('install', list=True)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
appy
atelier
beautifulsoup4
channels
channels_redis
daphne
djangorestframework
google-api-python-client
google-auth
google-auth-httplib2
google-auth-oauthlib
imagesize
lino_react
num2words
odfpy
openpyxl
pywebpush
social-auth-app-django


Don't read me
=============

In a tested doc that uses the React front end, don't forget to prefix your URLs
with "/#":

>>> url = "/api/comments/CommentsByRFC"
>>> res = test_client.get(url)
... #doctest: +NORMALIZE_WHITESPACE -REPORT_UDIFF +ELLIPSIS
Error during kernel.run_action() in ActionRequest for ShowTable on comments.CommentsByRFC: ShowTable has no run_from_ui() method
ShowTable has no run_from_ui() method
Traceback (most recent call last):
...
django.core.exceptions.BadRequest: ShowTable has no run_from_ui() method

>>> url = "/#/api/comments/CommentsByRFC"
>>> res = test_client.get(url)
... #doctest: +NORMALIZE_WHITESPACE -REPORT_UDIFF +ELLIPSIS
>>> res.status_code
200

The following request failed on 20241009 because Lino tried to set `pv`, `mt`
and `mk` on a request without an actor:

>>> url = "/user/settings/?dm=grid&mk=1&mt=23&pv=&pv=&pv=&pv=&pv=&ul=de&wt=t"
>>> res = test_client.get(url)
... #doctest: +NORMALIZE_WHITESPACE -REPORT_UDIFF +ELLIPSIS
>>> res.status_code
200
>>> print(res.content.decode())  #doctest: +ELLIPSIS
{ "act_as_button_text": "Act as another user", ...}


Installed plugins
=================

>>> for p in settings.SITE.installed_plugins:
...     print("{}: {}".format(p.app_label, p))
... #doctest: +REPORT_UDIFF
lino: lino
printing: lino.modlib.printing(needed by lino.modlib.system)
system: lino.modlib.system(needs ['lino.modlib.printing'])
contenttypes: django.contrib.contenttypes(needed by lino.modlib.gfks)
gfks: lino.modlib.gfks(needs ['lino.modlib.system', 'django.contrib.contenttypes'])
help: lino.modlib.help(needs ['lino.modlib.system'])
office: lino.modlib.office(needed by lino_xl.lib.countries)
xl: lino_xl.lib.xl(needed by lino_xl.lib.countries)
countries: lino_xl.lib.countries(needed by lino_noi.lib.contacts, needs ['lino.modlib.office', 'lino_xl.lib.xl'])
contacts: lino_noi.lib.contacts(needs ['lino_xl.lib.countries', 'lino.modlib.system'])
social_django: social_django(needed by lino_noi.lib.users)
users: lino_noi.lib.users(needs ['lino.modlib.system', 'social_django', 'social_django'])
noi: lino_noi.lib.noi(needed by lino_noi.lib.cal)
cal: lino_noi.lib.cal(needs ['lino.modlib.gfks', 'lino.modlib.printing', 'lino_xl.lib.xl', 'lino_noi.lib.noi'])
calview: lino_xl.lib.calview(needs ['lino_xl.lib.cal'])
topics: lino_xl.lib.topics(needs ['lino_xl.lib.xl', 'lino.modlib.gfks'])
excerpts: lino_xl.lib.excerpts(needed by lino_noi.lib.tickets, needs ['lino.modlib.gfks', 'lino.modlib.printing', 'lino.modlib.office', 'lino_xl.lib.xl'])
memo: lino.modlib.memo(needed by lino.modlib.comments, needs ['lino.modlib.office', 'lino.modlib.gfks'])
comments: lino.modlib.comments(needed by lino_noi.lib.tickets, needs ['lino.modlib.memo'])
tickets: lino_noi.lib.tickets(needs ['lino_xl.lib.excerpts', 'lino.modlib.comments', 'lino_noi.lib.noi'])
nicknames: lino_xl.lib.nicknames
summaries: lino.modlib.summaries(needed by lino_xl.lib.working)
channels: channels(needed by lino.modlib.linod)
daphne: daphne(needed by lino.modlib.linod)
linod: lino.modlib.linod(needed by lino.modlib.checkdata)
checkdata: lino.modlib.checkdata(needed by lino_xl.lib.working, needs ['lino.modlib.users', 'lino.modlib.gfks', 'lino.modlib.office', 'lino.modlib.linod'])
working: lino_xl.lib.working(needs ['lino.modlib.summaries', 'lino.modlib.checkdata'])
lists: lino_xl.lib.lists
changes: lino.modlib.changes(needs ['lino.modlib.users', 'lino.modlib.gfks'])
notify: lino.modlib.notify(needs ['lino.modlib.users', 'lino.modlib.memo', 'lino.modlib.linod'])
uploads: lino.modlib.uploads
export_excel: lino.modlib.export_excel
tinymce: lino.modlib.tinymce(needs ['lino.modlib.office'])
smtpd: lino.modlib.smtpd
jinja: lino.modlib.jinja(needed by lino.modlib.weasyprint)
weasyprint: lino.modlib.weasyprint(needs ['lino.modlib.jinja'])
appypod: lino_xl.lib.appypod
dashboard: lino.modlib.dashboard(needs ['lino.modlib.users'])
inbox: lino_xl.lib.inbox(needs ['lino.modlib.comments'])
userstats: lino_xl.lib.userstats(needs ['lino.modlib.users'])
groups: lino_noi.lib.groups
products: lino_noi.lib.products(needs ['lino_xl.lib.xl'])
periods: lino.modlib.periods(needed by lino_xl.lib.accounting)
accounting: lino_xl.lib.accounting(needed by lino_xl.lib.vat, needs ['lino.modlib.periods', 'lino.modlib.weasyprint', 'lino_xl.lib.xl', 'lino.modlib.uploads'])
vat: lino_xl.lib.vat(needed by lino_noi.lib.trading, needs ['lino.modlib.checkdata', 'lino_xl.lib.excerpts'])
trading: lino_noi.lib.trading(needs ['lino.modlib.memo', 'lino_xl.lib.products', 'lino_xl.lib.vat'])
storage: lino_xl.lib.storage(needs ['lino_xl.lib.products', 'lino.modlib.summaries'])
invoicing: lino_xl.lib.invoicing(needed by lino_noi.lib.subscriptions, needs ['lino_xl.lib.trading'])
subscriptions: lino_noi.lib.subscriptions(needs ['lino_xl.lib.invoicing'])
sepa: lino_xl.lib.sepa
peppol: lino_xl.lib.peppol(needs ['lino_xl.lib.vat'])
about: lino.modlib.about
react: lino_react.react(needs ['lino.modlib.jinja'])
rest_framework: rest_framework(needed by lino.modlib.restful)
restful: lino.modlib.restful(needs ['rest_framework'])
addresses: lino_xl.lib.addresses(needed by lino_xl.lib.google, needs ['lino.modlib.checkdata'])
phones: lino_xl.lib.phones(needed by lino_xl.lib.google)
google: lino_xl.lib.google(needs ['lino.modlib.users', 'lino_xl.lib.addresses', 'lino_xl.lib.phones'])
search: lino.modlib.search
staticfiles: django.contrib.staticfiles
sessions: django.contrib.sessions
