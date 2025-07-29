.. doctest docs/specs/trends.rst
.. include:: /../docs/shared/include/defs.rst
.. _specs.trends:

================================
``trends`` : Managing trends
================================

.. currentmodule:: lino_xl.lib.trends

The :mod:`lino_xl.lib.trends` plugin adds functionality for keeping track of
"trending events" in different "areas".


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *
>>> from django.db.models import Q

Usage
=====

When using this plugin, the application developer should set the
:attr:`Plugin.subject_model` and add :class:`EventsBySubject`
to the detail layout of this model.

Reference
=========


.. class:: TrendArea

    Represents a possible choice for the `trend_area` field of a
    :class:`TrendStage`.

.. class:: TrendStage

  .. attribute:: trend_area

      Pointer to the :class:`TrendArea`.

  .. attribute:: subject_column

      Whether this stage should cause subject column to be added .

      A subject column is a virtual column
      on the :attr:`Plugin.subject_model` that shows
      the date of the first event for a given trend stage and subject.


.. class:: TrendEvent

    .. attribute:: subject

        The subject we are talking about.

    .. attribute:: user

        The user who entered this data.

    .. attribute:: event_date

        The date when the subject reached the stage.

    .. attribute:: trend_area

        Pointer to the :class:`TrendArea`.

    .. attribute:: trend_stage

        Pointer to the :class:`TrendStage`.

    .. attribute:: remark

        A free text field.


.. class:: EventsBySubject

  Shows all trend events of that subject.


.. class:: TrendObservable

  Mixin that should be inherited by the :attr:`Plugin.subject_model` so that
  Lino automatically adds virtual columns for each trend stage having



>>> rt.show(trends.TrendAreas)
========================== ========================== ==========================
 Designation                Designation (de)           Designation (fr)
-------------------------- -------------------------- --------------------------
 Info Integration           Info Integration           Info Integration
 Alphabetisation            Alphabetisation            Alphabetisation
 A1                         A1                         A1
 A2                         A2                         A2
 Citizen course             Citizen course             Citizen course
 Professional integration   Professional integration   Professional integration
========================== ========================== ==========================
<BLANKLINE>

>>> rt.show(trends.TrendStages)
=========== ========================== =================================== =================================== =================================== ================
 Reference   Trend area                 Designation                         Designation (de)                    Designation (fr)                    Subject column
----------- -------------------------- ----------------------------------- ----------------------------------- ----------------------------------- ----------------
             Info Integration           Bilanzgespräch                      Bilanzgespräch                      Bilanzgespräch                      Yes
             Info Integration           Einschreibung in Integrationskurs   Einschreibung in Integrationskurs   Einschreibung in Integrationskurs   No
             Info Integration           Einschreibung in Sprachkurs         Einschreibung in Sprachkurs         Einschreibung in Sprachkurs         No
             Info Integration           Erstgespräch                        Erstgespräch                        Erstgespräch                        Yes
             Info Integration           Sprachtest                          Sprachtest                          Sprachtest                          No
             Alphabetisation            Abgebrochen                         Abgebrochen                         Abgebrochen                         No
             Alphabetisation            Abgeschlossen                       Abgeschlossen                       Abgeschlossen                       No
             Alphabetisation            Ausgeschlossen                      Ausgeschlossen                      Ausgeschlossen                      No
             Alphabetisation            Dispens                             Dispens                             Dispens                             No
             Alphabetisation            Eingeschrieben                      Eingeschrieben                      Eingeschrieben                      No
             A1                         Abgebrochen                         Abgebrochen                         Abgebrochen                         No
             A1                         Abgeschlossen                       Abgeschlossen                       Abgeschlossen                       No
             A1                         Ausgeschlossen                      Ausgeschlossen                      Ausgeschlossen                      No
             A1                         Dispens                             Dispens                             Dispens                             No
             A1                         Eingeschrieben                      Eingeschrieben                      Eingeschrieben                      No
             A2                         Abgebrochen                         Abgebrochen                         Abgebrochen                         No
             A2                         Abgeschlossen                       Abgeschlossen                       Abgeschlossen                       No
             A2                         Ausgeschlossen                      Ausgeschlossen                      Ausgeschlossen                      No
             A2                         Dispens                             Dispens                             Dispens                             No
             A2                         Eingeschrieben                      Eingeschrieben                      Eingeschrieben                      No
             Citizen course             Abgebrochen                         Abgebrochen                         Abgebrochen                         No
             Citizen course             Abgeschlossen                       Abgeschlossen                       Abgeschlossen                       No
             Citizen course             Ausgeschlossen                      Ausgeschlossen                      Ausgeschlossen                      No
             Citizen course             Dispens                             Dispens                             Dispens                             No
             Citizen course             Eingeschrieben                      Eingeschrieben                      Eingeschrieben                      No
             Professional integration   Begleitet vom ADG                   Begleitet vom ADG                   Begleitet vom ADG                   No
             Professional integration   Begleitet vom DSBE                  Begleitet vom DSBE                  Begleitet vom DSBE                  No
             Professional integration   Erwerbstätigkeit                    Erwerbstätigkeit                    Erwerbstätigkeit                    No
