.. doctest docs/apps/cosi/tim2lino.rst
.. _cosi.specs.tim2lino:

==================
Importing from TIM
==================

>>> from lino_book.projects.cosi2.startup import *
>>> from django.db.models import Q


>>> from lino_xl.lib.tim2lino.utils import TimLoader
>>> tim = TimLoader('', 'en')
>>> tim.dc2lino("D")
<accounting.DC.debit:D>

>>> tim.dc2lino("C")
<accounting.DC.credit:C>

>>> tim.dc2lino("A")
<accounting.DC.debit:D>
>>> tim.dc2lino("E")
<accounting.DC.credit:C>
