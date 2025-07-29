.. doctest docs/specs/events/index.rst
.. _book.specs.events:

=========================================
``events`` : Publishing an event calendar
=========================================

The :mod:`lino_book.projects.events` project and the :mod:`lino_xl.lib.events`
plugin were written for a website site that no longer exists, but the project
remains interesting because it has an example of a :ref:`table view with dynamic
columns <get_handle_name>`.

This project does not use :mod:`lino.modlib.users` because the content was being
maintained by updating the source code of its demo fixture (file `vor.py
<https://gitlab.com/lino-framework/xl/-/blob/master/lino_xl/lib/events/fixtures/vor.py>`__)

Originally this project didn't even have a web :term:`front end`. It just
created a set of Sphinx source files, which were then built into a static web
site. See :blogref:`20140203`.

Meanwhile this approach is no longer used because Lino has evolved since then.
You just invoke :manage:`runserver` in the project directory as with any Lino
demo site. The website is "automatically" read-only because
:class:`AnonymousUser` has no permission to edit anything.

.. image:: events_main.png

The :term:`dashboard` of this site shows a series of tables that are all defined
by a same actor, but their columns vary depending on the type of event: some
tables have three columns  ("When?" "What?" and "Where?") while others have only
two columns ("When?" and "Where?").


.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.events.settings')
>>> from lino.api.doctest import *


Test the content of the admin main page.

>>> # test_client.force_login(rt.login('rolf').user)
>>> # res = test_client.get('/api/main_html', REMOTE_USER='rolf')
>>> res = test_client.get('/api/main_html')
>>> print(res.status_code)
200
>>> result = json.loads(res.content.decode())
>>> result['success']
True
>>> # print(html2text(result['html']))
>>> soup = BeautifulSoup(result['html'], 'lxml')

Test a few basic things:

>>> links = soup.find_all('a')
>>> len(links)
8

>>> tables = soup.find_all('table')
>>> len(tables)
4

>>> for h in soup.find_all('h2'):
...     print(h.text.strip())
Breitensport ⏏
Radrennen Straße ⏏
MTB Rennen ≥ 15-jährige ⏏
Mountainbike Rennsport -- Kids Trophy O2 Biker/V.O.R.-Lotto ⏏


We might also test the complete content, but currently we skip this test as it
is much work to maintain.

>>> print(soup.get_text(' ', strip=True))
... #doctest: +NORMALIZE_WHITESPACE +REPORT_CDIFF +SKIP
