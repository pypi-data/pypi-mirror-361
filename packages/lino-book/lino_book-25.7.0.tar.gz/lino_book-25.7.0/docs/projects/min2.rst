.. doctest docs/projects/min2.rst

==================================================
``min2`` :
==================================================

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.min2.settings.demo')
>>> from lino.api.doctest import *
>>> ses = rt.login('robin')



Person #16 is not a Partner
----------------------------

Person #16 ('Altenberg Hans') is not a Partner (master_key is
<django.db.models.fields.related.ForeignKey: partner>)

>>> url = '/bs3/contacts/Person/16'
>>> test_client.force_login(rt.login('robin').user)
>>> res = test_client.get(url, REMOTE_USER='robin')
>>> print(res.status_code)
200
