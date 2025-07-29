.. doctest docs/plugins/search.rst
.. _dg.plugins.search:

=============================================
``search`` : Add search functionality
=============================================

.. currentmodule:: lino.modlib.search

The :mod:`lino.modlib.search` plugin adds functionality for doing site-wide
searches across all tables of the application.

This plugin can optionally use an :term:`ElasticSearch` server to have faster
and intelligent search functionalities.

Table of contents:

.. contents::
   :depth: 1
   :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *

Configuration settings
======================

.. setting:: use_elasticsearch

  Whether to use :term:`ElasticSearch`.

  This is a :term:`site setting`.

.. setting:: search.elasticsearch_url

  The URL of the :term:`ElasticSearch` server.

  This is a :term:`plugin setting`.


The ``SiteSearch`` table
========================

.. class:: SiteSearch

    A virtual table that searches in all database tables.

    Open it using the menu command :menuselection:`Site --> Search` or the
    :term:`quick link` :guilabel:`[Search]`


>>> #ses.show_menu_path('search.SiteSearch')

The base version uses the default Django ORM filtering.

>>> ses = rt.login("robin")
>>> ses.show('search.SiteSearch', quick_search="foo", limit=5)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF +SKIP
- **[Comment #2](Detail)** :  Who| What| Done?
  ---|---|---
  Him| Bar|
  Her| Foo the Bar|  **x**
  Them| Floop the pig
  | x
<BLANKLINE>
<BLANKLINE>
- **[Comment #5](Detail)** : breaking **De :**
  [lino@foo.net](mailto:lino@foo.net) [[mailto:foo@bar.com](mailto:foo@bar.com)]
  **Envoyé :** mardi 18 octobre 2016 08:52
  **À :** [eexample@foo.com](mailto:Far@baz.net)
  **Objet :** [welcht] YOU modified FOO BAR Dear Aurélie , this is to notify /
  BAR BAR modified TODO: include a summary of the modifications. Any subsequent
  notifications about ...
<BLANKLINE>
<BLANKLINE>
- **[Comment #10](Detail)** :  Who| What| Done?
  ---|---|---
  Him| Bar|
  Her| Foo the Bar|  **x**
  Them| Floop the pig
  | x
<BLANKLINE>
<BLANKLINE>
- **[Comment #13](Detail)** : breaking **De :**
  [lino@foo.net](mailto:lino@foo.net) [[mailto:foo@bar.com](mailto:foo@bar.com)]
  **Envoyé :** mardi 18 octobre 2016 08:52
  **À :** [eexample@foo.com](mailto:Far@baz.net)
  **Objet :** [welcht] YOU modified FOO BAR Dear Aurélie , this is to notify /
  BAR BAR modified TODO: include a summary of the modifications. Any subsequent
  notifications about ...
<BLANKLINE>
<BLANKLINE>
- **[Comment #18](Detail)** :  Who| What| Done?
  ---|---|---
  Him| Bar|
  Her| Foo the Bar|  **x**
  Them| Floop the pig
  | x

If your search contains more than one word, it shows all rows containing both
words.

>>> ses.show('search.SiteSearch', quick_search="est land", limit=5)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF +SKIP
- **Estonia**
<BLANKLINE>
<BLANKLINE>
- **Flandre de l'Est**
<BLANKLINE>
<BLANKLINE>
- **Flandre de l'Ouest**
<BLANKLINE>
<BLANKLINE>
- **[Comment #3](Detail)** : Lorem ipsum **dolor sit amet** , consectetur
  adipiscing elit. Nunc cursus felis nisi, eu pellentesque lorem lobortis non.
  Aenean non sodales neque, vitae venenatis lectus. In eros dui, gravida et
  dolor at, pellentesque hendrerit magna. Quisque vel lectus dictum, rhoncus
  massa feugiat, condimentum sem. ...
<BLANKLINE>
<BLANKLINE>
- **[Comment #11](Detail)** : Lorem ipsum **dolor sit amet** , consectetur
  adipiscing elit. Nunc cursus felis nisi, eu pellentesque lorem lobortis non.
  Aenean non sodales neque, vitae venenatis lectus. In eros dui, gravida et
  dolor at, pellentesque hendrerit magna. Quisque vel lectus dictum, rhoncus
  massa feugiat, condimentum sem. ...


>>> ses.show('search.SiteSearch', quick_search="123", limit=5)  #doctest: +SKIP
===================================================== ========================
 Description                                           Matches
----------------------------------------------------- ------------------------
 *Arens Andreas* (Partner)                             phone:+32 87**123**456
 *Arens Annette* (Partner)                             phone:+32 87**123**457
 *Dobbelstein-Demeulenaere Dorothée* (Partner)         id:123
 *Mr Andreas Arens* (Person)                           phone:+32 87**123**456
 *Mrs Annette Arens* (Person)                          phone:+32 87**123**457
 *Mrs Dorothée Dobbelstein-Demeulenaere* (Person)      id:123
 *+32 87123456* (Contact detail)                       value:+32 87**123**456
 *+32 87123457* (Contact detail)                       value:+32 87**123**457
 *Diner (09.05.2015 13:30)* (Calendar entry)           id:123
 *SLS 9.2* (Movement)                                  id:123
 *DOBBELSTEIN-DEMEULENAERE Dorothée (123)* (Patient)   id:123
===================================================== ========================
<BLANKLINE>

Dobbelstein-Demeulenaere Dorothée (id 123) is Partner, Person and
Patient. All three instances are listed in the SiteSearch.


The ``ElasticSiteSearch`` table
===============================

.. class:: ElasticSiteSearch

    A virtual table used to search on this Lino site using :term:`ElasticSearch`.

    It exists only when :setting:`settings.SITE.use_elasticsearch` is `True`.


Install an ElasticSearch server
===============================

This section explains how an :term:`application developer` can install
:term:`ElasticSearch` on their machine.

General instructions are `here
<https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html>`__.
For our demonstration purposes we will install ElasticSearch in a docker
container using the instructions provided `here
<https://www.elastic.co/guide/en/elasticsearch/reference/7.15/docker.html>`__.

Pull the docker image of ElasticSearch::

  $ sudo docker pull docker.elastic.co/elasticsearch/elasticsearch:7.15.0

Run an ElasticSearch instance on a docker container::

  $ sudo docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.15.0

PS: Always try to use the latest ElasticSearch version and replace 7.15.0 with
current x.xx.x version.

To run a docker container instance with minimal security enabled, use the
following command::

  $ sudo docker run -p 127.0.0.1:9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e "xpack.security.enabled=true" -e ELASTIC_PASSWORD="elastic" docker.elastic.co/elasticsearch/elasticsearch:7.15.0

Here we replaced `-p 9200:9200` with `-p 127.0.0.1:9200:9200` so that port 9200
is only accessible from the localhost and not open to the external network. The
option `-e "xpack.security.enabled=true"` enables the security feature of the
docker container and `-e ELASTIC_PASSWORD="elastic"` set the password to
`elastic` for the default user: `elastic`.

Source: https://www.elastic.co/guide/en/elasticsearch/reference/7.15/security-minimal-setup.html


Preparing Indexes
=================

:mod:`lino.modlib.search` provides a management command
:cmd:`python manage.py createindexes` (recommended to run before publishing a
site) that has the following grounds on a lino site:

The following method :meth:`search.utils.ESResolver.resolve_es_indexes` gathers
all the indexes, defined in the model definitions as
:attr:`lino.core.model.Model.ES_indexes`, into a dictionary for further uses in
the app `elasticsearch_django`'s settings:

>>> from lino.modlib.search.utils import ESResolver
>>> indexes, _ = ESResolver.resolve_es_indexes()
>>> indexes
{'comment': {'models': [<class 'lino.modlib.comments.models.Comment'>]}, 'ticket': {'models': [<class 'lino_noi.lib.tickets.models.Ticket'>]}}
>>> ESResolver.read_indexes()
{'comment': {'models': ['comments.Comment']}, 'ticket': {'models': ['tickets.Ticket']}}

URL to ElasticSearch instance:

>>> es_url = dd.plugins.search.ES_url
>>> print(es_url)
https://elastic:mMh6KlFP0UAooywwsWPLJ3ae@lino.es.us-central1.gcp.cloud.es.io:9243

.. http://elastic:elastic@localhost:9200

Create ElasticSearch index mapping files:

>>> # ESResolver.create_index_mapping_files()
>>> mappings_dir = dd.plugins.search.mappings_dir
>>> print(mappings_dir) # doctest: +ELLIPSIS
/.../lino/modlib/search/search/mappings

Content of the mapping files:

>>> import json
>>> def get_mappings_from_files(mappings_dir):
...     maps = dict()
...     for index in ESResolver.get_indexes():
...         filename = mappings_dir / (index + '.json')
...         with open(filename, 'r') as f:
...             obj = json.load(f)
...         maps[index] = obj
...     print(maps)
>>> get_mappings_from_files(mappings_dir)
{'comment': {'mappings': {'properties': {'body': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}, 'analyzer': 'autocomplete', 'search_analyzer': 'autocomplete_search'}, 'body_full_preview': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}, 'analyzer': 'autocomplete', 'search_analyzer': 'autocomplete_search'}, 'body_short_preview': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}, 'analyzer': 'autocomplete', 'search_analyzer': 'autocomplete_search'}, 'model': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}, 'analyzer': 'autocomplete', 'search_analyzer': 'autocomplete_search'}, 'modified': {'type': 'date'}, 'owner_id': {'type': 'long'}, 'owner_type': {'type': 'long'}, 'private': {'type': 'boolean'}, 'user': {'type': 'long'}}}}, 'ticket': {'mappings': {'properties': {'closed': {'type': 'boolean'}, 'description': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}, 'analyzer': 'autocomplete', 'search_analyzer': 'autocomplete_search'}, 'end_user': {'type': 'long'}, 'feedback': {'type': 'boolean'}, 'model': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}, 'analyzer': 'autocomplete', 'search_analyzer': 'autocomplete_search'}, 'priority': {'type': 'long'}, 'private': {'type': 'boolean'}, 'site': {'type': 'long'}, 'standby': {'type': 'boolean'}, 'state': {'properties': {'text': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}}, 'value': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}}}}, 'summary': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}, 'analyzer': 'autocomplete', 'search_analyzer': 'autocomplete_search'}, 'ticket_type': {'type': 'long'}, 'upgrade_notes': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}, 'analyzer': 'autocomplete', 'search_analyzer': 'autocomplete_search'}, 'user': {'type': 'long'}, 'waiting_for': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}, 'analyzer': 'autocomplete', 'search_analyzer': 'autocomplete_search'}}}}}


