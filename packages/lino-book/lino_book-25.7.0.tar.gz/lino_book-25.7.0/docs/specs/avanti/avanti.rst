.. doctest docs/specs/avanti/avanti.rst
.. _avanti.specs.avanti:

=================================
Clients in Lino Avanti
=================================

.. currentmodule:: lino_avanti.lib.avanti

This document describes the :mod:`lino_avanti.lib.avanti` plugin.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *


Overview
========

A **client** is a person using our services.


The legacy file number
======================

Dossiernummern:

- Wenn du "ip6" eintippst, sucht Lino die letzte Dossiernummer, die mit "IP 6"
  beginnt und zählt +1 hinzu. Also wenn der letzte bestehende Klient "IP 6923"
  hat, macht Lino aus "ip6" eine "IP 6924".

- Du kannst auch im Schnellsuche-Feld "ip 6900" eintippen, um nach Dossiernummer zu suchen.

- Wenn du "ip 1234" eintippst (also die Dossiernummer selber als vierstellige
  Zahl angibst), dann lässt Lino diese Nummer stehen.

- Ob du "ip" oder "IP" eintippst, ist egal, Lino macht daraus immer "IP".

- Auch das Leerzeichen kannst du beim Eintippen sparen, das setzt Lino
  automatisch rein.

- Wenn die Dossiernummer nicht mit "ip" beginnt, lässt Lino sie unverändert


>>> other = avanti.Client.objects.get(pk=17)
>>> other2 = avanti.Client.objects.get(pk=18)
>>> def update_other(ref, ref2):
...     other.ref = ref
...     other.full_clean()
...     other.save()
...     other2.ref = ref2
...     other2.full_clean()
...     other2.save()

>>> update_other(None, None) # tidy up from previous test run

>>> def test(ref):
...     obj = avanti.Client(ref=ref, name="x")
...     obj.full_clean()
...     print(obj.ref)

>>> test("ip")
IP 0001

>>> test("ip 1")
IP 1001

>>> update_other("IP 4010", "IP 5123")

>>> test("ip 4")
IP 4011

>>> test("ip")
IP 5124

>>> update_other("IP 6999", "IP 7000")
>>> test("ip6")
IP 61000

>>> update_other("IP 60999", "IP 61000")
>>> test("ip6")
IP 61001

Damit Lino die Referenzen automatisch verteilen kann, müssen alle bestehenden
Dossiernummern die gleiche Länge haben. Ansonsten kann Lino durcheinander
kommen. Zum Beispiel:

>>> update_other("IP 6999", "IP 61000")
>>> test("ip6")
Traceback (most recent call last):
...
django.core.exceptions.ValidationError: {'ref': ['Client with this Legacy file number already exists.']}

>>> update_other(None, None) # tidy up for the following tests


Clients
=======

.. class:: Client(lino.core.model.Model)

    .. attribute:: translator_type

        Which type of translator is needed with this client.

        See also :class:`TranslatorTypes`

    .. attribute:: professional_state

        The professional situation of this client.

        See also :class:`ProfessionalStates`

    .. attribute:: overview

        A panel with general information about this client.

    .. attribute:: client_state

        The state of this client record.

        This is a pointer to :class:`ClientStates` and can have the following
        values:

        >>> rt.show('clients.ClientStates')
        ======= ========== ============ =============
         value   name       text         Button text
        ------- ---------- ------------ -------------
         05      incoming   Incoming
         07      informed   Informed
         10      newcomer   Newcomer
         15      equal      Equal
         20      coached    Registered
         25      inactive   Inactive
         30      former     Ended
         40      refused    Abandoned
        ======= ========== ============ =============
        <BLANKLINE>


    .. attribute:: unemployed_since

       The date when this client got unemployed and stopped to have a
       regular work.

    .. attribute:: seeking_since

       The date when this client registered as unemployed and started
       to look for a new job.

    .. attribute:: work_permit_suspended_until

    .. attribute:: city

       The place (village or municipality) where this client lives.

       See :attr:`lino_xl.lib.contacts.Partner.city`.

    .. attribute:: municipality

       The *municipality* where this client lives. This is basically
       equal to :attr:`city`, except when :attr:`city` is a *village*
       and has a parent which is a *municipality* (which causes that
       place to be returned).


.. class:: ClientDetail

.. class:: Clients

    Base class for most tables of clients.

    .. attribute:: client_state

        If not empty, show only Clients whose `client_state` equals
        the specified value.


