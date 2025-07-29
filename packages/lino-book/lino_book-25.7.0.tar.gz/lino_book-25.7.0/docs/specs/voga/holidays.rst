.. doctest docs/specs/voga/holidays.rst
.. _voga.specs.holidays:

==============================
Holidays in Lino Voga
==============================

See also :ref:`xl.specs.holidays`.

..  Some initialization:

    >>> from lino_book.projects.voga2.startup import *
    >>> settings.SITE.verbose_client_info_message = True
    >>> from lino.api import rt, _
    >>> from atelier.utils import i2d
    >>> RecurrentEvent = cal.RecurrentEvent
    >>> Recurrences = cal.Recurrences


A series of weekends
====================


>>> obj = courses.Course.objects.get(name__contains="Weekends")
>>> print(obj)
Five Weekends 2015
>>> print(obj.start_date)
2015-06-19
>>> print(dd.today())
2015-05-22


>>> rt.show(cal.EntriesByController, obj, column_names="when_text detail_link state", nosummary=True)
=============================== ========================= ===========
 When                            Calendar entry            State
------------------------------- ------------------------- -----------
 Fri 06/11/2015-Sun 08/11/2015   `Activity #26  5 <…>`__   Suggested
 Fri 02/10/2015-Sun 04/10/2015   `Activity #26  4 <…>`__   Suggested
 Fri 28/08/2015-Sun 30/08/2015   `Activity #26  3 <…>`__   Suggested
 Fri 24/07/2015-Sun 26/07/2015   `Activity #26  2 <…>`__   Suggested
 Fri 19/06/2015-Sun 21/06/2015   `Activity #26  1 <…>`__   Suggested
=============================== ========================= ===========
<BLANKLINE>


..
  >>> dbhash.check_virgin()
