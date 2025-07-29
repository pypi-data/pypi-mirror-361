=======================
Running a POS with Lino
=======================

Lino can theoretically act as the software on a :term:`point of sale` (POS)
system.

A demo is in :mod:`lino_book.projects.cosi5`.

The main missing parts are:

- Usage is not yet intuitive (:ticket:`4579`)

- The :mod:`lino_xl.lib.ean` plugin is not yet implemented

- Communication with the miscellaneous devices (EAN scanner, printer, cash
  drawer, payment terminals, customer display, ...)



.. glossary::

  point of sale

    See https://en.wikipedia.org/wiki/Point_of_sale