.. class:: AllClients(Clients)

   This table is visible for Explorer who can also export it.

   This table shows only a very limited set of fields because e.g. an auditor
   may not see all data for privacy reasons. For example the names are hidden.
   OTOH it includes the :attr:`municipality
   <lino_avanti.lib.avanti.Client.municipality>` virtual field.


>>> show_columns(avanti.AllClients, all=True)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
- State (client_state) : The state of this client record.
- Starting reason (starting_reason) :
- Ending reason (ending_reason) :
- Locality (city) : The locality, i.e. usually a village, city or town.
- Municipality (municipality) : The municipality where this client lives. This is basically
  equal to city, except when city is a village
  and has a parent which is a municipality (which causes that
  place to be returned).
- Country (country) :
- Zip code (zip_code) :
- Nationality (nationality) : The nationality. This is a pointer to
  countries.Country which should
  contain also entries for refugee statuses.
- Gender (gender) : The sex of this person (male or female).
- Birth country (birth_country) :
- Lives in Belgium since (in_belgium_since) : Uncomplete dates are allowed, e.g.
  "00.00.1980" means "some day in 1980",
  "00.07.1980" means "in July 1980"
  or "23.07.0000" means "on a 23th of July".
- Needs work permit (needs_work_permit) :
- Translator type (translator_type) : Which type of translator is needed with this client.
- Mother tongues (mother_tongues) :
- None (cef_level_de) :
- None (cef_level_fr) :
- None (cef_level_en) :
- Primary coach (user) : The author of this database object.
- Recurrency policy (event_policy) :

>>> rt.show(avanti.AllClients, limit=5)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
============ ================= =============== ============ ============== ========= ========== ============= ========== ======== =============== ======================== =================== ================= ================ =================== =============== =============== ================= =================== ============== ================
 State        Starting reason   Ending reason   Locality     Municipality   Country   Zip code   Nationality   Age        Gender   Birth country   Lives in Belgium since   Needs work permit   Translator type   Mother tongues   cef_level_de        cef_level_fr    cef_level_en    Primary coach     Recurrency policy   Erstgespräch   Bilanzgespräch
------------ ----------------- --------------- ------------ -------------- --------- ---------- ------------- ---------- -------- --------------- ------------------------ ------------------- ----------------- ---------------- ------------------- --------------- --------------- ----------------- ------------------- -------------- ----------------
 Registered                                     4700 Eupen   4700 Eupen     Belgium   4700                     16 years   Male                                              No                  SETIS             Dutch            Not specified       Not specified   Not specified   nathalie          Every month         30/07/2016
 Registered                                     4700 Eupen   4700 Eupen     Belgium   4700                     20 years   Female                                            No                  Other             English          Not specified       Not specified   Not specified   Romain Raffault   Every 2 weeks
 Registered                                     4700 Eupen   4700 Eupen     Belgium   4700                     22 years   Male                                              No                  Other             French           A1+ (Certificate)   Not specified   Not specified   Rolf Rompen       Other
 Registered                                     4700 Eupen   4700 Eupen     Belgium   4700                     24 years   Male                                              No                  Other             English          Not specified       Not specified   Not specified   Robin Rood        Every 2 months
 Registered                                     4700 Eupen   4700 Eupen     Belgium   4700                     26 years   Male                                              No                  SETIS             French           Not specified       Not specified   Not specified   nathalie          Every 3 months
============ ================= =============== ============ ============== ========= ========== ============= ========== ======== =============== ======================== =================== ================= ================ =================== =============== =============== ================= =================== ============== ================
<BLANKLINE>


.. class:: MyClients(Clients)

    Shows all clients having me as primary coach. Shows all client states.

    Since 20250319 shows only registered clients.

    >>> rt.login('robin').show('avanti.MyClients')
    ... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
    ============================== ============ =============== ======== =========================== ========== ================ ======= ==== ====================
     Name                           State        National ID     Mobile   Address                     Age        e-mail address   Phone   ID   Legacy file number
    ------------------------------ ------------ --------------- -------- --------------------------- ---------- ---------------- ------- ---- --------------------
     ABDALLAH Aáish (28/robin)      Registered   920417 001-91            Bellmerin, 4700 Eupen       24 years                            28
     ABDO Aásim (39/robin)          Registered   831201 001-50            Gülcherstraße, 4700 Eupen   33 years                            39
     ASTAFUROV Agáfiiá (76/robin)   Registered   820120 002-60            Aachen, Germany             35 years                            76
     CONTEE Chike (32/robin)        Registered   870822 001-58            Edelstraße, 4700 Eupen      29 years                            32
     DIOP Ashánti (43/robin)        Registered   810214 002-32            Habsburgerweg, 4700 Eupen   36 years                            43
     JALLOH Diállo (59/robin)       Registered   740810 001-48            4730 Raeren                 42 years                            59
    ============================== ============ =============== ======== =========================== ========== ================ ======= ==== ====================
    <BLANKLINE>


