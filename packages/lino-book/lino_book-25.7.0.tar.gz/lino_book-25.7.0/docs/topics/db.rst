.. doctest docs/topics/db.rst

===========================
Database overview
===========================


.. contents::
   :depth: 1
   :local:

Import and setup execution context for demonstration purposes.

>>> from lino import startup
>>> startup('lino_book.projects.db_overview.settings')
>>> from lino.utils.diag import analyzer
>>> analyzer.show_db_overview()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
7 plugins: lino, about, jinja, bootstrap3, extjs, staticfiles, db_overview.
1 models:
==================== ========================= ========= =======
 Name                 Default table             #fields   #rows
-------------------- ------------------------- --------- -------
 db_overview.Potato   db_overview.PotatoTable   4         0
==================== ========================= ========= =======
<BLANKLINE>
Found 1 model with duplicate bases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model:
    lino_book.projects.db_overview.models.Potato
Duplicate base:
    Food
Inheritance trees:
    Food.Potato
    Food.Vegetable.Potato
