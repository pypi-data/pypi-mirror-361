.. doctest docs/specs/react/linoweb.rst
.. _specs.linoweb:

=======
linoweb
=======

>>> from lino_book.projects.noi1r.startup import *

>>> from django.contrib.staticfiles import finders
>>> from django.contrib.staticfiles.storage import staticfiles_storage

Static files
============

For some reason the Django test client doesn't find static files until 20221019.

>>> test_client.get("/media/cache/js/lino_900_en.js")  #doctest: +SKIP
<FileResponse status_code=200, "text/javascript">


'TableRequest' object has no attribute 'obj2str'
================================================

The following snippets failed on 2023-02-16

>>> rt.login("robin").show(contacts.Roles)
==== ========== ===================== =====================
 ID   Function   Person                Organization
---- ---------- --------------------- ---------------------
 1    CEO        Annette Arens         Bäckerei Ausdemwald
 2    CEO        Erna Ärgerlich        Garage Mergelsberg
 3    CEO        Erna Ärgerlich        Rumma & Ko OÜ
 4               Andreas Arens         Rumma & Ko OÜ
 5               Annette Arens         Bäckerei Ausdemwald
 6               Hans Altenberg        Bäckerei Mießen
 7               Alfons Ausdemwald     Bäckerei Schmitz
 8               Laurent Bastiaensen   Garage Mergelsberg
==== ========== ===================== =====================
<BLANKLINE>

#5739 (Oops, get_atomizer() returned None)
==========================================

The following snippet reproduced an example of :ticket:`5739` (Oops,
get_atomizer(...) returned None). Lino did "Oops" only the first time, and from
then on did its job. The problem disappeared for end users after simply hitting
:kbd:`Ctrl+R`.   It was because the html boxes created by
:class:`LightWeightContainer` for rendering a slave table as delayed value were
created lazily after :term:`site startup`. Since 20250523 the
:meth:`Kernel.kernel_startup` triggers their creation.

>>> erna = contacts.Role.objects.get(pk=2).person
>>> print(erna.pk)
69

>>> url  = "values/contacts/Persons/{}/contacts.RolesByPerson".format(erna.pk)

>>> demo_get('robin', url, None, -1)  #doctest: +NORMALIZE_WHITESPACE +SKIP
GET /values/contacts/Persons/69/contacts.RolesByPerson for user Robin Rood got
{'data': 'Oops, get_atomizer(lino_xl.lib.contacts.models.Persons, '
         "lino_xl.lib.contacts.models.RolesByPerson, 'contacts.RolesByPerson') "
         'returned None'}


>>> demo_get('robin', url, None, -1)  #doctest: +NORMALIZE_WHITESPACE -REPORT_UDIFF
GET /values/contacts/Persons/69/contacts.RolesByPerson for user Robin Rood got
{'data': '<div class="htmlText"><a href="javascript:window.App.runAction({ '
         '&quot;action_full_name&quot;: &quot;contacts.Companies.detail&quot;, '
         '&quot;actorId&quot;: &quot;contacts.Companies&quot;, &quot;rp&quot;: '
         'null, &quot;status&quot;: { &quot;record_id&quot;: 5 } })" '
         'style="text-decoration:none">Garage Mergelsberg (CEO)</a>, <a '
         'href="javascript:window.App.runAction({ '
         '&quot;action_full_name&quot;: &quot;contacts.Companies.detail&quot;, '
         '&quot;actorId&quot;: &quot;contacts.Companies&quot;, &quot;rp&quot;: '
         'null, &quot;status&quot;: { &quot;record_id&quot;: 1 } })" '
         'style="text-decoration:none">Rumma &amp; Ko OÜ (CEO)</a>, <a '
         'href="javascript:window.App.runAction({ '
         '&quot;action_full_name&quot;: '
         '&quot;countries.Countries.insert&quot;, &quot;actorId&quot;: '
         '&quot;contacts.RolesByPerson&quot;, &quot;onMain&quot;: false, '
         '&quot;rp&quot;: null, &quot;status&quot;: { &quot;base_params&quot;: '
         '{ &quot;mk&quot;: 69, &quot;mt&quot;: 10 }, &quot;data_record&quot;: '
         '{ &quot;data&quot;: { &quot;company&quot;: null, '
         '&quot;companyHidden&quot;: null, &quot;disabled_fields&quot;: {  }, '
         '&quot;type&quot;: null, &quot;typeHidden&quot;: null }, '
         '&quot;phantom&quot;: true, &quot;title&quot;: &quot;Insert a new '
         'Contact person&quot; }, &quot;record_id&quot;: null } })" '
         'title="Insert a new Contact person." class="pi pi-plus-circle"></a> '
         '<a href="javascript:window.App.runAction({ '
         '&quot;action_full_name&quot;: '
         '&quot;system.SiteConfigs.open_help&quot;, &quot;actorId&quot;: '
         '&quot;contacts.RolesByPerson&quot;, &quot;onMain&quot;: false, '
         '&quot;rp&quot;: null, &quot;status&quot;: { &quot;base_params&quot;: '
         '{ &quot;mk&quot;: 69, &quot;mt&quot;: 10 } } })" title="Open Help '
         'Window" style="text-decoration:none">?</a> </div>'}
