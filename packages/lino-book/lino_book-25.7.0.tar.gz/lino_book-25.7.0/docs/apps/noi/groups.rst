.. doctest docs/apps/noi/projects.rst
.. _noi.specs.projects:

===================
``groups`` in Noi
===================

This document tests how to :mod:`lino_xl.lib.groups` plugin is used in
:ref:`noi`.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *

>>> ses = rt.login("robin")

>>> ses.show(groups.Groups, max_width=40)
+--------------------+---------+------------------------------------------+
| Team               | Private | Memberships                              |
+====================+=========+==========================================+
| `Developers <…>`__ | No      | `Marc <…>`__, `Rolf Rompen <…>`__,       |
|                    |         | **New** **?**                            |
+--------------------+---------+------------------------------------------+
| `Managers <…>`__   | Yes     | `Jean <…>`__, `Mathieu <…>`__, `Robin    |
|                    |         | Rood <…>`__, **New** **?**               |
+--------------------+---------+------------------------------------------+
| `Sales team <…>`__ | No      | `Luc <…>`__, `Romain Raffault <…>`__,    |
|                    |         | **New** **?**                            |
+--------------------+---------+------------------------------------------+
<BLANKLINE>


>>> ses.show(groups.Groups, column_names="id name")
==== ============= ================== ==================
 ID   Designation   Designation (de)   Designation (fr)
---- ------------- ------------------ ------------------
 1    Developers    Developers         Developers
 2    Managers      Managers           Managers
 3    Sales team    Sales team         Sales team
==== ============= ================== ==================
<BLANKLINE>

>>> ses.show(groups.Memberships)
==== ================= ============ ========
 ID   User              Team         Remark
---- ----------------- ------------ --------
 1    Jean              Managers
 2    Luc               Sales team
 3    Marc              Developers
 4    Mathieu           Managers
 5    Romain Raffault   Sales team
 6    Rolf Rompen       Developers
 7    Robin Rood        Managers
==== ================= ============ ========
<BLANKLINE>


>>> ses.show(groups.MembershipsByUser, master_instance=ses.get_user())
`Managers <…>`__, **New** **?**

>>> sales = groups.Group.objects.get(pk=3)
>>> ses.show(groups.MembershipsByGroup, master_instance=sales)
`Luc <…>`__, `Romain Raffault <…>`__, **New** **?**

>>> rt.login("robin").show(subscriptions.Subscriptions)
==== ============ =========== ===================== ========= ==========================
 ID   Start date   Reference   Partner               Subject   Workflow
---- ------------ ----------- --------------------- --------- --------------------------
 1    07/01/2014   welket      Rumma & Ko OÜ                   **Registered** → [Draft]
 2    27/01/2014   welsch      Bäckerei Ausdemwald             **Registered** → [Draft]
 3    16/02/2014   aab         Bäckerei Mießen                 **Registered** → [Draft]
 4    08/03/2014   bcc         Bäckerei Schmitz                **Registered** → [Draft]
 5    28/03/2014   dde         Garage Mergelsberg              **Registered** → [Draft]
==== ============ =========== ===================== ========= ==========================
<BLANKLINE>
