.. doctest docs/plugins/sources.rst
.. _xl.plugins.sources:

============================================
``sources`` : manage bibliographic sources
============================================

.. currentmodule:: lino_xl.lib.sources

The :mod:`lino_xl.lib.sources` plugin adds the notions for managing your
:term:`bibliographic sources <bibliographic source>`, including lists of
sources, authors and licenses.

.. contents::
   :depth: 1
   :local:


About this document
===================

Examples in this document use the :mod:`lino_book.projects.cms1` demo
project.

>>> from lino import startup
>>> startup('lino_book.projects.cms1.settings')
>>> from lino.api.doctest import *


:menuselection:`Publisher --> Sources`.

Authors and Licenses can be configured via
:menuselection:`Configure --> Publisher --> Authors`
and
:menuselection:`Configure --> Publisher --> Licenses`.

>>> show_menu_path('sources.Sources')
Publisher --> Sources
>>> show_menu_path('sources.Authors')
Configure --> Publisher --> Authors
>>> show_menu_path('sources.Licenses')
Configure --> Publisher --> Licenses


>>> rt.show('sources.Sources')
==== =========================================== ======================================= =======================================================================================================
 ID   Title                                       Author                                  URL
---- ------------------------------------------- --------------------------------------- -------------------------------------------------------------------------------------------------------
 1    Private collection                          Luc Saffre
 2    The Hitchhiker's Guide to the Galaxy        Douglas Adams (1952-11-03—2001-11-05)
 3    Crossroads, Kilham West Field               Christine Johnstone                     https://commons.wikimedia.org/wiki/File:Crossroads,_Kilham_West_Field_-_geograph.org.uk_-_2097672.jpg
 4    Haunted House - geograph.org.uk - 6141456   Derek Harper                            https://commons.wikimedia.org/wiki/File:Haunted_House_-_geograph.org.uk_-_6141456.jpg
 5    People talking (3945337913).jpg             Herman Theodore Bohlman (*1872-04-15)   https://commons.wikimedia.org/wiki/File:People_talking_(3945337913).jpg
 6    History of PDF - Wikipedia                                                          https://en.wikipedia.org/wiki/History_of_PDF
==== =========================================== ======================================= =======================================================================================================
<BLANKLINE>


>>> rt.show('sources.Authors')
=========== ================= ============
 Last name   First name        Birth date
----------- ----------------- ------------
 Adams       Douglas           1952-11-03
 Bohlman     Herman Theodore   1872-04-15
 Harper      Derek
 Johnstone   Christine
 Saffre      Luc
=========== ================= ============
<BLANKLINE>


>>> rt.show('sources.Licenses')
======================== ======================== ========================
 Designation              Designation (de)         Designation (fr)
------------------------ ------------------------ ------------------------
 All rights reserved      All rights reserved      All rights reserved
 Creative Commons BY SA   Creative Commons BY SA   Creative Commons BY SA
======================== ======================== ========================
<BLANKLINE>
