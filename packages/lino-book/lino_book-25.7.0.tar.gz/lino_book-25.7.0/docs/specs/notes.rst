.. doctest docs/specs/notes.rst
.. _specs.notes:

================
``notes``: Notes
================

The :mod:`lino_xl.lib.niotes` plugin adds a multipurpose concept of
**notes**.

Examples in this document have been tested against the
:mod:`lino_book.projects.cosi2` demo project.

>>> from lino_book.projects.cosi2.startup import *


.. contents::
   :depth: 1
   :local:




Notes
=====


.. class:: Note

    A **note** is a dated and timed document written by its author (a
    user). For example a report of a meeting or a phone call, or just
    some observation.  Notes are usually meant for internal use.

    .. attribute:: date
    .. attribute:: time
    .. attribute:: type

      The type of note.

    .. attribute:: event_type

      The type of the event that this note means.

    .. attribute:: subject
    .. attribute:: body
    .. attribute:: language


Note types
==========

Im Web-Interface unter :menuselection:`Configure --> Note Types` müssen die
Notizarten definiert werden.


.. class:: NoteType

    .. attribute:: name
    .. attribute:: important
    .. attribute:: remark
    .. attribute:: special_type

    .. attribute:: print_method

      Wenn dieses Feld leer ist, kann eine Notiz dieser Art nur am Bildschirm
      konsultiert werden und ist nicht druckbar.

      In der Auswahlliste stehen zwar weitere Methoden, aber funktionieren tut
      bis auf weiteres nur die Methode AppyPrintMethod.

    .. attribute:: template

      Wenn eine Druckmethode angegeben ist, muss außerdem im Feld `template`
      eine Vorlagedatei ausgewählt werden.

    .. attribute:: body_template

      An optional template that will be rendered into the `body` variable.



.. class:: EventType

    A possible choice for :attr:`Note.event_type`.

    .. attribute:: remark
    .. attribute:: body



.. class:: NoteTypes


Choicelists
===========

.. class:: SpecialTypes

    The list of special note types which have been declared on this
    Site.


.. class:: SpecialType

    Represents a special note type.
