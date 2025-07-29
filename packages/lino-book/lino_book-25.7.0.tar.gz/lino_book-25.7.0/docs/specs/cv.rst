.. doctest docs/specs/cv.rst
.. _lino.tested.cv:

================================================
``cv`` : Managing career-related data of clients
================================================

.. currentmodule:: lino_xl.lib.cv

The :mod:`lino_xl.lib.cv` plugin adds functionality for managing career-related
information about a client which can be used for example to generate a CV (a
*curriculum vitae*).

.. contents::
   :depth: 1
   :local:


Concepts
========

.. glossary::

  language knowledge

    The fact that a given person knows a given language at a given degree.

    Stored in the :class:`LanguageKnowledge` database model.

  education entry

    A period of time where a given person has received education of a given type
    in a given establishment.  There are two basic classes of education entries:
    :term:`study entries <study entry>` and
    :term:`training entries <training entry>`.

    fr: Éducation, de: Bildung

    Stored in models that inherit from the :class:`EducationEntry` mixin.

  work experience

    A period of time where a given person has been working in a given
    :term:`organization`.

    fr: Expérience professionnelle, de: Berufserfahrung


  study entry

    An :term:`education entry` with mostly theoretical lessons.

    fr: Études, de: Studium


  training entry

    An :term:`education entry` with more practical work than theoretical
    lessons. There is no school.

    fr: Formation, de: Ausbildung

  education type

    A type of education.  See `Education types`.

    Stored in a model called :class:`StudyType` for historical reasons.

  work status

    The legal status of a :term:`work experience`. Stored in :class:`Status`.

  work regime

    The number of hours per week of a :term:`work experience`.  Stored in
    :class:`Regime`.

  contract duration

    The duration of the contract of a :term:`work experience`. Stored in
    :class:`Duration`.

  job title

    Stored in :class:`Function`.

  activity sector

    Stored in :class:`Sector`.


.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.min9.settings')
>>> from lino.api.doctest import *

Studies, trainings and work experiences
=======================================

.. class:: Study

    Django model representing a :term:`study entry`.

    .. attribute:: education_level

      Pointer to :class:`EducationLevel`.

    .. attribute:: content

      Free-text description of the content.


.. class:: Training

    Django model representing a :term:`training entry`.

    .. attribute:: content

       Describes the content of this training. A free one-line text field.


.. class:: Experience

    Django model representing a :term:`work experience`.




>>> UserTypes = rt.models.users.UserTypes
>>> AllLanguageKnowledges = rt.models.cv.AllLanguageKnowledges

>>> a = UserTypes.admin
>>> a
<users.UserTypes.admin:900>

>>> u = UserTypes.user
>>> u
<users.UserTypes.user:100>

>>> AllLanguageKnowledges.required_roles == {cv.CareerStaff}
True

>>> AllLanguageKnowledges.default_action.get_view_permission(u)
False

>>> AllLanguageKnowledges.default_action.get_view_permission(a)
False



.. class:: LanguageKnowledge

  Django model to represent a :term:`language knowledge`.

  .. attribute:: person

    The person to which this entry applies.

  .. attribute:: language

    The language to which this entry applies.

  .. attribute:: spoken
  .. attribute:: written
  .. attribute:: spoken_passively
  .. attribute:: written_passively
  .. attribute:: native
  .. attribute:: cef_level

    The CEF level. A pointer to a choice of :class:`CefLevels`

  .. attribute:: has_certificate

    Whether this entry is confirmed by a certificate.

  .. attribute:: entry_date

    When this entry was created.


Education types
===============

Lino has a configurable list of :term:`education types <education type>`  that
can be used to group :term:`education entries <education entry>` according to
their type.