=========== ========================== =================================== =================================== =================================== ================
<BLANKLINE>


>>> rt.show(trends.TrendStages, filter=Q(subject_column=True))
=========== ================== ================ ================== ================== ================
 Reference   Trend area         Designation      Designation (de)   Designation (fr)   Subject column
----------- ------------------ ---------------- ------------------ ------------------ ----------------
             Info Integration   Bilanzgespräch   Bilanzgespräch     Bilanzgespräch     Yes
             Info Integration   Erstgespräch     Erstgespräch       Erstgespräch       Yes
=========== ================== ================ ================== ================== ================
<BLANKLINE>

For each trend stage having :attr:`subject_column` checked, Lino adds, in the
:class:`avanti.AllClients <lino_avanti.lib.avanti.AllClients>` table, a virtual
column showing the date of the last event with that trend stage for the given
client. In our example these trend stages are "Bilanzgespräch" and
"Erstgespräch".


>>> rt.login("robin").show(avanti.AllClients)
============ ================= =============== ========================== ========================== ============= ========== ============= ========== ======== =============== ======================== =================== ================= ================ =================== =================== =================== ================= ==================== ============== ================
 State        Starting reason   Ending reason   Locality                   Municipality               Country       Zip code   Nationality   Age        Gender   Birth country   Lives in Belgium since   Needs work permit   Translator type   Mother tongues   cef_level_de        cef_level_fr        cef_level_en        Primary coach     Recurrency policy    Erstgespräch   Bilanzgespräch
