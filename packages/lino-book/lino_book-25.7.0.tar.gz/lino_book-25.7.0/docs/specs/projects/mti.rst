=============================
Multi-table inheritance (MTI)
=============================


..  how to test just this page:

    $ doctest docs/specs/projects/mti.rst

    doctest init:
    >>> from lino import startup
    >>> startup('lino_book.projects.mti.settings')
    >>> from lino.api.doctest import *
    >>> Person = app.Person
    >>> Restaurant = app.Restaurant
    >>> Place = app.Place
    >>> Visit = app.Visit
    >>> Meal = app.Meal


This document describes the :mod:`lino_book.projets.mti` demo project,
an application used for testing and explaining :ref:`dev.mti`.

.. currentmodule:: lino.utils.mti

.. contents::
   :local:
   :depth: 2




The example database
--------------------

Here is the :xfile:`models.py` file used for this example.  This is
classical Django know-how: `Restaurant` inherits from `Place`, and
`Place` is *not* abstract.  That's what Django calls `multi table
inheritance
<https://docs.djangoproject.com/en/5.0/topics/db/models/#multi-table-inheritance>`_.

.. literalinclude:: /../../book/lino_book/projects/mti/app/models.py

>>> rt.show("app.Persons")
========
 name
--------
 Anne
 Bert
 Claude
 Dirk
 Ernie
 Fred
========
<BLANKLINE>

>>> rt.show("app.Places")
==== ===================== ============================
 ID   name                  owners
---- --------------------- ----------------------------
 1    Bert's pub            `Anne <…>`__, `Bert <…>`__
 2    The Chopping Shack    `Anne <…>`__
 3    The Abacus Well       `Claude <…>`__
 4    The Olive Lounge      `Ernie <…>`__
 5    The Autumn Bite       `Anne <…>`__
 6    The Private Mission   `Claude <…>`__
 7    Nova                  `Ernie <…>`__
 8    Babylon               `Anne <…>`__
 9    Blossoms              `Claude <…>`__
 10   Whisperwind           `Ernie <…>`__
 11   Catch                 `Anne <…>`__
==== ===================== ============================
<BLANKLINE>


>>> rt.show("app.Restaurants")
==== ===================== ================= ================ ==============
 ID   name                  serves hot dogs   owners           cooks
---- --------------------- ----------------- ---------------- --------------
 2    The Chopping Shack    No                `Anne <…>`__     `Bert <…>`__
 3    The Abacus Well       No                `Claude <…>`__   `Dirk <…>`__
 4    The Olive Lounge      No                `Ernie <…>`__    `Fred <…>`__
 5    The Autumn Bite       No                `Anne <…>`__     `Bert <…>`__
 6    The Private Mission   No                `Claude <…>`__   `Dirk <…>`__
 7    Nova                  No                `Ernie <…>`__    `Fred <…>`__
 8    Babylon               No                `Anne <…>`__     `Bert <…>`__
 9    Blossoms              No                `Claude <…>`__   `Dirk <…>`__
 10   Whisperwind           No                `Ernie <…>`__    `Fred <…>`__
 11   Catch                 No                `Anne <…>`__     `Bert <…>`__
==== ===================== ================= ================ ==============
<BLANKLINE>
