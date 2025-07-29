.. doctest docs/specs/tera/topics.rst
.. _specs.tera.topics:

====================================
The ``topics`` plugin in :ref:`tera`
====================================

.. currentmodule:: lino_xl.lib.topics

:ref:`tera` uses the :mod:`lino_xl.lib.topics` plugin.  See
:doc:`/specs/topics` for a general description of this module.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.tera1.settings')
>>> from lino.api.doctest import *
>>> from django.db.models import Q


Overview
========

In :ref:`tera` the :setting:`topics.partner_model` is `None` because  we use
topics only to describe the content of a therapy using tags, but there is no
"partner" to inform about these taggings.

>>> print(dd.plugins.topics.partner_model)
None

>>> rt.models.topics.Interest
Traceback (most recent call last):
...
AttributeError: module 'lino_xl.lib.topics.models' has no attribute 'Interest'


Tags
=========

Note that topic tags are assigned *per therapy*, not e.g. *per patient*.

In the detail window of a therapy they have a panel "Topics"
(:class:`TagsByOwner`).

For example let's take some therapy and look at the interests it has been
assigned to:

>>> c = courses.Course.objects.all().first()
>>> c
Course #1 ('Arens Andreas')

>>> rt.show(topics.TagsByOwner, c)
`(A) Alcoholism <…>`__, `(P) Phobia <…>`__


A site manager can configure the list of topics.

>>> show_menu_path(topics.AllTopics)
Configure --> Topics --> Topics

The detail window of a topic has a panel "Interests"
(:class:`InterestsByTopic`), which shows the dossiers for which this topic is
interesting.

>>> t = topics.Topic.objects.all().first()
>>> t
Topic #1 ('(A) Alcoholism')

>>> rt.show(topics.TagsByTopic, t)  #doctest: +NORMALIZE_WHITESPACE
`Arens Andreas <…>`__, `Arens Annette <…>`__, `Bastiaensen Laurent <…>`__, `Collard Charlotte <…>`__, `Demeulenaere Dorothée <…>`__, `Dericum Daniel <…>`__, `Eierschal Emil <…>`__, `Emonts Daniel <…>`__, `Emontspool Erwin <…>`__, `Evers Eberhart <…>`__, `Evertz Bernd <…>`__, `Groteclaes Gregory <…>`__, `Ingels Irene <…>`__, `Jacobs Jacqueline <…>`__, `Johnen Johann <…>`__, ...

A site manager can see a global list of all tags. This might be useful e.g. for
exporting the data.

>>> show_menu_path(topics.Tags)
Explorer --> Topics --> Tags

>>> rt.show(topics.Tags)  #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
================ ===========================================
 Topic            Owner