.. class:: StudyType

    Django model representing an :term:`education type`.

    TODO: Rename this to `EducationType`.

    Also used in :attr:`isip.Contract.study_type
    <lino_welfare.modlib.isip.models.Contract.study_type>` and by
    :attr:`EducationEntry.type`.

    .. attribute:: education_level

        Pointer to :class:`EducationLevel`.

    .. attribute:: study_regime

        Pointer to :class:`StudyRegimes`.

    Inherits from :class:`StudyOrTraining`.

>>> rt.show(cv.StudyTypes)
==== ================= ==================== ======================= ======= ========== =================
 ID   Designation       Designation (de)     Designation (fr)        Study   Training   Education Level
---- ----------------- -------------------- ----------------------- ------- ---------- -----------------
 11   Alpha             Alpha                Alpha                   No      Yes
 4    Apprenticeship    Lehre                Apprentissage           Yes     No
 5    Highschool        Hochschule           École supérieure        Yes     No
 7    Part-time study   Teilzeitunterricht   Cours à temps partiel   Yes     No
 9    Prequalifying     Prequalifying        Préqualification        No      Yes
 10   Qualifying        Qualifying           Qualification           No      Yes
 8    Remote study      Fernkurs             Cours à distance        Yes     No
 1    School            Schule               École                   Yes     No
 2    Special school    Sonderschule         École spéciale          Yes     No
 3    Training          Ausbildung           Formation               Yes     No
 6    University        Universität          Université              Yes     No
==== ================= ==================== ======================= ======= ========== =================
<BLANKLINE>


Education levels
================


.. class:: EducationLevel

    Inherits from :class:`StudyOrTraining`

>>> rt.show(cv.EducationLevels)
============= ================== ================== ======= ==========
 Designation   Designation (de)   Designation (fr)   Study   Training
------------- ------------------ ------------------ ------- ----------
 Bachelor      Bachelor           Bachelor           Yes     No
 Higher        Hochschule         Supérieur          Yes     No
 Master        Master             Master             Yes     No
 Primary       Primär             Primaire           Yes     No
 Secondary     Sekundär           Secondaire         Yes     No
============= ================== ================== ======= ==========
<BLANKLINE>



.. class:: Status

    Django model representing a :term:`work status`.

>>> rt.show(cv.Statuses)
==== ============= ================== ==================
 ID   Designation   Designation (de)   Designation (fr)
---- ------------- ------------------ ------------------
 2    Employee      Angestellter       Employé
 3    Freelancer    Selbstständiger    Indépendant
 7    Interim       Interim            Intérim
 6    Laboratory    Laboratory         Stage
 5    Student       Student            Étudiant
 4    Voluntary     Ehrenamtlicher     Bénévole
 1    Worker        Arbeiter           Ouvrier
==== ============= ================== ==================
<BLANKLINE>


.. class:: Regime

    Django model representing a :term:`work regime`.

>>> rt.show(cv.Regimes)
==== ============= ================== ==================
 ID   Designation   Designation (de)   Designation (fr)
---- ------------- ------------------ ------------------
 1    Full-time     Vollzeit           Temps-plein
 3    Other         Sonstige           Autre
 2    Part-time     Teilzeit           Temps partiel
==== ============= ================== ==================
<BLANKLINE>


.. class:: Duration

    Django model representing a :term:`contract duration`.

>>> rt.show(cv.Durations)
==== ===================== ===================== ==========================
 ID   Designation           Designation (de)      Designation (fr)
---- --------------------- --------------------- --------------------------
 3    Clearly defined job   Clearly defined job   Travail nettement défini
 5    Interim               Interim               Intérim
 2    Limited duration      Beschränkte Dauer     Durée déterminée
 4    Replacement           Ersatz                Contrat de remplacement
 1    Unlimited duration    Unbeschränkte Dauer   Durée indéterminée
==== ===================== ===================== ==========================
<BLANKLINE>


.. class:: Sector

    Django model representing an :term:`activity sector`.

.. class:: Function

    Django model representing a :term:`job title`.

For data examples see the specs of :ref:`welfare`.

