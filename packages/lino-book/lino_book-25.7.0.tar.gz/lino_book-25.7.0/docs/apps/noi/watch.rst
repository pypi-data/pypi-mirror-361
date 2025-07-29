.. doctest docs/apps/noi/watch.rst

===========================
Lino Noi watcher specs
===========================

This document describes the watchers.


.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *

>>> show_change_watchers()  #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
+------------------+------------------------+------------------------------------------+
| model            | master_key             | ignored_fields                           |
+==================+========================+==========================================+
| comments.Comment | comments.Comment.owner | body_full_preview body_short_preview     |
|                  |                        | created created_natural full_page        |
|                  |                        | list_item modified name_column           |
|                  |                        | navigation_panel overview rowselect user |
|                  |                        | workflow_buttons                         |
+------------------+------------------------+------------------------------------------+
| tickets.Ticket   | None                   | _user_cache created fixed_since modified |
+------------------+------------------------+------------------------------------------+
<BLANKLINE>
