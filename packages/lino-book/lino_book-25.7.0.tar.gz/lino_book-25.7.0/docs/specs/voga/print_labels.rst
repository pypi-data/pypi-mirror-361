.. doctest docs/specs/voga/print_labels.rst
.. _voga.specs.print_labels:

======================
Printing addres labels
======================


>>> from lino_book.projects.voga2.startup import *

This document describes and tests printing address labels.


.. contents::
  :local:

>>> settings.SITE.appy_params.update(raiseOnError=True)
>>> test_client.force_login(rt.login('robin').user)
>>> def mytest(k):
...     url = 'http://127.0.0.1:8000/api/{0}?an=print_labels'.format(k)
...     res = test_client.get(url, REMOTE_USER='robin')
...     assert res.status_code == 200
...     result = json.loads(res.content.decode())
...     assert result['success']
...     print(result['open_url'])

>>> mytest("contacts/Persons")  #doctest: -SKIP
/media/cache/appypdf/127.0.0.1/contacts.Persons.pdf


..
  >>> dbhash.check_virgin()