Model mixins
============

.. class:: StudyOrTraining

    Model mixin inherited by :class:`EducationLevel` and :class:`StudyType`.

    .. attribute:: is_study

      Whether education entries are considered a :term:`study entry`.

    .. attribute:: is_training

      Whether education entries are considered a :term:`training entry`.


.. class:: PersonHistoryEntry

    Base class for :class:`Study`, :class:`Training` and :class:`Experience`.

    Inherits from :class:`lino.mixins.period.DateRange`.

    .. attribute:: person

      The person to whom this entry applies.
      Pointer to :attr:`Plugin.person_model`.

    .. attribute:: start_date

      When this entry started.


    .. attribute:: end_date

      When this entry ended.

    .. attribute:: duration_text

      Free-text description of the duration of this entry.

.. class:: EducationEntry

    Model mixin to represent an :term:`education entry`.
    Inherited by :class:`Training` and :class:`Study`.

    .. attribute:: language

      Foreign key to :class:`lino.modlib.languages.Language`.

    .. attribute:: school

      The establishment where the education happened.

    .. attribute:: state = EducationEntryStates.field(blank=True)

      Choicelist field to :class:`EducationEntryStates`.

    .. attribute:: remarks

      Remarks about this entry.

    .. attribute:: type

      Pointer to :class:`StudyType`.

.. class:: BiographyOwner

  Model mixin usually inherited by the :attr:`Plugin.person_model`. It adds a
  few virtual fields.

  .. attribute:: language_knowledge

    A summary of the :term:`language knowledges <language knowledge>` of this
    person.

  .. attribute:: mother_tongues

  .. attribute:: cef_level_en
  .. attribute:: cef_level_de
  .. attribute:: cef_level_fr


ChoiceLists
===========

.. class:: HowWell

    A list of possible answers to questions of type "How well ...?":
    "not at all", "a bit", "moderate", "quite well" and "very well"
    which are stored in the database as '0' to '4',
    and whose `__str__()` returns their translated text.

>>> rt.show(cv.HowWell)
======= ========= ============
 value   name      text
------- --------- ------------
 0                 not at all
 1                 a bit
 2       default   moderate
 3                 quite well
 4                 very well
======= ========= ============
<BLANKLINE>


.. class:: CefLevel

    Levels of the `Common European Framework of Reference (CEFR) for Languages
    <https://en.wikipedia.org/wiki/Common_European_Framework_of_Reference_for_Languages>`__.

>>> rt.show(cv.CefLevel)
======= ====== ======
 value   name   text
------- ------ ------
 A0             A0
 A1             A1
 A1+            A1+
 A2             A2
 A2+            A2+
 B1             B1
 B2             B2
 B2+            B2+
 C1             C1
 C2             C2
 C2+            C2+
======= ====== ======
<BLANKLINE>


See also

- `Council of Europe Language Policy Portal <https://www.coe.int/en/web/language-policy/home>`__
- `Mapping IELTS to CEF <https://ielts.org/organisations/ielts-for-organisations/compare-ielts/ielts-and-the-cefr>`__



.. class:: EducationEntryStates

    The possible states of an :term:`education entry`.

>>> rt.show(cv.EducationEntryStates)
======= ========= =========
 value   name      text
------- --------- ---------
 0       success   Success
 1       failure   Failure
 2       ongoing   Ongoing
======= ========= =========
<BLANKLINE>



Tables
======

.. class:: HistoryByPerson

    Table mixin for :class:`StudiesByPerson` and :class:`ExperiencesByPerson`.

    Makes the start_date of a new entry automatically default to the end_date of
    the previous entry.


.. class:: SectorFunction

    Model mixin for entries that refer to a
    :class:`Sector` and a :class:`Function`.

    .. attribute:: sector

      Pointer to the :class:`Sector`.

    .. attribute:: function

      Pointer to the :class:`Function`.
