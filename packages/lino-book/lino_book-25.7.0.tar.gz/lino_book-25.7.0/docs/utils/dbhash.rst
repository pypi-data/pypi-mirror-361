.. doctest docs/utils/addressable.rst

=====================================
The ``lino.utils.dbhash`` module
=====================================

.. currentmodule:: lino.utils.dbhash

This document demonstrates the :mod:`lino.utils.dbhash` module, which is used in
:term:`tested documents <tested document>`.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.min1.startup import *

Usage
=====

It sometimes happens that a doctest modifies the content of the database of a
:term:`demo project`. Such changes remain in the database if we don't "tidy up",
i.e. restore the database state. And they can cause doctest failures in other
documents that are absolutely unrelated except that they use the same
:term:`demo project`. Such failures can be difficult to debug. An example is
:ticket:`6176` (doctest docs/plugins/checkdata.rst fails sometimes) where the
"culprit" was docs/specs/voga/trading.rst, which printed an invoice and thereby
created a :term:`database excerpt`, which later caused :func:`check_virgin` to
report it and the doctest do fail. Now we call :func:`check_virgin` at the end
of every rst document that uses :mod:`lino_book.projects.voga2` so that the
failure happens at least in the document that caused a database change instead
of some random other document.

The :func:`check_virgin` function is there to warn us when the database is not
"virgin", i.e. has been modified after :cmd:`pm prep`. It usually does not print
anything, which means that everything is okay. But when the database has been
modified it prints a warning message, causing our doctest to fail.

Let's try it:

>>> dbhash.check_virgin()

Uff! No warning! Now we know that our database is virgin.

Now here is a code snippet that modifies the content of the database by creating
a database object and then saving it:

>>> obj = contacts.Person(first_name="Joe")
>>> obj.full_clean()
>>> obj.save()

We now have modified the database, so here is what the :func:`check_virgin` now
says:

>>> dbhash.check_virgin()  #docterst: +ELLIPSIS
Database .../lino_book/projects/min1 isn't virgin:
- contacts.Partner: 1 rows added
- contacts.Person: 1 rows added
Tidy up 2 rows from database: [(<class 'lino_xl.lib.contacts.models.Partner'>, {...}), (<class 'lino_xl.lib.contacts.models.Person'>, {...})].
Database has been restored.

Our instance of :class:`lino_xl.lib.contacts.Person` no longer exists in the
database:

>>> contacts.Person.objects.get(pk=obj.pk)
Traceback (most recent call last):
...
lino_xl.lib.contacts.models.Person.DoesNotExist: Person matching query does not exist.

Calling :func:`check_virgin` a second time will be silent again because the
database state has been restored.

>>> dbhash.check_virgin()  #docterst: +ELLIPSIS

Good to know
============

- When the :func:`check_virgin` at the beginning of a document prints warnings,
  then the reason for these warnings is *some other* file that uses the same
  demo project and did not do its job of tidying up.

- When the warnings end with "Database has been restored.", then you can simply
  run the same test case again. Since it has repaired the error condition, it
  will no longer fail.


Limitations
===========

The restore is not perfect. For example the value of the next available primary
key of a table does *not* get restored. That's whay we cannot rely on the
primary key of temporary database objects being the same. The folllowing test
would pass when running this doctest for the first time after :cmd:`pm prep`,
but it would fail the second time because

>>> print(obj.pk)  #doctest: +SKIP
183


Another limitation is that dbhash.check_virgin() can't tidy up in when we also
update existing database rows. The dbhash ignores these changes, it considers
only the primary keys per model.

Here is how the dbhash looks like. It is a `dict` with one key for every
database model, and the value is a list of the primary keys of every row.

>>> pprint(dbhash.compute_dbhash(), compact=True)
{'contacts.Company': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
 'contacts.CompanyType': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                          16],
 'contacts.Partner': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
                      32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45,
                      46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
                      60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73,
                      74, 75, 76, 77, 78, 79, 80, 81],
 'contacts.Person': [15, 13, 14, 16, 17, 70, 77, 20, 19, 18, 22, 80, 21, 24, 23,
                     79, 71, 75, 28, 50, 52, 51, 29, 25, 27, 26, 30, 31, 32, 34,
                     33, 35, 37, 36, 81, 38, 39, 40, 41, 78, 76, 42, 43, 44, 45,
                     46, 72, 47, 49, 48, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62,
                     63, 73, 74, 65, 64, 66, 69, 67, 68],
 'contacts.Role': [3, 1, 2],
 'contacts.RoleType': [1, 2, 3, 4, 5],
 'countries.Country': ['BD', 'BE', 'CD', 'DE', 'EE', 'FR', 'MA', 'NL', 'RU',
                       'US'],
 'countries.Place': [1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                     19, 20, 21, 22, 23, 24, 26, 33, 34, 35, 36, 46, 47, 48, 49,
                     50, 51, 52, 53, 60, 61, 63, 64, 65, 66, 67, 68, 69, 70, 71,
                     72, 73, 74, 75, 76, 77, 78, 79, 80, 2, 4, 25, 27, 28, 29,
                     30, 31, 32, 37, 38, 39, 40, 41, 42, 43, 44, 45, 56, 62, 59,
                     54, 55, 57, 58],
 'system.SiteConfig': [1],
 'users.Authority': [],
 'users.User': [3, 2, 1]}
