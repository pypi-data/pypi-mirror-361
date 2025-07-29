.. doctest docs/specs/lists.rst
.. _specs.lists:

=========================
``lists`` : Partner lists
=========================

.. currentmodule:: lino_xl.lib.lists

The :mod:`lino_xl.lib.lists` plugin adds functionality for managing partner
lists.

.. contents::
   :depth: 1
   :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *

.. glossary::

  Partner list

    A list of partners.

  List membership

    The fact that a given partner is in a given list.


.. class:: List

  Django model to represent a partner list.

  .. attribute:: name
  .. attribute:: ref
  .. attribute:: list_type
  .. attribute:: remark

.. class:: Member

  Django model to represent a membership of a partner in a list.

  .. attribute:: partner
  .. attribute:: list
  .. attribute:: remark
  .. attribute:: seqno


>>> rt.show(lists.Lists)
=========== ================================ ==================
 Reference   overview                         List Type
----------- -------------------------------- ------------------
             `Announcements <…>`__            Mailing list
             `Weekly newsletter <…>`__        Mailing list
             `General discussion <…>`__       Discussion group
             `Beginners forum <…>`__          Discussion group
             `Developers forum <…>`__         Discussion group
             `PyCon 2014 <…>`__               Flags
             `Free Software Day 2014 <…>`__   Flags
             `Schools <…>`__                  Flags
=========== ================================ ==================
<BLANKLINE>

>>> obj = lists.List.objects.get(pk=1)
>>> rt.show(lists.MembersByList, obj)
===== =============================== ======== ========== ===================================================== ===================================================================
 No.   Partner                         Remark   Workflow   Address                                               Contact details
----- ------------------------------- -------- ---------- ----------------------------------------------------- -------------------------------------------------------------------
 1     Rumma & Ko OÜ                                       Uus tn 1, Vigala vald, 78003 Rapla maakond, Estonia   `https://www.saffre-rumma.net/ <https://www.saffre-rumma.net/>`__
 9     Bernd Brechts Bücherladen                           Brienner Straße 18, 80333 Aachen, Germany
 17    Bastiaensen Laurent                                 Am Berg, 4700 Eupen
 25    Ernst Berta                                         Bergkapellstraße, 4700 Eupen
 33    Hilgers Hildegard                                   Favrunpark, 4700 Eupen
 41    Kaivers Karl                                        Haasberg, 4700 Eupen
 49    Meier Marie-Louise                                  Hisselsgasse, 4700 Eupen
 57    Radermacher Edgard                                  4730 Raeren
 65    da Vinci David                                      4730 Raeren
 73    Radermecker Rik                                     Amsterdam, Netherlands
 81    Jeanémart Jérôme                                    Paris, France
 89    Electrabel Customer Solutions                       Boulevard Simón Bolívar 34, 1000 Brussels             `https://www.electrabel.be <https://www.electrabel.be>`__
===== =============================== ======== ========== ===================================================== ===================================================================
<BLANKLINE>


The quick search field of a members list looks in the partner names and the
membership remark.

>>> rt.show(lists.MembersByList, obj, quick_search="ers")
===== =================== ======== ========== ======================== =================
 No.   Partner             Remark   Workflow   Address                  Contact details
----- ------------------- -------- ---------- ------------------------ -----------------
 33    Hilgers Hildegard                       Favrunpark, 4700 Eupen
 41    Kaivers Karl                            Haasberg, 4700 Eupen
===== =================== ======== ========== ======================== =================
<BLANKLINE>


>>> [f.name for f in lists.Member.quick_search_fields]
['partner__name', 'remark']
