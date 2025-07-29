.. _dev.xl:

======================
About plugin libraries
======================

.. contents::
   :depth: 1
   :local:


Glossary
========

.. glossary::

  Lino core

    A :term:`source repository` containing core functionality of the Lino
    framework. Used by every :term:`Lino application`.

  XL

    Abbreviation for :term:`Lino Extensions Library`.

  Lino Extensions Library

    A :term:`plugin library` with shared plugins that are  maintained by
    Synodalsoft, considered part of the :ref:`Lino framework <lf>` and used by
    many  :term:`Lino applications <Lino application>`.

  plugin library

    A collection of :term:`plugins <plugin>` grouped into a single :term:`source
    repository`, designed to work together and maintained by a given
    :term:`development provider`.

    Examples of plugin libraries:
    :mod:`lino.modlib`, :mod:`lino_xl.lib`, :mod:`lino_noi.lib`,
    :mod:`lino_voga.lib`, :mod:`lino_welfare.modlib`.



"Core" versus "Extensions" library
======================================

The plugins of the Lino framework are spread over several Python packages. Some
of them are in :mod:`lino.modlib`  and we call them :ref:`core plugins
<specs.core>`, others are in :mod:`lino_xl` and we call them the :ref:`plugins
of the Extension Library <specs.xl>`. Furthermore, individual applications can
have their own plugin library.

The XL is separate from the :doc:`/specs/modlib` because  despite our efforts of
making it very reusable, it is still just *one* possible view of the world and
you might prefer your own view.

It is *a big library*, so beginners might not want to dive into all these
concepts right now.

Where is the borderline between a standard plugin and an "XL" plugin?  The
theoretical answer is that the :doc:`/specs/modlib` contains "basic features"
that remain useful also for people who don't want the XL.

The borderline is neither very clear nor definitive. For example we have two
plugins :mod:`printing <lino.modlib.printing>` and :mod:`excerpts
<lino_xl.lib.excerpts>`.  The former in the core (:mod:`lino.modlib`) while the
latter is in :mod:`lino_xl.lib`. Yes, it remains arbitrary choice.

TODO: move ``languages`` and ``office`` to the XL?  Move ``excerpts`` to the
core? And what about ``vocbook``?
