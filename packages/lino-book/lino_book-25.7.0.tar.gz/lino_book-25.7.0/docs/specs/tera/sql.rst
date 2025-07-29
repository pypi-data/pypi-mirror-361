.. doctest docs/specs/tera/sql.rst
.. _specs.tera.sql:

===================================
Exploring SQL activity in Lino Tera
===================================

This document explores some SQL requests in Lino Tera.
It is also a demo of
the :func:`show_sql_queries <lino.api.doctest.show_sql_queries>`
function.

We use the :mod:`lino_book.projects.tera1` demo database.

>>> from lino import startup
>>> startup('lino_book.projects.tera1.settings')
>>> from lino.api.doctest import *

Startup
=======

During startup there are a few SQL queries caused by
:func:`lino_xl.lib.excerpts.models.set_excerpts_actions`, which is called during
startup as a :data:`lino.core.signals.pre_analyze` handler:

>>> show_sql_queries()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
SELECT excerpts_excerpttype.id, excerpts_excerpttype.name, excerpts_excerpttype.build_method, excerpts_excerpttype.template, excerpts_excerpttype.attach_to_email, excerpts_excerpttype.email_template, excerpts_excerpttype.certifying, excerpts_excerpttype.remark, excerpts_excerpttype.body_template, excerpts_excerpttype.content_type_id, excerpts_excerpttype.primary, excerpts_excerpttype.backward_compat, excerpts_excerpttype.print_recipient, excerpts_excerpttype.print_directly, excerpts_excerpttype.shortcut, excerpts_excerpttype.name_de, excerpts_excerpttype.name_fr FROM excerpts_excerpttype ORDER BY excerpts_excerpttype.id ASC
SELECT django_content_type.id, django_content_type.app_label, django_content_type.model FROM django_content_type WHERE django_content_type.id = ... LIMIT 21
SELECT django_content_type.id, django_content_type.app_label, django_content_type.model FROM django_content_type WHERE django_content_type.id = ... LIMIT 21
SELECT django_content_type.id, django_content_type.app_label, django_content_type.model FROM django_content_type WHERE django_content_type.id = ... LIMIT 21
SELECT django_content_type.id, django_content_type.app_label, django_content_type.model FROM django_content_type WHERE django_content_type.id = ... LIMIT 21
SELECT django_content_type.id, django_content_type.app_label, django_content_type.model FROM django_content_type WHERE django_content_type.id = ... LIMIT 21
SELECT django_content_type.id, django_content_type.app_label, django_content_type.model FROM django_content_type WHERE django_content_type.id = ... LIMIT 21
SELECT django_content_type.id, django_content_type.app_label, django_content_type.model FROM django_content_type WHERE django_content_type.id = ... LIMIT 21
SELECT django_content_type.id, django_content_type.app_label, django_content_type.model FROM django_content_type WHERE django_content_type.id = ... LIMIT 21
SELECT django_content_type.id, django_content_type.app_label, django_content_type.model FROM django_content_type WHERE django_content_type.id = ... LIMIT 21
SELECT invoicing_task.id, invoicing_task.start_date, invoicing_task.start_time,
  invoicing_task.end_date, invoicing_task.end_time, invoicing_task.seqno,
  invoicing_task.every_unit, invoicing_task.every, invoicing_task.positions,
  invoicing_task.monday, invoicing_task.tuesday, invoicing_task.wednesday,
  invoicing_task.thursday, invoicing_task.friday, invoicing_task.saturday,
  invoicing_task.sunday, invoicing_task.max_events, invoicing_task.user_id,
  invoicing_task.log_level, invoicing_task.disabled,
  invoicing_task.last_start_time, invoicing_task.last_end_time,
  invoicing_task.requested_at, invoicing_task.message, invoicing_task.procedure,
  invoicing_task.name, invoicing_task.target_journal_id,
  invoicing_task.max_date_offset, invoicing_task.today_offset FROM invoicing_task
  WHERE NOT invoicing_task.disabled
SELECT accounting_journal.id, accounting_journal.name, accounting_journal.seqno,
  accounting_journal.ref, accounting_journal.build_method,
  accounting_journal.template, accounting_journal.trade_type,
  accounting_journal.voucher_type, accounting_journal.journal_group,
  accounting_journal.auto_check_clearings,
  accounting_journal.auto_fill_suggestions, accounting_journal.force_sequence,
  accounting_journal.preliminary, accounting_journal.make_ledger_movements,
  accounting_journal.account_id, accounting_journal.partner_id,
  accounting_journal.printed_name, accounting_journal.dc,
  accounting_journal.yearly_numbering, accounting_journal.must_declare,
  accounting_journal.uploads_volume_id,
  accounting_journal.default_invoiceable_type_id,
  accounting_journal.printed_name_de, accounting_journal.printed_name_fr,
  accounting_journal.name_de, accounting_journal.name_fr,
  accounting_journal.sepa_account_id FROM accounting_journal
  WHERE accounting_journal.id = 1 LIMIT 21

TODO: explain why `django_content_type.id` is not always the same.

>>> reset_sql_queries()

.. _specs.tera.sql.AccountingReport:


Now we run some action and look at the SQL queries resulting from it.

