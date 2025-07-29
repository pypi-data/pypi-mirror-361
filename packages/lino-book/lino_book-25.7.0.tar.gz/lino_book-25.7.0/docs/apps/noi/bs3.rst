.. doctest docs/apps/noi/bs3.rst
.. _noi.specs.bs3:

=====================================================
A read-only interface to Team using generic Bootstrap
=====================================================

This document describes the
:mod:`lino_book.projects.bs3` demo project.


.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.bs3.settings.demo')
>>> from lino.api.doctest import *

This project is a read-only public front end of Lino Noi.

It provides read-only anonymous access to the data of
:mod:`lino_book.projects.noi1e`, using the :mod:`lino.modlib.bootstrap3` front
end. See also :mod:`lino_book.projects.public`


This does not use :mod:`lino.modlib.extjs` at all.


.. contents::
  :local:

.. The following was used to reproduce :ticket:`960`:

    >>> res = test_client.get('/tickets/Ticket/17')
    >>> res.status_code
    200


Tickets are rendered using plain bootstrap HTML:

>>> res = test_client.get('/')
>>> res.status_code
200
>>> soup = BeautifulSoup(res.content, "lxml")
>>> links = soup.find_all('a')
>>> len(links)  #doctest: +SKIP
50
>>> print(links[0].get('href'))
/?ul=de
>>> print(links[1].get('href'))
/?ul=fr
>>> print(links[2].get('href'))
#

NB: The `len(links)` in above snippet is skipped because it gives 49 on some
machines and 50 on some others `example
<https://gitlab.com/lino-framework/book/-/jobs/1396985872>`__. No need to
explore this until somebody wants to use the bs3 front end.

>>> res = test_client.get('/tickets/Ticket/17')
>>> res.status_code
200
>>> soup = BeautifulSoup(res.content, "lxml")


>>> links = soup.find_all('a')
>>> len(links)
28
>>> print(links[0].get('href'))
/

The following is currently skipped because the demo project has some general issues.
See :ticket:`3857`.
For example after clicking on ticket #10 in the dashboard it says that this ticket doesn't exist.

>>> print(soup.get_text(' ', strip=True))
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF +ELLIPSIS +SKIP
Tickets Sign in — Home en de fr Tickets All tickets Office Recent comments Site About #15 (Bars have no foo) << < > >> State: Closed
<BLANKLINE>
<BLANKLINE>
(last update ...) Created ... by Jean Site: pypi ... This is Lino Noi ... using ...
