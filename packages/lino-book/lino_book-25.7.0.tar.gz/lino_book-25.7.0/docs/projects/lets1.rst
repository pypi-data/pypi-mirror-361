.. doctest docs/projects/lets1.rst
.. _book.projects.lets1:

=================================================
``lets1`` : First prototype of the LETS tutorial
=================================================

.. module:: lino_book.projects.lets1

A :term:`demo project` that will be used the new LETS tutorial. Started as a
copy of :mod:`lino_lets`

>>> from lino import startup
>>> startup('lino_book.projects.lets1.settings')
>>> from lino.api.doctest import *
>>> ses = rt.login('robin')


>>> walk_menu_items('robin')  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
- Members --> Members : 10
- Market --> Products : 7
- Market --> Offers : 6
- Market --> Demands : 4
- Configure --> System --> Members : 10
- Configure --> System --> Site configuration : (not tested)
- Configure --> Market --> Places : 5
- Explorer --> System --> Authorities : 1
- Explorer --> System --> User types : 3
- Explorer --> System --> User roles : 2
- Explorer --> Market --> Delivery units : 4
- Site --> About : (not tested)
- Site --> User sessions : ...
<BLANKLINE>

>>> ses.show("market.ActiveProducts", max_width=35)
+-------------------------+-------------------------------------+-------------------------------------+
| Designation             | Offers                              | Demands                             |
+=========================+=====================================+=====================================+
| Bread                   | `Bread offered by Fred <…>`__,      | **New**                             |
|                         | **New**                             |                                     |
+-------------------------+-------------------------------------+-------------------------------------+
| Buckwheat               | `Buckwheat offered by Fred <…>`__,  | `Buckwheat (Henri) <…>`__, **New**  |
|                         | `Buckwheat offered by Anne <…>`__,  |                                     |
|                         | **New**                             |                                     |
+-------------------------+-------------------------------------+-------------------------------------+
| Eggs                    | **New**                             | `Eggs (Henri) <…>`__, `Eggs (Mari)  |
|                         |                                     | <…>`__, **New**                     |
+-------------------------+-------------------------------------+-------------------------------------+
| Electricity repair work | `Electricity repair work offered by | **New**                             |
|                         | Henri <…>`__, `Electricity repair   |                                     |
|                         | work offered by Argo <…>`__,        |                                     |
|                         | **New**                             |                                     |
+-------------------------+-------------------------------------+-------------------------------------+
<BLANKLINE>


>>> ses.show("users.AllUsers", max_width=35)
+------------+----------+-------------------------------------+-------------------------------------+
| First name | Place    | Offers                              | Demands                             |
+============+==========+=====================================+=====================================+
| Anne       | Tallinn  | `Buckwheat offered by Anne <…>`__,  | **New**                             |
|            |          | **New**                             |                                     |
+------------+----------+-------------------------------------+-------------------------------------+
| Argo       | Haapsalu | `Electricity repair work offered by | **New**                             |
|            |          | Argo <…>`__, **New**                |                                     |
+------------+----------+-------------------------------------+-------------------------------------+
| Fred       | Tallinn  | `Bread offered by Fred <…>`__,      | **New**                             |
|            |          | `Buckwheat offered by Fred <…>`__,  |                                     |
|            |          | **New**                             |                                     |
+------------+----------+-------------------------------------+-------------------------------------+
| Henri      | Tallinn  | `Electricity repair work offered by | `Buckwheat (Henri) <…>`__, `Eggs    |
|            |          | Henri <…>`__, **New**               | (Henri) <…>`__, **New**             |
+------------+----------+-------------------------------------+-------------------------------------+
| Jaanika    | Tallinn  | **New**                             | **New**                             |
+------------+----------+-------------------------------------+-------------------------------------+
| Katrin     | Vigala   | **New**                             | **New**                             |
+------------+----------+-------------------------------------+-------------------------------------+
| Mari       | Tartu    | **New**                             | `Eggs (Mari) <…>`__, **New**        |
+------------+----------+-------------------------------------+-------------------------------------+
| Peter      | Vigala   | **New**                             | **New**                             |
+------------+----------+-------------------------------------+-------------------------------------+
| Robin      |          | **New**                             | **New**                             |
+------------+----------+-------------------------------------+-------------------------------------+
<BLANKLINE>
