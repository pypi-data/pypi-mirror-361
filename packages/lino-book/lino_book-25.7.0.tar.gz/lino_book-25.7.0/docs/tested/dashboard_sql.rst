.. doctest docs/tested/dashboard_sql.rst
.. include:: /../docs/shared/include/defs.rst
.. _book.tested.dashboard_sql:

=======================================
Exploring SQL activity of new dashboard
=======================================

See :blogref:`20210615`.

>>> from lino_book.projects.noi1r.startup import *

During startup there were two SQL queries:

>>> show_sql_queries()  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
SELECT excerpts_excerpttype.id, excerpts_excerpttype.name, excerpts_excerpttype.build_method, excerpts_excerpttype.template, excerpts_excerpttype.attach_to_email, excerpts_excerpttype.email_template, excerpts_excerpttype.certifying, excerpts_excerpttype.remark, excerpts_excerpttype.body_template, excerpts_excerpttype.content_type_id, excerpts_excerpttype.primary, excerpts_excerpttype.backward_compat, excerpts_excerpttype.print_recipient, excerpts_excerpttype.print_directly, excerpts_excerpttype.shortcut, excerpts_excerpttype.name_de, excerpts_excerpttype.name_fr FROM excerpts_excerpttype ORDER BY excerpts_excerpttype.id ASC
SELECT django_content_type.id, django_content_type.app_label, django_content_type.model FROM django_content_type WHERE django_content_type.id = ...
SELECT django_content_type.id, django_content_type.app_label, django_content_type.model FROM django_content_type WHERE django_content_type.id = ...



Now we do a single request to :class:`Tickets`. And look at all the
SQL that poor Django must do in order to return a single row.

>>> reset_sql_queries()
>>> ses = rt.login('robin')
>>> test_client.force_login(ses.get_user())
>>> r = test_client.get('/')
>>> show_sql_summary()
=================== =========== =======
 table               stmt_type   count
------------------- ----------- -------
                     COMMIT      1
                     UNKNOWN     1
                     UPDATE      1
 django_session      SELECT      1
 system_siteconfig   SELECT      1
 users_user          SELECT      1
=================== =========== =======
<BLANKLINE>

>>> reset_sql_queries()


>>> show_sql_queries()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF +SKIP

..

  >> r = test_client.get('/api/system/Dashboard')
  >> print(r)


  >> r = demo_get('robin','api/tickets/Tickets', fmt='json', limit=1)
  >> res = test_client.get('/api/tickets/Tickets?fmt=json&limit=1')
  >> res = check_json_result(res)
  >> rmu(res.keys())
  ['count', 'rows', 'no_data_text', 'success', 'title', 'param_values']
  >> len(res['rows'])
  1