------------ ----------------- --------------- -------------------------- -------------------------- ------------- ---------- ------------- ---------- -------- --------------- ------------------------ ------------------- ----------------- ---------------- ------------------- ------------------- ------------------- ----------------- -------------------- -------------- ----------------
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     16 years   Male                                              No                  SETIS             Dutch            Not specified       Not specified       Not specified       nathalie          Every month          30/07/2016
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     20 years   Female                                            No                  Other             English          Not specified       Not specified       Not specified       Romain Raffault   Every 2 weeks
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     22 years   Male                                              No                  Other             French           A1+ (Certificate)   Not specified       Not specified       Rolf Rompen       Other
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     24 years   Male                                              No                  Other             English          Not specified       Not specified       Not specified       Robin Rood        Every 2 months
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     26 years   Male                                              No                  SETIS             French           Not specified       Not specified       Not specified       nathalie          Every 3 months
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     31 years   Female                                            No                  Other             German           Not specified       Not specified       C1 (Certificate)    Rolf Rompen       Every 2 months
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     33 years   Male                                              No                  SETIS             French           Not specified       Not specified       Not specified       Robin Rood        Every 3 months       27/08/2016
 Registered                                     Amsterdam                  Amsterdam                  Netherlands                            37 years   Male                                              No                  Other             German           Not specified       Not specified       Not specified       Romain Raffault   Every 2 months
 Registered                                     4730 Raeren                4730 Raeren                Belgium       4730                     39 years   Male                                              No                  SETIS             English          Not specified       A2+ (Certificate)   Not specified       Rolf Rompen       Every 3 months
 Registered                                     4730 Raeren                4730 Raeren                Belgium       4730                     44 years   Male                                              No                  Other             German           Not specified       Not specified       Not specified       Romain Raffault   Every 2 months
 Registered                                     4730 Raeren                4730 Raeren                Belgium       4730                     46 years   Male                                              No                  SETIS             English          Not specified       Not specified       Not specified       Rolf Rompen       Every 3 months       24/09/2016
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     18 years   Male                                              No                  SETIS             Estonian         C1 (Certificate)    B2+ (Certificate)   Not specified       nathalie          Every 3 months                      28/09/2016
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     28 years   Male                                              No                  SETIS             English          Not specified       Not specified       Not specified       nathalie          Once after 10 days
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     30 years   Female                                            No                  SETIS             Estonian         Not specified       A1 (Certificate)    Not specified       nelly             Every month
 Registered                                     Aachen / Aix-la-Chapelle   Aachen / Aix-la-Chapelle   Germany                                35 years   Female                                            No                  SETIS             German           Not specified       Not specified       A2+                 Robin Rood        Once after 10 days                  26/10/2016
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     17 years   Female                                            No                  Private           Estonian         Not specified       B2                  Not specified       nathalie          Every 2 months
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     36 years   Female                                            No                  Private           German           Not specified       Not specified       Not specified       Rolf Rompen       Every month
 Registered                                     4730 Raeren                4730 Raeren                Belgium       4730                     41 years   Male                                              No                  SETIS             Dutch            Not specified       C2+ (Certificate)   B2+ (Certificate)   nelly             Once after 10 days
 Registered                                     4730 Raeren                4730 Raeren                Belgium       4730                     43 years   Female                                            No                  SETIS             German           Not specified       Not specified       Not specified       Romain Raffault   Every month          19/11/2016
 Registered                                     4730 Raeren                4730 Raeren                Belgium       4730                     48 years   Male                                              No                  SETIS             Dutch            Not specified       Not specified       A1                  nathalie          Once after 10 days
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     27 years   Male                                              No                  Other             Estonian         A2+ (Certificate)   A1+ (Certificate)   Not specified       Rolf Rompen       Every 2 weeks
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     29 years   Male                                              No                  Other             Dutch            Not specified       Not specified       B2                  Robin Rood        Other
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     unknown    Female                                            No                  SETIS             Estonian         Not specified       Not specified       Not specified       nelly             Once after 10 days   17/12/2016
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     34 years   Male                                              No                  Private           French           B2+ (Certificate)   Not specified       C2+ (Certificate)   Rolf Rompen       Every 2 weeks                       21/12/2016
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     36 years   Female                                            No                  Other             Estonian         Not specified       Not specified       Not specified       Robin Rood        Other
 Registered                                     4700 Eupen                 4700 Eupen                 Belgium       4700                     unknown    Female                                            No                  Private           French           A1 (Certificate)    Not specified       Not specified       nathalie          Every month
 Registered                                     4730 Raeren                4730 Raeren                Belgium       4730                     40 years   Male                                              No                  Other             Dutch            Not specified       Not specified       A1+ (Certificate)   Rolf Rompen       Every 2 weeks
 Registered                                     4730 Raeren                4730 Raeren                Belgium       4730                     42 years   Male                                              No                  Other             French           B2 (Certificate)    Not specified       Not specified       Robin Rood        Other
 Registered                                     4730 Raeren                4730 Raeren                Belgium       4730                     47 years   Female                                            No                  Private           Dutch            Not specified       Not specified       Not specified       Romain Raffault   Every 2 weeks                       18/01/2017
============ ================= =============== ========================== ========================== ============= ========== ============= ========== ======== =============== ======================== =================== ================= ================ =================== =================== =================== ================= ==================== ============== ================
<BLANKLINE>