.. class:: ClientsByNationality(Clients)


.. class:: Residence(lino.core.model.Model)


.. class:: EndingReason(lino.core.model.Model)

>>> rt.show('avanti.EndingReasons')
==== ======================== ========================== ========================
 ID   Designation              Designation (de)           Designation (fr)
---- ------------------------ -------------------------- ------------------------
 1    Successfully ended       Erfolgreich beendet        Successfully ended
 2    Health problems          Gesundheitsprobleme        Health problems
 3    Familiar reasons         Familiäre Gründe           Familiar reasons
 4    Missing motivation       Fehlende Motivation        Missing motivation
 5    Return to home country   Rückkehr ins Geburtsland   Return to home country
 9    Other                    Sonstige                   Autre
==== ======================== ========================== ========================
<BLANKLINE>

.. class:: Category(BabelDesignated)

>>> rt.show('avanti.Categories')
==== =============================== =============================== ===============================
 ID   Designation                     Designation (de)                Designation (fr)
---- ------------------------------- ------------------------------- -------------------------------
 1    Language course                 Sprachkurs                      Language course
 2    Integration course              Integrationskurs                Integration course
 3    Language & integration course   Language & integration course   Language & integration course
 4    External course                 External course                 External course
 5    Justified interruption          Begründete Unterbrechung        Justified interruption
 6    Successfully terminated         Erfolgreich beendet             Successfully terminated
==== =============================== =============================== ===============================
<BLANKLINE>


.. class:: TranslatorTypes

    List of choices for the :attr:`Client.translator_type` field of a
    client.

    >>> rt.show(rt.models.avanti.TranslatorTypes, language="de")
    ====== ====== ==========
     Wert   name   Text
    ------ ------ ----------
     10            SETIS
     20            Sonstige
     30            Privat
    ====== ====== ==========
    <BLANKLINE>


.. class:: ProfessionalStates

    List of choices for the :attr:`Client.professional_state` field of
    a client.

    >>> rt.show(rt.models.avanti.ProfessionalStates, language="de")
    ... #doctest: +NORMALIZE_WHITESPACE -REPORT_UDIFF
    ====== ====== ================================
     Wert   name   Text
    ------ ------ --------------------------------
     100           Student
     200           Arbeitslos
     300           Eingeschrieben beim Arbeitsamt
     400           Angestellt
     500           Selbstständig
     600           Pensioniert
     700           Arbeitsunfähig
    ====== ====== ================================
    <BLANKLINE>



>>> rt.show(checkdata.Checkers, language="en")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
================================= =============================================
 value                             text
--------------------------------- ---------------------------------------------
 beid.SSINChecker                  Check for invalid SSINs
 cal.ConflictingEventsChecker      Check for conflicting calendar entries
 cal.EventGuestChecker             Entries without participants
 cal.LongEntryChecker              Too long-lasting calendar entries
 cal.ObsoleteEventTypeChecker      Obsolete generated calendar entries
 comments.CommentChecker           Check for missing owner in reply to comment
 countries.PlaceChecker            Check data of geographical places
 dupable.DupableChecker            Check for missing phonetic words
 dupable.SimilarObjectsChecker     Check for similar objects
 memo.PreviewableChecker           Check for previewables needing update
 printing.CachedPrintableChecker   Check for missing target files
 system.BleachChecker              Find unbleached html content
 uploads.UploadChecker             Check metadata of upload files
 uploads.UploadsFolderChecker      Find orphaned files in uploads folder
================================= =============================================
<BLANKLINE>


Career
======

Language knowledges
===================

Avanti adds an entry date to the language knowledge table of a client.
There can be multiple entries per language and client.
Because we want to report whether knowledge changed after attending a course.

Some example cases:

>>> client = rt.models.avanti.Client.objects.get(pk=21)
>>> rt.show('cv.LanguageKnowledgesByPerson', client, nosummary=True)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
========== =============== ============ ============ =========== ============= ============
 Language   Mother tongue   Spoken       Written      CEF level   Certificate   Entry date
---------- --------------- ------------ ------------ ----------- ------------- ------------
 Dutch      No              a bit        moderate     A2+         Yes           05/02/2017
 Dutch      No              moderate     quite well   A2          Yes           12/01/2016
 German     No              quite well   very well    A1+         Yes           12/01/2016
 French     Yes                                                   No            12/01/2016