We run the :meth:`run_update_plan` action of an accounting report
(:class:`sheets.Report <lino_xl.lib.sheets.Report>`).  You might want
to read the Django documentation about `Using aggregates within a
Subquery expression
<https://docs.djangoproject.com/en/5.0/ref/models/expressions/#using-aggregates-within-a-subquery-expression>`__.

>>> ses = rt.login("robin")
>>> obj = rt.models.sheets.Report.objects.get(pk=1)

>>> reset_sql_queries()
>>> obj.run_update_plan(ses)
>>> show_sql_summary()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
======================== =========== =======
 table                    stmt_type   count
------------------------ ----------- -------
                          COMMIT      4
                          INSERT      91
                          UNKNOWN     4
 accounting_account       SELECT      19
 ana_account              SELECT      16
 cal_event                SELECT      91
 cal_task                 SELECT      91
 checkdata_message        SELECT      91
 contacts_partner         SELECT      54
 django_content_type      SELECT      14
 excerpts_excerpt         SELECT      91
 invoicing_item           SELECT      91
 memo_mention             SELECT      182
 notes_note               SELECT      91
 periods_storedperiod     SELECT      2
 sheets_accountentry      DELETE      1
 sheets_accountentry      SELECT      1
 sheets_anaaccountentry   DELETE      1
 sheets_anaaccountentry   SELECT      1
 sheets_item              SELECT      29
 sheets_itementry         DELETE      1
 sheets_itementry         SELECT      2
 sheets_partnerentry      DELETE      1
 sheets_partnerentry      SELECT      1
 sheets_report            SELECT      91
 topics_tag               SELECT      91
 trading_invoiceitem      SELECT      91
 uploads_upload           SELECT      91
======================== =========== =======
<BLANKLINE>


TODO: above output shows some bug with parsing the statements, and
then we must explain why there are so many select statements in
unrelated tables (e.g. notes_note).

Here is an untested simplified log of the full SQL queries:

>>> show_sql_queries()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF +SKIP
SELECT ... FROM django_session WHERE (...)
SELECT users_user.id, ... FROM users_user WHERE users_user.id = 1
SELECT ... FROM ledger_accountingperiod WHERE ledger_accountingperiod.id = 1
SELECT ... FROM ledger_accountingperiod WHERE ledger_accountingperiod.id = 3
SELECT accounts_account.id, ...,
  (SELECT CAST(SUM(V0.amount) AS NUMERIC) AS total FROM ledger_movement V0
    INNER JOIN ledger_voucher V2 ON (V0.voucher_id = V2.id)
      WHERE (V0.account_id = (accounts_account.id)
        AND V2.accounting_period_id IN (SELECT U0.id AS Col1 FROM ledger_accountingperiod U0 WHERE U0.ref < '2015-01')
        AND V0.dc = 0)
        GROUP BY V0.account_id)
   AS old_c,
   (SELECT ...) AS during_d,
   (SELECT ...) AS during_c,
   (SELECT ...) AS old_d
   FROM accounts_account
     LEFT OUTER JOIN accounts_group ON (accounts_account.group_id = accounts_group.id)
       WHERE NOT ((SELECT CAST(SUM(V0.amount) AS NUMERIC) AS total FROM ledger_movement V0
         INNER JOIN ledger_voucher V2 ON (V0.voucher_id = V2.id)
         WHERE (V0.account_id = (accounts_account.id)
           AND V2.accounting_period_id IN (SELECT U0.id AS Col1 FROM ledger_accountingperiod U0 WHERE U0.ref < '2015-01')
           AND V0.dc = 0)
           GROUP BY V0.account_id) = '0'
       AND (...) = '0' AND (... = '0' AND (...) = '0')
   ORDER BY accounts_group.ref ASC, accounts_account.ref ASC
SELECT ... FROM system_siteconfig WHERE system_siteconfig.id = 1
SELECT ... FROM accounts_account WHERE accounts_account.id = 1
SELECT contacts_partner.id, ...,
  (SELECT CAST(SUM(V0.amount) AS NUMERIC) AS total
      FROM ledger_movement V0 INNER JOIN ledger_voucher V3 ON (V0.voucher_id = V3.id)
        WHERE (V0.partner_id = (contacts_partner.id) AND V0.account_id = 1
        AND V3.accounting_period_id IN (...) AND V0.dc = 0)
        GROUP BY V0.partner_id) AS old_c,
  (SELECT ...) AS during_d,
  (SELECT ...) AS during_c,
  (SELECT ...) AS old_d
  FROM contacts_partner
  WHERE NOT (...)
  ORDER BY contacts_partner.name ASC, contacts_partner.id ASC
SELECT ... FROM accounts_account WHERE accounts_account.id = 2
SELECT contacts_partner.id, contacts_partner.email, ...
  (SELECT CAST(SUM(V0.amount) AS NUMERIC) AS total
     FROM ledger_movement V0
     INNER JOIN ledger_voucher V3 ON (V0.voucher_id = V3.id)
       WHERE (V0.partner_id = (contacts_partner.id) AND V0.account_id = 2
         AND V3.accounting_period_id IN (...) AND V0.dc = 0)
       GROUP BY V0.partner_id)
    AS old_c,
  (SELECT ...) AS during_c,
  (SELECT ...) AS old_d
  FROM contacts_partner
  WHERE NOT (...)
  ORDER BY contacts_partner.name ASC, contacts_partner.id ASC
SELECT ... FROM users_user WHERE users_user.username = 'robin'
