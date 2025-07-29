.. doctest docs/plugins/agenda.rst
.. _dg.plugins.agenda:

====================================
``agenda`` : Agenda functionality
====================================

.. currentmodule:: lino_xl.lib.agenda

The :mod:`lino_xl.lib.agenda` plugin adds agenda functionality.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.min9.settings')


>>> from lino.api.doctest import *


.. class:: Item

  The Django model to represent an :term:`agenda item`.

  .. attribute:: meeting

    The meeting.

  .. attribute:: topic

    The optional topic.

  .. attribute:: title

    The title.

  .. attribute:: description

    A rich-text description.


Demo fixtures
=============

The default implementation loops over the first 12 calendar events that are
appointments and creates 8 agenda items for each of them.

>>> rt.show(agenda.Items)
==== ===== ================================= =================================== =================================== =============
 ID   No.   Calendar entry                    Ticket                              Title                               Description
---- ----- --------------------------------- ----------------------------------- ----------------------------------- -------------
 1    1     Diner (03.10.2014 08:30)          #1 (Bar cannot baz)                 #1 (Bar cannot baz)
 2    2     Diner (03.10.2014 08:30)          #2 (Bars have no foo)               #2 (Bars have no foo)
 3    3     Diner (03.10.2014 08:30)          #3 (How to get bar from foo)        #3 (How to get bar from foo)
 4    1     Abendessen (04.10.2014 09:40)     #4 (Foo never bars)                 #4 (Foo never bars)
 5    2     Abendessen (04.10.2014 09:40)     #5 (No more foo when bar is gone)   #5 (No more foo when bar is gone)
 6    3     Abendessen (04.10.2014 09:40)     #6 (Cannot delete foo)              #6 (Cannot delete foo)
 7    4     Abendessen (04.10.2014 09:40)     #7 (Why <p> tags are so bar)        #7 (Why <p> tags are so bar)
 8    1     Breakfast (05.10.2014 10:20)      #8 (Irritating message when bar)    #8 (Irritating message when bar)
 9    2     Breakfast (05.10.2014 10:20)      #9 (How can I see where bar?)       #9 (How can I see where bar?)
 10   3     Breakfast (05.10.2014 10:20)      #10 (Misc optimizations in Baz)     #10 (Misc optimizations in Baz)
 11   4     Breakfast (05.10.2014 10:20)      #1 (Bar cannot baz)                 #1 (Bar cannot baz)
 12   5     Breakfast (05.10.2014 10:20)      #2 (Bars have no foo)               #2 (Bars have no foo)
 13   1     Réunion (05.10.2014 11:10)        #3 (How to get bar from foo)        #3 (How to get bar from foo)
 14   2     Réunion (05.10.2014 11:10)        #4 (Foo never bars)                 #4 (Foo never bars)
 15   3     Réunion (05.10.2014 11:10)        #5 (No more foo when bar is gone)   #5 (No more foo when bar is gone)
 16   4     Réunion (05.10.2014 11:10)        #6 (Cannot delete foo)              #6 (Cannot delete foo)
 17   5     Réunion (05.10.2014 11:10)        #7 (Why <p> tags are so bar)        #7 (Why <p> tags are so bar)
 18   6     Réunion (05.10.2014 11:10)        #8 (Irritating message when bar)    #8 (Irritating message when bar)
 19   1     Beratung (06.10.2014 13:30)       #9 (How can I see where bar?)       #9 (How can I see where bar?)
 20   2     Beratung (06.10.2014 13:30)       #10 (Misc optimizations in Baz)     #10 (Misc optimizations in Baz)
 21   3     Beratung (06.10.2014 13:30)       #1 (Bar cannot baz)                 #1 (Bar cannot baz)
 22   4     Beratung (06.10.2014 13:30)       #2 (Bars have no foo)               #2 (Bars have no foo)
 23   5     Beratung (06.10.2014 13:30)       #3 (How to get bar from foo)        #3 (How to get bar from foo)
 24   6     Beratung (06.10.2014 13:30)       #4 (Foo never bars)                 #4 (Foo never bars)
 25   7     Beratung (06.10.2014 13:30)       #5 (No more foo when bar is gone)   #5 (No more foo when bar is gone)
 26   1     Seminar (07.10.2014 08:30)        #6 (Cannot delete foo)              #6 (Cannot delete foo)
 27   2     Seminar (07.10.2014 08:30)        #7 (Why <p> tags are so bar)        #7 (Why <p> tags are so bar)
 28   3     Seminar (07.10.2014 08:30)        #8 (Irritating message when bar)    #8 (Irritating message when bar)
 29   1     Evaluation (07.10.2014 09:40)     #9 (How can I see where bar?)       #9 (How can I see where bar?)
 30   2     Evaluation (07.10.2014 09:40)     #10 (Misc optimizations in Baz)     #10 (Misc optimizations in Baz)
 31   3     Evaluation (07.10.2014 09:40)     #1 (Bar cannot baz)                 #1 (Bar cannot baz)
 32   4     Evaluation (07.10.2014 09:40)     #2 (Bars have no foo)               #2 (Bars have no foo)
 33   1     Erstgespräch (08.10.2014 10:20)   #3 (How to get bar from foo)        #3 (How to get bar from foo)
 34   2     Erstgespräch (08.10.2014 10:20)   #4 (Foo never bars)                 #4 (Foo never bars)
 35   3     Erstgespräch (08.10.2014 10:20)   #5 (No more foo when bar is gone)   #5 (No more foo when bar is gone)
 36   4     Erstgespräch (08.10.2014 10:20)   #6 (Cannot delete foo)              #6 (Cannot delete foo)
 37   5     Erstgespräch (08.10.2014 10:20)   #7 (Why <p> tags are so bar)        #7 (Why <p> tags are so bar)
 38   1     Interview (09.10.2014 11:10)      #8 (Irritating message when bar)    #8 (Irritating message when bar)
 39   2     Interview (09.10.2014 11:10)      #9 (How can I see where bar?)       #9 (How can I see where bar?)
 40   3     Interview (09.10.2014 11:10)      #10 (Misc optimizations in Baz)     #10 (Misc optimizations in Baz)
 41   4     Interview (09.10.2014 11:10)      #1 (Bar cannot baz)                 #1 (Bar cannot baz)
 42   5     Interview (09.10.2014 11:10)      #2 (Bars have no foo)               #2 (Bars have no foo)
 43   6     Interview (09.10.2014 11:10)      #3 (How to get bar from foo)        #3 (How to get bar from foo)
 44   1     Diner (09.10.2014 13:30)          #4 (Foo never bars)                 #4 (Foo never bars)
 45   2     Diner (09.10.2014 13:30)          #5 (No more foo when bar is gone)   #5 (No more foo when bar is gone)
 46   3     Diner (09.10.2014 13:30)          #6 (Cannot delete foo)              #6 (Cannot delete foo)
 47   4     Diner (09.10.2014 13:30)          #7 (Why <p> tags are so bar)        #7 (Why <p> tags are so bar)
 48   5     Diner (09.10.2014 13:30)          #8 (Irritating message when bar)    #8 (Irritating message when bar)
 49   6     Diner (09.10.2014 13:30)          #9 (How can I see where bar?)       #9 (How can I see where bar?)
 50   7     Diner (09.10.2014 13:30)          #10 (Misc optimizations in Baz)     #10 (Misc optimizations in Baz)
 51   1     Abendessen (10.10.2014 08:30)     #1 (Bar cannot baz)                 #1 (Bar cannot baz)
 52   2     Abendessen (10.10.2014 08:30)     #2 (Bars have no foo)               #2 (Bars have no foo)
 53   3     Abendessen (10.10.2014 08:30)     #3 (How to get bar from foo)        #3 (How to get bar from foo)
 54   1     Breakfast (11.10.2014 09:40)      #4 (Foo never bars)                 #4 (Foo never bars)
 55   2     Breakfast (11.10.2014 09:40)      #5 (No more foo when bar is gone)   #5 (No more foo when bar is gone)
 56   3     Breakfast (11.10.2014 09:40)      #6 (Cannot delete foo)              #6 (Cannot delete foo)
 57   4     Breakfast (11.10.2014 09:40)      #7 (Why <p> tags are so bar)        #7 (Why <p> tags are so bar)
==== ===== ================================= =================================== =================================== =============
<BLANKLINE>