========== =============== ============ ============ =========== ============= ============
<BLANKLINE>


>>> client = rt.models.avanti.Client.objects.get(pk=22)
>>> rt.show('cv.LanguageKnowledgesByPerson', client, nosummary=True)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
========== =============== ======== ========= =========== ============= ============
 Language   Mother tongue   Spoken   Written   CEF level   Certificate   Entry date
---------- --------------- -------- --------- ----------- ------------- ------------
 Estonian   Yes                                            No            12/01/2016
========== =============== ======== ========= =========== ============= ============
<BLANKLINE>


>>> client = rt.models.avanti.Client.objects.get(pk=23)
>>> rt.show('cv.LanguageKnowledgesByPerson', client, nosummary=True, language="de")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
============= =============== ============== ============== =============== ============ =================
 Sprache       Muttersprache   Wort           Schrift        CEF-Kategorie   Zertifikat   Erfassungsdatum
------------- --------------- -------------- -------------- --------------- ------------ -----------------
 Deutsch       Nein            gar nicht      ein bisschen   A1              Ja           05.02.17
 Deutsch       Nein            ein bisschen   mittelmäßig    A0              Ja           12.01.16
 Französisch   Ja                                                            Nein         12.01.16
============= =============== ============== ============== =============== ============ =================
<BLANKLINE>

The end user usually sees the summary of language knowledges , which shows the
CEF level of the languages defined in :attr:`lino.core.site.Site.languages`,
and only the most recent CEF level.  For above client the CEF level for German
is A1 (not A0):

>>> rt.show('cv.LanguageKnowledgesByPerson', client, language="de")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
en: Ohne Angabe
de: A1 (Zertifikat)
fr: Ohne Angabe
Muttersprachen: Französisch



Creating a new client
=====================


>>> ses = rt.login("romain")
>>> url = '/api/avanti/MyClients/-99999?an=insert&fmt=json'
>>> test_client.force_login(ses.user)
>>> res = test_client.get(url)
>>> res.status_code
200
>>> d = AttrDict(json.loads(res.content))
>>> sorted(d.keys())
... #doctest: +NORMALIZE_WHITESPACE +IGNORE_EXCEPTION_DETAIL +ELLIPSIS
['data', 'phantom', 'title']
>>> d.phantom
True
>>> print(d.title)
Insérer Bénéficiaire


The dialog window has 6 data fields:

>>> sorted(d.data.keys())  #doctest: +NORMALIZE_WHITESPACE
['disabled_fields', 'email', 'first_name', 'gender', 'genderHidden', 'last_name']


>>> fld = avanti.Clients.parameters['observed_event']
>>> rt.show(fld.choicelist, language="en")
No data to display


Miscellaneous
=============

Until 20200818 the help_text of the municipality field wasn't set at all, and
the help text of Partner.city talked about a client because it had been
overwritten by the help text of :attr:`lino_avanti.lib.contacts.Person.city`.

On 20210709 (after moving help texts to separate plugin :mod:`lino.modlib.help`)
there was another subtle problem here.

Compare (a) the specs (i.e. the target of the links) and (b) the help texts of
the following fields:

- :attr:`lino_avanti.lib.avanti.Client.city`
- :attr:`lino_avanti.lib.avanti.Client.municipality`
- :attr:`lino_avanti.lib.contacts.Person.city`
- :attr:`lino_avanti.lib.contacts.Person.municipality`

The :attr:`lino_xl.lib.countries.CountryCity.municipality` field is defined on
the :class:`lino_xl.lib.countries.CountryCity` model mixin. It is documented on
:ref:`dg.plugins.countries`, which causes the help_text_extractor to extract its
help_text::

  The locality, i.e. usually a village, city or town.

This :attr:`help_text` is inherited by all models that use this model mixin:
Person, Partner, Company, Client. But Client overrides it again to be more
specific.

>>> print(contacts.Person._meta.get_field('municipality').help_text)
The municipality, i.e. either the city or a parent of it.

>>> print(contacts.Person._meta.get_field('city').help_text)
The locality, i.e. usually a village, city or town.

>>> print(contacts.Person._meta.get_field('city').help_text)
The locality, i.e. usually a village, city or town.

>>> print(avanti.Client._meta.get_field('municipality').help_text)
The municipality where this client lives. This is basically equal to city, except when city is a village and has a parent which is a municipality (which causes that place to be returned).

Don't read
==========

