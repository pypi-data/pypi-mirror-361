.. doctest docs/topics/show.rst
.. _dg.topics.show:

=========================
The ``show()`` function
=========================

This documents shows how to use the :meth:`ar.show
<lino.core.requests.BaseRequest.show>` method.


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *


>>> rt.login('robin').show(cal.EntryStates)
======= ============ ============ ============= ============= ======== ============= =========
 value   name         text         Button text   Fill guests   Stable   Transparent   No auto
------- ------------ ------------ ------------- ------------- -------- ------------- ---------
 10      suggested    Suggested    ?             Yes           No       No            No
 20      draft        Draft        ☐             Yes           No       No            No
 50      took_place   Took place   ☑             No            Yes      No            No
 70      cancelled    Cancelled    ☒             No            Yes      Yes           Yes
======= ============ ============ ============= ============= ======== ============= =========
<BLANKLINE>

>>> rt.show(cal.EntryStates)
======= ============ ============ ============= ============= ======== ============= =========
 value   name         text         Button text   Fill guests   Stable   Transparent   No auto
------- ------------ ------------ ------------- ------------- -------- ------------- ---------
 10      suggested    Suggested    ?             Yes           No       No            No
 20      draft        Draft        ☐             Yes           No       No            No
 50      took_place   Took place   ☑             No            Yes      No            No
 70      cancelled    Cancelled    ☒             No            Yes      Yes           Yes
======= ============ ============ ============= ============= ======== ============= =========
<BLANKLINE>


>>> rt.show(courses.Topics)
==== ================== ================== ==================
 ID   Designation        Designation (de)   Designation (fr)
---- ------------------ ------------------ ------------------
 1    Citizen course     Citizen course     Citizen course
 2    Language courses   Language courses   Language courses
==== ================== ================== ==================
<BLANKLINE>

>>> rt.show(courses.Topics, show_links=True)
=========== ================== ================== ==================
 ID          Designation        Designation (de)   Designation (fr)
----------- ------------------ ------------------ ------------------
 `1 <…>`__   Citizen course     Citizen course     Citizen course
 `2 <…>`__   Language courses   Language courses   Language courses
=========== ================== ================== ==================
<BLANKLINE>

>>> rt.show(courses.Topics, show_urls=True)
================================= ================== ================== ==================
 ID                                Designation        Designation (de)   Designation (fr)
--------------------------------- ------------------ ------------------ ------------------
 `1 </#/api/courses/Topics/1>`__   Citizen course     Citizen course     Citizen course
 `2 </#/api/courses/Topics/2>`__   Language courses   Language courses   Language courses
================================= ================== ================== ==================
<BLANKLINE>

