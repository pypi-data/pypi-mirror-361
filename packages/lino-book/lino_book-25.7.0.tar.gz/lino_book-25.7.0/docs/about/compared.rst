=================================
Lino compared to other frameworks
=================================

The following projects do something similar to Lino.  If you have used or
otherwise know one of them, please write a few sentences about what's
different.

.. contents::
  :local:

.. _plain_django:

Plain Django
============

From the technological point of view, Lino applications are *just Django*
projects combined to an ExtJS or React front end.  People who know how to host a
Django project can also host a Lino application.


.. _tryton:

Odoo / Tryton
=============

Lino can be compared to `Tryton <http://www.tryton.org/>`__ and `Odoo
<https://en.wikipedia.org/wiki/Odoo>`__ (formerly known as OpenERP).

Several technical differences could be mentioned:

- Odoo is rather a highly configurable and modularized ERP *application* while
  Lino is a *framework* for creating such applications.

- Odoo requires Postgresql as a DBMS while Lino can be used with any DBMS
  supported by Django.

- Odoo addons or Odoo applications (equivalents of plugins in Lino) must be
  written in the Odoo logic while Lino applications can use any Django packages.
  Which means that Lino is backed by a bigger community.

Starting at the v9.0 release, Odoo was split into a proprietary enterprise
edition with cloud-hosted SaaS and a cut-down community edition. So  Odoo is not
Free Software in the meaning defined by the FSF. The freely downloadable
Community Edition is not for commercial use. It is only for non-profits and
students. Besides this it has limited functionality, for example, it works only
on Desktop, not on Mobile devices. And functionalities like Accounting, Payroll,
Documents, Signing exist only in the Enterprise edition. (`Source
<https://www.odoo.com/page/editions)>`__)




restdb.io
=========

With `restdb.io <https://restdb.io>`__, a company based in Bergen
(Norway), you have "collections" (which correspond to Django's models)
and "pages" (which correspond to Django's views).  With restdb you can
switch to "developer mode" and edit your database structure. There is
a basic user interface for entering data into these collections. And
you have an API for accessing the data from other applications. A nice
tool, certainly useful for certain kinds of applications.

Lino has more complex UI concepts (tables, form layouts, menus,
actions, virtual fields, slave tables, ...).  restdb.io is not meant
for writing e.g. a accounting or calender application.

Lino has no "visual GUI editor".  In Lino you define all these things using
Python code, not via a web interface.


Apache Isis
===========

`Apache Isis <https://isis.apache.org>`__ is a DDD framework in Java.

An example application is `Estatio <http://www.estatio.org>`__, which was
developed to fulfil the needs of a big real estate company in the EU. It is Open
Source and its main contributor appears to still be the company that created it.


Appy framework
==============

- `Appy framework <http://appyframework.org/>`_


Dolibarr
========

- https://www.dolibarr.org/
