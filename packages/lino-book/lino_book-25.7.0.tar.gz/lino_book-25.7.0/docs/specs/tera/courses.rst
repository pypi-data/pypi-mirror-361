.. doctest docs/specs/tera/courses.rst
.. _tera.specs.courses:

=========
Therapies
=========

This document specifies how the :mod:`lino_xl.lib.courses` plugin is
being used in :ref:`tera`.

Activities in :ref:`tera` are called "therapies". There are individual
therapies, "life groups" (families and similar groups who live
together or have lived together) and "therapeutical groups" (groups of
indipendent clients who share a common interest).


.. contents::
  :local:


.. currentmodule:: lino_tera.lib.courses


.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.tera1.settings')
>>> from lino.api.doctest import *

>>> dd.plugins.courses
<lino_tera.lib.courses.Plugin lino_tera.lib.courses>

>>> dd.plugins.courses.__class__.__bases__
(<class 'lino_xl.lib.courses.Plugin'>,)


The detail view of a therapy
============================

>>> print(py2rst(courses.Activities.detail_layout))
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
(main) [visible for all]:
- **General** (general):
  - (general_1): **Reference** (ref), **Designation** (name), **Invoice recipient** (partner), **Invoiceable fee** (invoiceable_fee)
  - (general_2): **Manager** (user), **Therapist** (teacher), **Dossier type** (line)
  - (general_3): **ID** (id), **Print** (print_actions), **Workflow** (workflow_buttons)
  - **Enrolments** (EnrolmentsByCourse) [visible for secretary therapist admin]
- **Therapy** (therapy):
  - (therapy_1): **Therapy domain** (therapy_domain), **Procurer** (procurer), **Mandatory** (mandatory), **Translator type** (translator_type)
  - (therapy_2): **Healthcare plan** (healthcare_plan), **Ending reason** (ending_reason)
  - (therapy_3) [visible for therapist admin]: **Tags** (topics.TagsByOwner), **Notes** (notes.NotesByProject)
- **Appointments** (calendar):
  - (calendar_1): **Recurrence** (every_unit), **Repeat every** (every), **Generate events until** (max_date), **Number of events** (max_events)
  - (calendar_2): **Room** (room), **Start date** (start_date), **End Date** (end_date), **Start time** (start_time), **End Time** (end_time)
  - (calendar_3): **Monday** (monday), **Tuesday** (tuesday), **Wednesday** (wednesday), **Thursday** (thursday), **Friday** (friday), **Saturday** (saturday), **Sunday** (sunday)
  - **Calendar entries** (courses.EntriesByCourse) [visible for secretary therapist admin]
- **Invoicing** (invoicing_2) [visible for secretary therapist admin]:
  - **Invoicings** (trading.InvoiceItemsByGenerator) [visible for secretary admin]
  - **Existing excerpts** (excerpts.ExcerptsByProject)
- **More** (more): **Division** (team), **Remark** (remark), **Tasks** (cal.TasksByProject) [visible for secretary therapist admin]
<BLANKLINE>


Note in particular that topic interests and notes are not visible to
secretary:

>>> show_permissions(topics.TagsByOwner)
therapist admin

>>> show_permissions(notes.NotesByProject)
therapist admin





Activity lines and activity layouts
===================================

In :ref:`tera` the  :class:`lino_xl.lib.courses.ActivityLayouts` choicelist is
populated with the following activity layouts:

>>> rt.show(courses.ActivityLayouts)
======= ============= ====================== =====================
 value   name          text                   Table
------- ------------- ---------------------- ---------------------
 IT      therapies     Individual therapies   courses.Therapies
 LG      life_groups   Life groups            courses.LifeGroups
 OG      default       Other groups           courses.OtherGroups
======= ============= ====================== =====================
<BLANKLINE>



While in Voga or Avanti we can have many course lines, in Lino Tera
there is only one course line per course layout.

>>> print(courses.Line._meta.verbose_name_plural)
Dossier types

Every course line knows which its layout.

>>> rt.show(courses.Lines)
=========== ====================== ================== ================== ====================== ============== ===================== ===================
 Reference   Designation            Designation (de)   Designation (fr)   Layout                 Service type   Manage presences as   Invoicing policy
----------- ---------------------- ------------------ ------------------ ---------------------- -------------- --------------------- -------------------
             Individual therapies                                         Individual therapies                  Attendee              By calendar event
             Life groups                                                  Life groups                           Attendee              By calendar event
             Other groups                                                 Other groups                          Attendee              By calendar event
=========== ====================== ================== ================== ====================== ============== ===================== ===================
<BLANKLINE>

Some table views use a given fixed activity layout, some don't.

>>> courses.LifeGroups.activity_layout
'life_groups'

>>> print(courses.AllActivities.activity_layout)
None

When you are in a table with a fixed layout, your choices for the
:attr:`Course.line` field are limited to lines of that layout.

>>> show_choices("robin", "/choices/courses/LifeGroups/line")
<br/>
Life groups

>>> show_choices("robin", "/choices/courses/AllActivities/line")
<br/>
Individual therapies
Life groups
Other groups

Furthermore, when you are in a table with a fixed layout *and there is
only one line object having that layout*, Lino fills the line field
automatically when creating a new course.


>>> fld = courses.Course._meta.get_field('line')
>>> print(fld.verbose_name)
Dossier type

>>> fld.blank
False
