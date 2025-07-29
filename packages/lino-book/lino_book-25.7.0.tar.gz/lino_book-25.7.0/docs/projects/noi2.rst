.. doctest docs/projects/noi2.rst
.. _dg.projects.noi2:

====================================================
``noi2`` : Noi with publisher and without accounting
====================================================

>>> from lino_book.projects.noi2.startup import *

>>> walk_menu_items('robin', severe=False)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF +SKIP

Installed plugins
=================

>>> for p in settings.SITE.installed_plugins:
...     print("{}: {}".format(p.app_label, p))  #doctest: +REPORT_UDIFF
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
users: lino_noi.lib.users(needs ['lino.modlib.system'])
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
bootstrap3: lino.modlib.bootstrap3(needed by lino.modlib.publisher, needs ['lino.modlib.jinja'])
publisher: lino.modlib.publisher(needed by lino_xl.lib.blogs, needs ['lino.modlib.system', 'lino.modlib.linod', 'lino.modlib.jinja', 'lino.modlib.bootstrap3'])
albums: lino_xl.lib.albums(needed by lino_xl.lib.blogs, needs ['lino.modlib.uploads'])
sources: lino_xl.lib.sources(needed by lino_xl.lib.blogs)
blogs: lino_xl.lib.blogs(needs ['lino.modlib.publisher', 'lino_xl.lib.topics', 'lino_xl.lib.albums', 'lino_xl.lib.sources'])
polls: lino_xl.lib.polls(needs ['lino_xl.lib.xl'])
about: lino.modlib.about
react: lino_react.react(needs ['lino.modlib.jinja'])
staticfiles: django.contrib.staticfiles
sessions: django.contrib.sessions

Language selector
=================

>>> lang = settings.SITE.languages[1]
>>> lang
LanguageInfo(django_code='bn', name='bn', index=1, suffix='_bn')
>>> ar = rt.login(renderer=dd.plugins.publisher.renderer)
>>> publisher.Page.objects.get(pk=1)
Page #1 ('Home')
>>> ar  = publisher.Pages.create_request(parent=ar, selected_pks=[1])
>>> print(ar.get_request_url(ul="bn"))
/p/1?ul=bn

Don't read this
===============

Pages:

>>> rt.show('publisher.Pages', display_mode="grid", column_names="ref parent title language")
=========== ============ =============================== ==========
 Reference   Parent       Title                           Language
----------- ------------ ------------------------------- ----------
 index                    Home                            en
 index                    হোম                             bn
 index                    Startseite                      de
                          Terms and conditions            en
                          Terms and conditions            bn
                          Allgemeine Geschäftsbediungen   de
                          Privacy policy                  en
                          Privacy policy                  bn
                          Datenschutz                     de
                          Cookie settings                 en
                          Cookie settings                 bn
                          Cookie settings                 de
                          Copyright                       en
                          Copyright                       bn
                          Autorenrecht                    de
                          About us                        en
                          About us                        bn
                          Über uns                        de
             Home         Calendar                        en
             হোম          Calendar                        bn
             Startseite   Kalender                        de
             Home         Blog                            en
             হোম          Blog                            bn
             Startseite   Blog                            de
                          SynodalCon
                          Cascaded Continuous Voting
                          Liquid democracy
                          Digital vs analog
                          Software should be free
                          Synodality
             Home         Mission                         en
             Home         Maxim                           en
             Home         Propaganda                      en
             Home         About us                        en
             About us     Team                            en
             About us     History                         en
             About us     Contact                         en
             About us     Terms & conditions              en
             হোম          Mission                         bn
             হোম          Maxim                           bn
             হোম          Propaganda                      bn
             হোম          About us                        bn
             About us     Team                            bn
             About us     History                         bn
             About us     Contact                         bn
             About us     Terms & conditions              bn
             Startseite   Mission                         de
             Startseite   Maxim                           de
             Startseite   Propaganda                      de
             Startseite   Über uns                        de
             Über uns     Team                            de
             Über uns     History                         de
             Über uns     Kontakt                         de
             Über uns     Nutzungsbestimmungen            de
=========== ============ =============================== ==========
<BLANKLINE>


Ensure database state:

>>> for obj in linod.SystemTask.objects.all():
...     obj.last_start_time = None
...     obj.requested_at = None
...     obj.disabled = False
...     obj.save()

>>> from logging import getLevelName
>>> from asgiref.sync import async_to_sync
>>> bt = linod.SystemTask.objects.get(procedure=linod.Procedures.update_publisher_pages)
>>> bt.status
'Scheduled to run asap'
>>> ar = rt.login("robin")
>>> print(getLevelName(ar.logger.level))
INFO
>>> ar.logger.setLevel("DEBUG")
>>> print(getLevelName(ar.logger.level))
DEBUG
>>> ar.logger.handlers
[<StreamHandler (INFO)>, <AdminEmailHandler (ERROR)>]
>>> [getLevelName(h.level) for h in ar.logger.handlers]
['INFO', 'ERROR']
>>> ar.logger.handlers[0].setLevel("DEBUG")
>>> async_to_sync(bt.start_task)(ar)
Start System task #11 (update_publisher_pages) with logging level INFO
Update publisher pages...
54 pages have been updated.
Successfully terminated System task #11 (update_publisher_pages)
>>> bt.disabled
False
>>> bt.status  #doctest: +ELLIPSIS
'Scheduled to run at ... (... from now)'

>>> bt = linod.SystemTask.objects.get(procedure=linod.Procedures.delete_older_changes)
>>> bt.status
'Scheduled to run asap'

'Scheduled to run asap'
>>> async_to_sync(bt.start_task)(ar)
Start System task #6 (delete_older_changes) with logging level INFO
Successfully terminated System task #6 (delete_older_changes)
>>> bt.disabled
False
>>> bt.status  #doctest: +ELLIPSIS
'Scheduled to run at ... (... from now)'

>>> bt.run_now.run_from_ui(ar)
>>> bt.message  #doctest: +ELLIPSIS
'Robin Rood requested to run this task at ....'

>>> bt.status  #doctest: +ELLIPSIS
'Requested to run asap (since ... (...))'

Restore database state:

>>> for obj in linod.SystemTask.objects.all():
...     obj.last_start_time = None
...     obj.requested_at = None
...     obj.disabled = False
...     obj.save()


>>> dbhash.check_virgin()
