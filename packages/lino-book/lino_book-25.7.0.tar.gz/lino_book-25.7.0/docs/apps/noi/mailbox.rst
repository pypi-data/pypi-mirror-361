.. doctest docs/apps/noi/mailbox.rst
.. _noi.specs.mailbox:

====================
Lino Noi and mailbox
====================

>>> import pytest; pytest.skip('this doctest is not maintained')

This page describes the :mod:`lino_xl.lib.mailbox` plugin.

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *


TODO: write some explanations...

>>> # rt.show('mailbox.Messages', column_names="subject from_header to_header")
================================================= ========================================= ================
 Subject                                           From header                               To header
------------------------------------------------- ----------------------------------------- ----------------
 Re: Tonis in Vigala                               Tanel Saimre <tanel.saimre@example.com>   Luc Saffre
 Tonis in Vigala                                   Luc Saffre <luc.saffre@example.com>       Tanel Saimre
 parameters crash course by example                Luc Saffre <luc.saffre@example.com>       Tonis Piip
 Next hangout                                      Luc Saffre <luc.saffre@example.com>       Khchine Hamza
 with attachments                                  tonis <tonis@Pluto>                       team@localhost
 Re: Furnitures company                            "Stephanie.c" <stephanie.c@bigao-f.com>
 *****SPAM***** re: buy more instagram followers   "STEVEN" <medinaluca1@gmail.com>
================================================= ========================================= ================
<BLANKLINE>
