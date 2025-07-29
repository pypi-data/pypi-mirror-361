.. doctest docs/apps/noi/public.rst
.. _noi.specs.public:

=================================================================
Experimental interface to Team using Bootstrap and self-made URLs
=================================================================

The :mod:`lino_noi.lib.public` front end is yet another way of providing
read-only anonymous access.  But it is probably deprecated because the
:term:`React front end` does it better.

This document describes the :mod:`lino_book.projects.public` variant of
:ref:`noi`, which provides readonly anonymous access to the data of
:mod:`lino_book.projects.noi1e` using the :mod:`lino_noi.lib.public`
front end.


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.public.settings.demo')
>>> from lino.api.doctest import *


The home page:

>>> res = test_client.get('/')
>>> res.status_code
200
>>> soup = BeautifulSoup(res.content, 'lxml')
>>> links = soup.find_all('a')
>>> len(links)
29
>>> print(links[0].get('href'))
/?ul=de
>>> print(links[1].get('href'))
/?ul=fr
>>> print(links[2].get('href'))
/ticket/115


>>> res = test_client.get('/ticket/13/')
>>> res.status_code
200
>>> soup = BeautifulSoup(res.content, 'lxml')
>>> print(soup.get_text(' ', strip=True))
... #doctest: +NORMALIZE_WHITESPACE -REPORT_UDIFF +ELLIPSIS
Home en de fr #13 Bar cannot foo State: Working
<BLANKLINE>
<BLANKLINE>
(last update ...) Created ... by Rolf Rompen Linking to [ticket 1] and to blog .
 © Copyright 2015 Rumma & Ko OÜ | This website runs Lino Noi ... using ...
