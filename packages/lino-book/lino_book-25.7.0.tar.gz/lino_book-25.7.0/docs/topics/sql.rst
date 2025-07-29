.. doctest docs/topics/sql.rst
.. _dg.topics.sql:

==================
Tuning SQL queries
==================


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.min9.settings')
>>> from lino.api.doctest import *


>>> show_sql_summary() #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
====================== =========== =======
 table                  stmt_type   count
---------------------- ----------- -------
 django_content_type    SELECT      8
 excerpts_excerpttype   SELECT      1
====================== =========== =======
<BLANKLINE>


Now we do a single request to :term:`partners <partner>`. And look at all the
SQL that poor Django must do in order to return a single row.

>>> reset_sql_queries()
>>> lst = [o.address for o in contacts.Person.objects.all()]
>>> print(len(lst))
97
>>> show_sql_summary() #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
=================== =========== =======
 table               stmt_type   count
------------------- ----------- -------
 contacts_person     SELECT      1
 countries_country   SELECT      69
 countries_place     SELECT      69
=================== =========== =======
<BLANKLINE>

>>> reset_sql_queries()

When we loop using the data table,  which overrides `get_request_queryset` to add
`select_related`, then we save the repeated lookups to place and country::

    @classmethod
    def get_request_queryset(cls, ar, **filter):
        qs = super().get_request_queryset(ar, **filter)
        return qs.select_related('country', 'city')

>>> ar = rt.login("robin")
>>> lst = [o.address for o in ar.spawn(contacts.Persons)]
>>> print(len(lst))
97
>>> show_sql_summary() #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
=================== =========== =======
 table               stmt_type   count
------------------- ----------- -------
 contacts_person     SELECT      1
 system_siteconfig   SELECT      1
 users_user          SELECT      1
=================== =========== =======
<BLANKLINE>