Links in `displayfield` columns are shown even when `show_links` is not
specified (that's actually a bug but nobody has complained about it so far):

>>> language_courses = courses.Topic.objects.get(pk=2)
>>> rt.show(courses.ActivitiesByTopic, language_courses)
====================================== =========== ============= ================== =========== ============= =========== ========
 Activity                               When        Times         Available places   Confirmed   Free places   Requested   Trying
-------------------------------------- ----------- ------------- ------------------ ----------- ------------- ----------- --------
 `Alphabetisation (16/01/2017) <…>`__   Every day   09:00-12:00   5                  3           0             3           2
 `Alphabetisation (16/01/2017) <…>`__   Every day   14:00-17:00   15                 2           0             4           13
 `Alphabetisation (16/01/2017) <…>`__   Every day   18:00-20:00   15                 12          0             11          3
 **Total (3 rows)**                                               **35**             **17**      **0**         **18**      **18**
====================================== =========== ============= ================== =========== ============= =========== ========
<BLANKLINE>


>>> rt.show(courses.LinesByTopic, language_courses)
==================== ====================== ====================== ====================== ================== ============ ===================== ===================== ============ ==============
 Reference            Designation            Designation (de)       Designation (fr)       Topic              Layout       Calendar entry type   Manage presences as   Recurrency   Repeat every
-------------------- ---------------------- ---------------------- ---------------------- ------------------ ------------ --------------------- --------------------- ------------ --------------
                      Alphabetisation        Alphabetisation        Alphabetisation        Language courses   Activities   Lesson                Pupil                 weekly       1
                      German A1+             German A1+             German A1+             Language courses   Activities   Lesson                Pupil                 weekly       1
                      German A2              German A2              German A2              Language courses   Activities   Lesson                Pupil                 weekly       1
                      German A2 (women)      German A2 (women)      German A2 (women)      Language courses   Activities   Lesson                Pupil                 weekly       1
                      German for beginners   German for beginners   German for beginners   Language courses   Activities   Lesson                Pupil                 weekly       1
 **Total (5 rows)**                                                                                                                                                                 **5**
==================== ====================== ====================== ====================== ================== ============ ===================== ===================== ============ ==============
<BLANKLINE>

The :func:`show` function does not check whether the user has permission to see
the specified actor because this test makes no sense in a script or a doctest.
For example, the following two examples get the same result:

>>> rt.show(courses.AllActivities, show_links=True)
========================= ============ ======================= ================== =========== =============
 Activity line             Start date   Instructor              Author             When        Times
------------------------- ------------ ----------------------- ------------------ ----------- -------------
 `Alphabetisation <…>`__   16/01/2017   `Laura Lieblig <…>`__   `nelly <…>`__      Every day   18:00-20:00
 `Alphabetisation <…>`__   16/01/2017   `Laura Lieblig <…>`__   `nathalie <…>`__   Every day   14:00-17:00
 `Alphabetisation <…>`__   16/01/2017   `Laura Lieblig <…>`__   `martina <…>`__    Every day   09:00-12:00
========================= ============ ======================= ================== =========== =============
<BLANKLINE>

>>> rt.login('robin').show(courses.AllActivities, show_links=True)
========================= ============ ======================= ================== =========== =============
 Activity line             Start date   Instructor              Author             When        Times
------------------------- ------------ ----------------------- ------------------ ----------- -------------
 `Alphabetisation <…>`__   16/01/2017   `Laura Lieblig <…>`__   `nelly <…>`__      Every day   18:00-20:00
 `Alphabetisation <…>`__   16/01/2017   `Laura Lieblig <…>`__   `nathalie <…>`__   Every day   14:00-17:00
 `Alphabetisation <…>`__   16/01/2017   `Laura Lieblig <…>`__   `martina <…>`__    Every day   09:00-12:00
========================= ============ ======================= ================== =========== =============
<BLANKLINE>

But for certain tables there is a difference between being signed in or not.
For example when the table needs to know the user.

>>> rt.show(courses.MyCoursesGiven)  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
Error while executing <ActionRequest courses.MyCoursesGiven.grid({'known_values':
{'teacher': <lino.core.auth.utils.AnonymousUser object at ...>}, 'user': 'anonymous'})>:
Field 'id' expected a number but got <lino.core.auth.utils.AnonymousUser object at ...>.
(Subsequent warnings will be silenced.)
Field 'id' expected a number but got <lino.core.auth.utils.AnonymousUser object at ...>.
(set catch_layout_exceptions to see details)

>>> rt.login('laura').show(courses.MyCoursesGiven)
... #doctest: +NORMALIZE_WHITESPACE -REPORT_UDIFF
============ ====================================== =========== ============= ====== =============
 Start date   Activity                               When        Times         Room   Workflow
------------ -------------------------------------- ----------- ------------- ------ -------------
 16/01/2017   `Alphabetisation (16/01/2017) <…>`__   Every day   09:00-12:00          **Started**
 16/01/2017   `Alphabetisation (16/01/2017) <…>`__   Every day   14:00-17:00          **Started**
 16/01/2017   `Alphabetisation (16/01/2017) <…>`__   Every day   18:00-20:00          **Started**
============ ====================================== =========== ============= ====== =============
<BLANKLINE>


>>> obj = courses.Course.objects.get(pk=1)
>>> rt.login('laura').show('cal.EntriesByController', obj)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF +ELLIPSIS
February 2017: `Fri 24. <…>`__? `Thu 23. <…>`__? `Tue 21. <…>`__? `Mon 20. <…>`__? `Fri 17. <…>`__? `Thu 16. <…>`__? `Tue 14. <…>`__? `Mon 13. <…>`__? `Fri 10. <…>`__? `Thu 09. <…>`__? `Tue 07. <…>`__☑ `Mon 06. <…>`__☑ `Fri 03. <…>`__☒ `Thu 02. <…>`__☑
January 2017: `Tue 31. <…>`__☑ `Mon 30. <…>`__☑ `Fri 27. <…>`__☑ `Thu 26. <…>`__☑ `Tue 24. <…>`__☑ `Mon 23. <…>`__☑ `Fri 20. <…>`__☑ `Thu 19. <…>`__☒ `Tue 17. <…>`__☑ `Mon 16. <…>`__☑
Suggested : 10 ,  Draft : 0 ,  Took place : 12 ,  Cancelled : 2 **New**


Even though Nathalie is author of the morning course, it is Laura (the teacher)
who is responsible for the individual events.

>>> rt.login('laura').show('cal.MyEntries')
... #doctest: +NORMALIZE_WHITESPACE -REPORT_UDIFF +ELLIPSIS
====================================== ======== ===================================
 Calendar entry                         Client   Workflow
-------------------------------------- -------- -----------------------------------
 `Lesson 19 (16.02.2017 09:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 19 (16.02.2017 14:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 19 (16.02.2017 18:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 20 (17.02.2017 09:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 20 (17.02.2017 14:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 20 (17.02.2017 18:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 21 (20.02.2017 09:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 21 (20.02.2017 14:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 21 (20.02.2017 18:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 22 (21.02.2017 09:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 22 (21.02.2017 14:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 22 (21.02.2017 18:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 23 (23.02.2017 09:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 23 (23.02.2017 14:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 23 (23.02.2017 18:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 24 (24.02.2017 09:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 24 (24.02.2017 14:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
 `Lesson 24 (24.02.2017 18:00) <…>`__            [▽] **? Suggested** → [☐] [☑] [☒]
====================================== ======== ===================================
<BLANKLINE>



>>> rt.show(courses.ReminderStates)
======= =========== =========== =============
 value   name        text        Button text
------- ----------- ----------- -------------
 10      draft       Draft
 20      sent        Sent
 30      ok          OK
 40      final       Final
 90      cancelled   Cancelled
======= =========== =========== =============
<BLANKLINE>


>>> rt.login("romain").show(courses.DitchingEnrolments)
============== ================================ ============================== =================
 Missing rate   Participant                      Activity                       Primary coach
-------------- -------------------------------- ------------------------------ -----------------
 54,17          ABID Abdul Báásid (63/romain)    Alphabetisation (16/01/2017)   Romain Raffault
 54,17          CISSE Chátá (51/romain)          Alphabetisation (16/01/2017)   Romain Raffault
 50,00          BEK-MURZIN Agápiiá (61/romain)   Alphabetisation (16/01/2017)   Romain Raffault
============== ================================ ============================== =================
<BLANKLINE>



>>> obj = courses.Course.objects.get(pk=1)
>>> rt.login('rolf').show('courses.EnrolmentsByCourse', obj, show_urls=True)
... #doctest: +NORMALIZE_WHITESPACE -REPORT_UDIFF
================================================================= ======== ============= ========== =========== ======== ============== ================================================== ==============
 Participant                                                       Gender   Nationality   Age        Childcare   Remark   Missing rate   Workflow                                           Municipality
----------------------------------------------------------------- -------- ------------- ---------- ----------- -------- -------------- -------------------------------------------------- --------------
 `ARNOLD Alexei (30/nathalie) </#/api/avanti/Clients/30>`__        Male                   28 years   No                   50,00          **Confirmed** → [Cancelled] [Requested] [Trying]   4700 Eupen
 `ABDELNOUR Aámir (26/nelly) </#/api/avanti/Clients/26>`__         Male                   28 years   No                                  **Requested** → [Confirm] [Cancelled] [Trying]     4700 Eupen
 `ARENT Afánásiiá (25/robin) </#/api/avanti/Clients/25>`__         Female                 27 years   No                   50,00          **Trying** → [Requested]                           4700 Eupen
 `DEMEULENAERE Dorothée (22/nelly) </#/api/avanti/Clients/22>`__   Female                 unknown    No                                  **Confirmed** → [Cancelled] [Requested] [Trying]   4700 Eupen
 `ABBASI Aáishá (19/romain) </#/api/avanti/Clients/19>`__          Female                 20 years   No                                  **Requested** → [Confirm] [Cancelled] [Trying]     4700 Eupen
 `ALEKSANDROV Akim (17/nathalie) </#/api/avanti/Clients/17>`__     Male                   18 years   No                                  **Trying** → [Requested]                           4700 Eupen
 `ABBAS Aábid (16/nelly) </#/api/avanti/Clients/16>`__             Male                   17 years   No                                  **Confirmed** → [Cancelled] [Requested] [Trying]   4700 Eupen
 `ABEZGAUZ Adrik (13/nelly) </#/api/avanti/Clients/13>`__          Male                   16 years   No                                  **Requested** → [Confirm] [Cancelled] [Trying]     4700 Eupen
================================================================= ======== ============= ========== =========== ======== ============== ================================================== ==============
<BLANKLINE>


>>> kwargs = dict(column_names="id user owner", limit=3,
...     display_mode=DISPLAY_MODE_GRID)
>>> rt.login("robin").show(comments.Comments, **kwargs)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
==== ========== ==================================
 ID   Author     Topic
---- ---------- ----------------------------------
 1    audrey     `BALLO Armáni (80/romain) <…>`__
 2    martina    `BALLO Armáni (80/romain) <…>`__
 3    nathalie   `BALLO Armáni (80/romain) <…>`__
==== ========== ==================================
<BLANKLINE>


>>> kwargs.update(show_urls=True)
>>> rt.login("robin").show(comments.Comments, **kwargs)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
==================================== ======================================== =========================================================
 ID                                   Author                                   Topic
------------------------------------ ---------------------------------------- ---------------------------------------------------------
 `1 </#/api/comments/Comments/1>`__   `audrey </#/api/users/AllUsers/7>`__     `BALLO Armáni (80/romain) </#/api/avanti/Clients/80>`__
 `2 </#/api/comments/Comments/2>`__   `martina </#/api/users/AllUsers/8>`__    `BALLO Armáni (80/romain) </#/api/avanti/Clients/80>`__
 `3 </#/api/comments/Comments/3>`__   `nathalie </#/api/users/AllUsers/5>`__   `BALLO Armáni (80/romain) </#/api/avanti/Clients/80>`__
==================================== ======================================== =========================================================
<BLANKLINE>