.. Managing Search
.. ===============

.. >>> from elasticsearch_django.models import execute_search
.. >>> from elasticsearch_django.settings import get_client
.. >>> client = get_client()
.. >>> from elasticsearch_dsl import Search
.. >>> from elasticsearch_dsl.query import MultiMatch
.. >>> query = MultiMatch(query='foo')
.. >>> search = Search(using=client)
.. >>> s = search.query(query)
.. >>> s.count()
.. 98

.. Pagination:

.. >>> page_size = settings.SEARCH_SETTINGS['settings']['page_size']
.. >>> def get_range(page):
.. ...     start = (page - 1) * page_size
.. ...     end = start + page_size
.. ...     return start, end
.. >>> page = 1
.. >>> start, end = get_range(page)

.. >>> s = s[start:end]
.. >>> sq = execute_search(s, save=False)
.. >>> resp = sq.response
.. >>> len(resp.hits)
.. 15

.. >>> page = 2
.. >>> start, end = get_range(page)
.. >>> s = s[start:end]
.. >>> sq = execute_search(s, save=False)

.. >>> for hit in sq.response.hits:
.. ...     obj = eval(hit['model']).objects.get(pk=hit['id'])
.. ...     print(obj)
.. Comment #122
.. Comment #130
.. Comment #138
.. Comment #146
.. Comment #154
.. Comment #162
.. Comment #5
.. Comment #13
.. Comment #21
.. Comment #29
.. Comment #37
.. Comment #45
.. Comment #53
.. Comment #61
.. Comment #69


