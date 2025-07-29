.. doctest docs/specs/voga/partners.rst
.. _voga.specs.partners:

=====================
Partners in Lino Voga
=====================

>>> from lino_book.projects.voga2.startup import *


Partners in Lino Voga are :class:`polymorphic
<lino.mixins.polymorphic.Polymorphic>`, i.e. the database has a series
of models which are more or less specialized subclasses of a partner.

In Lino Voga we differentiate the following subclasses of Partner:

.. django2rst:: contacts.Partner.print_subclasses_graph()


..
    >>> from lino.mixins.polymorphic import Polymorphic
    >>> issubclass(contacts.Person, Polymorphic)
    True
    >>> issubclass(contacts.Person, contacts.Partner)
    True
    >>> issubclass(courses.Pupil, contacts.Person)
    True
    >>> issubclass(courses.Teacher, contacts.Person)
    True
    >>> issubclass(courses.Teacher, contacts.Partner)
    True

    >>> print(noblanklines(contacts.Partner.get_subclasses_graph()))
    .. graphviz::
       digraph foo {
        "Partner" -> "Organization"
        "Partner" -> "Person"
        "Person" -> "Participant"
        "Person" -> "Instructor"
      }



Partner lists
=============

Members of partner lists in the demo database.

>>> rt.show(lists.Members)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
===== ===== ======================== =================================== ========
 ID    No.   Partner List             Partner                             Remark
----- ----- ------------------------ ----------------------------------- --------
 1     1     Announcements            Bestbank
 2     2     Weekly newsletter        Rumma & Ko OÜ
 3     3     General discussion       Bäckerei Ausdemwald
 4     4     Beginners forum          Bäckerei Mießen
 ...
 101   101   Developers forum         AA Neudorf
 102   102   PyCon 2014               Nisperter Schützenverein
 103   103   Free Software Day 2014   Mehrwertsteuer-Kontrollamt Eupen
===== ===== ======================== =================================== ========
<BLANKLINE>


>>> from urllib.parse import quote
>>> url = '/api/lists/Members?'
>>> url += 'limit=20&start=0&fmt=json&'
>>> url += "filter=" + quote('[{"type":"string","value":"3","field":"list"}]')
>>> test_client.force_login(rt.login('robin').user)
>>> res = test_client.get(url, REMOTE_USER='robin')
>>> print(res.status_code)
200

>>> d = json.loads(res.content.decode())
>>> d['count']
14
>>> d['rows'][13]
[None, None, None, None, None, None, None, None, None, None, None, {'meta': True, 'phantom': True}]


..
  >>> dbhash.check_virgin()