---------------- -------------------------------------------
 (A) Alcoholism   `Arens Andreas <…>`__
 (P) Phobia       `Arens Andreas <…>`__
 (I) Insomnia     `Arens Annette <…>`__
 (A) Alcoholism   `Arens Annette <…>`__
 (P) Phobia       `Ausdemwald Alfons <…>`__
 (I) Insomnia     `Bastiaensen Laurent <…>`__
 (A) Alcoholism   `Bastiaensen Laurent <…>`__
 (P) Phobia       `Chantraine Marc <…>`__
 (I) Insomnia     `Chantraine Marc <…>`__
 (A) Alcoholism   `Collard Charlotte <…>`__
 (P) Phobia       `Collard Charlotte <…>`__
 (I) Insomnia     `Demeulenaere Dorothée <…>`__
 (A) Alcoholism   `Demeulenaere Dorothée <…>`__
 (P) Phobia       `Denon Denis <…>`__
 (I) Insomnia     `Dericum Daniel <…>`__
 (A) Alcoholism   `Dericum Daniel <…>`__
 (P) Phobia       `Dobbelstein-Demeulenaere Dorothée <…>`__
 (I) Insomnia     `Dobbelstein-Demeulenaere Dorothée <…>`__
 (A) Alcoholism   `Eierschal Emil <…>`__
 (P) Phobia       `Eierschal Emil <…>`__
 (I) Insomnia     `Emonts Daniel <…>`__
 (A) Alcoholism   `Emonts Daniel <…>`__
 (P) Phobia       `Emonts Erich <…>`__
 (I) Insomnia     `Emontspool Erwin <…>`__
 (A) Alcoholism   `Emontspool Erwin <…>`__
 (P) Phobia       `Engels Edgar <…>`__
 (I) Insomnia     `Engels Edgar <…>`__
 (A) Alcoholism   `Evers Eberhart <…>`__
 (P) Phobia       `Evers Eberhart <…>`__
 (I) Insomnia     `Evertz Bernd <…>`__
 (A) Alcoholism   `Evertz Bernd <…>`__
 (P) Phobia       `Faymonville Luc <…>`__
 (I) Insomnia     `Groteclaes Gregory <…>`__
 (A) Alcoholism   `Groteclaes Gregory <…>`__
 (P) Phobia       `Hilgers Henri <…>`__
 (I) Insomnia     `Hilgers Henri <…>`__
 (A) Alcoholism   `Ingels Irene <…>`__
 (P) Phobia       `Ingels Irene <…>`__
 (I) Insomnia     `Jacobs Jacqueline <…>`__
 (A) Alcoholism   `Jacobs Jacqueline <…>`__
 (P) Phobia       `Jansen Jérémy <…>`__
 (I) Insomnia     `Johnen Johann <…>`__
 (A) Alcoholism   `Johnen Johann <…>`__
 (P) Phobia       `Jonas Josef <…>`__
 (I) Insomnia     `Jonas Josef <…>`__
 (A) Alcoholism   `Kaivers Karl <…>`__
 (P) Phobia       `Kaivers Karl <…>`__
 (I) Insomnia     `Keller Karl <…>`__
 (A) Alcoholism   `Keller Karl <…>`__
 (P) Phobia       `Lahm Lisa <…>`__
 (I) Insomnia     `Laschet Laura <…>`__
 (A) Alcoholism   `Laschet Laura <…>`__
 (P) Phobia       `Lazarus Line <…>`__
 (I) Insomnia     `Lazarus Line <…>`__
 (A) Alcoholism   `Malmendier Marc <…>`__
 (P) Phobia       `Malmendier Marc <…>`__
 (I) Insomnia     `Martelaer Mark <…>`__
 (A) Alcoholism   `Martelaer Mark <…>`__
 (P) Phobia       `Meessen Melissa <…>`__
 (I) Insomnia     `Mießen Michael <…>`__
 (A) Alcoholism   `Mießen Michael <…>`__
 (P) Phobia       `Radermacher Alfons <…>`__
 (I) Insomnia     `Radermacher Alfons <…>`__
 (A) Alcoholism   `Radermacher Christian <…>`__
 (P) Phobia       `Radermacher Christian <…>`__
 (I) Insomnia     `Radermacher Daniela <…>`__
 (A) Alcoholism   `Radermacher Daniela <…>`__
 (P) Phobia       `Radermacher Edgard <…>`__
 (I) Insomnia     `Radermacher Guido <…>`__
 (A) Alcoholism   `Radermacher Guido <…>`__
 (P) Phobia       `Radermacher Hans <…>`__
 (I) Insomnia     `Radermacher Hans <…>`__
 (A) Alcoholism   `Radermacher Inge <…>`__
 (P) Phobia       `Radermacher Inge <…>`__
 (I) Insomnia     `Radermacher Jean <…>`__
 (A) Alcoholism   `Radermacher Jean <…>`__
 (P) Phobia       `Radermecker Rik <…>`__
 (I) Insomnia     `da Vinci David <…>`__
 (A) Alcoholism   `da Vinci David <…>`__
 (P) Phobia       `di Rupo Didier <…>`__
 (I) Insomnia     `di Rupo Didier <…>`__
 (A) Alcoholism   `Ärgerlich Erna <…>`__
 (P) Phobia       `Ärgerlich Erna <…>`__
 (I) Insomnia     `Õunapuu Õie <…>`__
 (A) Alcoholism   `Õunapuu Õie <…>`__
 (P) Phobia       `Östges Otto <…>`__
================ ===========================================
<BLANKLINE>