Don't read on
=============

The remaining part of this page is just technical stuff.

>>> from lino.core.utils import get_models
>>> ar = rt.login()
>>> user_type = ar.get_user().user_type
>>> count = 0
>>> for model in get_models():
...     t = model.get_default_table()
...     if t and not t.get_view_permission(user_type):
...         print("Not visible: {}".format(t))
...     count += 1
>>> print(f"Verified {count} models")
Verified 112 models

>>> rt.models.contacts.Person.quick_search_fields_digit
(<django.db.models.fields.BigAutoField: id>,)

The following request caused problems before 20180920 (:ticket:`2544`
SiteSearch fails when it finds a name containing "&")

>>> ses.show('search.SiteSearch', quick_search="rumma & ko")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
- [Partner #1](…) : [Rumma & Ko OÜ](…) (Uus tn 1, Vigala vald, 78003 Rapla
  maakond, Estonia)
<BLANKLINE>
...

AnonymousUser does NOT have row permission on Partner

>>> rt.show('search.SiteSearch', quick_search="rumma")
<BLANKLINE>

Using Solr as search backend
============================

Lino utilizes django-haystack app along with apache Solr backend server to
provide intelligent search functionalities.

Installing Solr and dependencies
================================

The following command will set the :term:`application developer` for a
compatible Solr - django-haystack environment.

Install pysolr::

  $ pip install pysolr

Install django-haystack::

  $ pip install django-haystack

Install java-1.8 (Linux):

  jre1.8 is available for download `here <https://www.java.com/en/download/linux_manual.jsp>`__
  however, to make it more command line friendly, lino team made downloading
  jre1.8 available from another source for Linux (x64) based systems.
  Follow the commands below::

    $ cd ~
    $ curl -o jre-8u311-linux-x64.tar.gz "link"
    $ tar -xvf jre-8u311-linux-x64.tar.gz

  Change JAVA_HOME to our downloaded jre1.8::

    $ export JAVA_HOME="$HOME/jre1.8.0_311"

Install solr-8.11.0::

  $ cd ~
  $ curl -o solr-8.11.0.zip "https://dlcdn.apache.org/lucene/solr/8.11.0/solr-8.11.0.zip"
  $ unzip solr-8.11.0.zip

Add solr-6.6.6 to unix PATH::

  $ export PATH="$HOME/solr-8.11.0/bin:$PATH"

Run solr and create a collection named *lino*::

  $ solr start
  $ solr create -c lino -n basic_config

Now we are ready to use solr with a lino project. Go to the root directory of
you lino project (where :xfile:`manage.py` is located) and run the following
command::

  $ python manage.py build_solr_schema_v2 --configure-directory="$HOME/solr-8.11.0/server/lino/conf" --reload-core=lino

The last command will build solr schema and reload the solr core name *lino*.
And now your solr core/collection *lino* is ready for indexing and searching
search documents.