>>> obj = avanti.Client.objects.get(pk=68)
>>> rt.login("robin").show("changes.ChangesByMaster", obj)
Aucun enregistrement

The following (specifying a wrong mt) caused a server traceback until 20230620

>>> url = "/api/changes/ChangesByMaster?dm=grid&fmt=json&limit=15&mk=68&mt=75&start=0&ul=en&wt=d"
>>> res = test_client.get(url)
>>> d = json.loads(res.content.decode())
>>> print(d['title'])
Changes of MissingRow(Line matching query does not exist. (pk=68))

.. _ticket5751:

#5751 ObjectDoesNotExist: Invalid primary key 4968 for avanti.Clients
=====================================================================

Before 20240910, the following request was returning ``{'data': 'Oops, Invalid
primary key 16 for avanti.Clients'}`` because client 16 has client_state
"former" and therefore is not visible in the default :class:`avanti.Clients`
table. This was :ticket:`5751`. Then, until 20241004, Lino didn't check at all
whether the table (avanti.Clients in this case) gives access to a particular
row. This was :ticket:`5759` (Anonymous can GET private comments).

Since 20250319 avanti.Clients shows all clients (not only coached ones) and
MyClients shows only coached ones.

>>> ses = rt.login("robin")
>>> test_client.force_login(ses.user)
>>> pk = 16
>>> cli = avanti.Client.objects.get(pk=pk)
>>> cli.client_state
<clients.ClientStates.former:30>
>>> url = f"/api/avanti/MyClients/{pk}?fmt=json"
>>> res = test_client.get(url)
>>> d  = json.loads(res.content.decode())
>>> d['message']
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
'Row 16 is not visible here.<br>But you can see it in <a
href="javascript:window.App.runAction({ &quot;action_full_name&quot;: &quot;avanti.Clients.detail&quot;,
&quot;actorId&quot;: &quot;avanti.Clients&quot;, &quot;rp&quot;:
null, &quot;status&quot;: { &quot;base_params&quot;: {  },
&quot;param_values&quot;: { &quot;aged_from&quot;: null, &quot;aged_to&quot;:
null, &quot;client_contact_company&quot;: null,
&quot;client_contact_companyHidden&quot;: null, &quot;client_state&quot;: null,
&quot;client_stateHidden&quot;: null, &quot;course&quot;: null,
&quot;courseHidden&quot;: null, &quot;end_date&quot;: null,
&quot;enrolment_state&quot;: null, &quot;enrolment_stateHidden&quot;: null,
&quot;gender&quot;: null, &quot;genderHidden&quot;: null,
&quot;nationality&quot;: null, &quot;nationalityHidden&quot;: null,
&quot;start_date&quot;: null, &quot;user&quot;: null, &quot;userHidden&quot;:
null }, &quot;record_id&quot;: 16 } })"
style="text-decoration:none">Clients</a>.'

Indeed client 16 does not exist in the avanti.MyClients table when using its
default parameters (i.e. show only coached clients). That's why also requests
for a single database row must provide parameter values. Another reason for the
parameter values is navigation: Lino does not only return data of the row but
also navinfo with pointers to next and previous rows.

>>> url += "&fmt=json&pv=&pv=&pv=&pv=&pv=&pv=&pv=&pv=&pv=&pv=&pv="
>>> res = test_client.get(url)
>>> d = json.loads(res.content.decode())
>>> d['data']['first_name']
'Aábid'
>>> d['data']['cal.GuestsByPartner']  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
'<div><table cellspacing="3px" bgcolor="#eeeeee" width="100%"
name="cal.GuestsByPartner.grid">... title="Insert a new Presence." class="pi
pi-plus-circle" /></p></div>'

The same is true for delayed values:

>>> url = f"/values/avanti/MyClients/{pk}/cal.GuestsByPartner"
>>> res = test_client.get(url)  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
No row 16 in ActionRequest for ShowTable on avanti.MyClients
Traceback (most recent call last):
...
lino_avanti.lib.avanti.models.Client.DoesNotExist: No row 16 in ActionRequest for ShowTable on avanti.MyClients
Bad Request: /values/avanti/MyClients/16/cal.GuestsByPartner


>>> url += "?pv=&pv=&pv=&pv=&pv=&pv=&pv=&pv=&pv=&pv=&pv="
>>> res = test_client.get(url)
>>> d = json.loads(res.content.decode())
>>> d  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
{'data': '<div class="htmlText"><ul><li>February 2017: ... <a href="..."
title="Insert a new Presence." class="pi pi-plus-circle"></a></p></div>'}
