.. doctest docs/specs/avanti/roles.rst
.. _avanti.specs.roles:

=========================
User types in Lino Avanti
=========================

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *

>>> rt.show('users.UsersOverview')
========== ===================== ==========
 Username   User type             Language
---------- --------------------- ----------
 audrey     300 (Auditor)         en
 laura      100 (Teacher)         en
 martina    400 (Coordinator)     en
 nathalie   200 (Social worker)   en
 nelly      200 (Social worker)   en
 robin      900 (Administrator)   en
 rolf       900 (Administrator)   de
 romain     900 (Administrator)   fr
 sandra     410 (Secretary)       en
========== ===================== ==========
<BLANKLINE>

User roles
==========

The following table shows which roles are assigned to each user type.

>>> rt.show(users.UserRoles)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
================================ ===== ===== ===== ===== ===== ===== ===== =====
 Name                             000   100   200   300   400   410   800   900
-------------------------------- ----- ----- ----- ----- ----- ----- ----- -----
 avanti.Administrator                                                       ☑
 avanti.Auditor                                     ☑
 avanti.ClientsNameUser                 ☑     ☑           ☑     ☑     ☑     ☑
 avanti.ClientsStaff                                                  ☑     ☑
 avanti.ClientsUser                           ☑                 ☑     ☑     ☑
 avanti.Coordinator                                       ☑
 avanti.Secretary                                               ☑
 avanti.SiteStaff                                                     ☑     ☑
 avanti.SocialWorker                          ☑
 avanti.Teacher                         ☑
 beid.BeIdUser                                ☑                 ☑     ☑     ☑
 cal.GuestOperator                      ☑     ☑                       ☑     ☑
 checkdata.CheckdataUser                      ☑           ☑     ☑     ☑     ☑
 coachings.CoachingsStaff                                             ☑     ☑
 coachings.CoachingsUser                      ☑                       ☑     ☑
 comments.CommentsStaff                                               ☑     ☑
 comments.CommentsUser                        ☑                       ☑     ☑
 comments.PrivateCommentsReader                                             ☑
 contacts.ContactsStaff                                               ☑     ☑
 contacts.ContactsUser                        ☑                 ☑     ☑     ☑
 core.DataExporter                            ☑           ☑                 ☑
 core.Explorer                                ☑     ☑                 ☑     ☑
 core.SiteAdmin                                                             ☑
 core.SiteUser                          ☑     ☑     ☑     ☑     ☑     ☑     ☑
 courses.CoursesTeacher                 ☑
 courses.CoursesUser                          ☑     ☑     ☑     ☑     ☑     ☑
 cv.CareerStaff                                                       ☑     ☑
 cv.CareerUser                                ☑                       ☑     ☑
 excerpts.ExcerptsStaff                                               ☑     ☑
 excerpts.ExcerptsUser                        ☑                 ☑     ☑     ☑
 office.OfficeOperator                        ☑           ☑     ☑     ☑     ☑
 office.OfficeStaff                                                   ☑     ☑
 office.OfficeUser                      ☑     ☑     ☑           ☑     ☑     ☑
 polls.PollsStaff                                                     ☑     ☑
 polls.PollsUser                              ☑                       ☑     ☑
 search.SiteSearcher                          ☑                       ☑     ☑
 trends.TrendsStaff                                                   ☑     ☑
 trends.TrendsUser                            ☑                       ☑     ☑
================================ ===== ===== ===== ===== ===== ===== ===== =====
<BLANKLINE>



Site manager
==================

>>> show_menu('robin')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
- Contacts : Persons, Organizations, Clients, My Clients, Households, Partner Lists
- Calendar : My appointments, Overdue appointments, My unconfirmed appointments, My tasks, My guests, My presences, My overdue appointments, Calendar
- Office : My Comments, Recent comments, My Notification messages, My expiring upload files, My Upload files, My Excerpts, Data problem messages assigned to me
- Polls : My Polls, My Responses
- Activities : My Activities, Activities, -, Activity lines, Pending requested enrolments, Pending confirmed enrolments, Course planning, Absence control
- Configure :
  - System : Users, Site configuration, System tasks
  - Places : Countries, Places
  - Contacts : Legal forms, Functions, Categories, Ending reasons, Household Types, List Types
  - Calendar : Calendars, Rooms, Recurring events, Guest roles, Calendar entry types, Recurrency policies, Remote Calendars, Absence reasons, Planner rows
  - Office : Comment Types, Library volumes, Upload types, Excerpt Types
  - Clients : Client Contact types
  - Career : Education Types, Education Levels, Activity sectors, Job titles, Work Regimes, Statuses, Contract Durations, Languages
  - Trends : Trend areas, Trend stages
  - Polls : Choice Sets
  - Activities : Topics, Timetable Slots
- Explorer :
  - System : Authorities, User types, User roles, Notification messages, Changes, Phonetic words, All dashboard widgets, content types, Background procedures, Data checkers, Data problem messages
  - Contacts : Contact persons, Partners, Clients, Residences, Household member roles, Household Members, List memberships
  - Calendar : Calendar entries, Tasks, Presences, Subscriptions, Entry states, Presence states, Task states, Planner columns, Display colors
  - Office : Comments, Reactions, Upload files, Upload areas, Excerpts, Mentions
  - Clients : Client Contacts, Known contact types
  - Career : Language knowledges, Trainings, Studies, Job Experiences
  - Trends : Trend events
  - Polls : Polls, Questions, Choices, Responses, Answer Choices, Answer Remarks
  - Activities : Activities, Enrolments, Enrolment states, Course layouts, Activity states, Reminders
- Site : About, User sessions



Coordinator
===========

>>> rt.login('martina').user.user_type
<users.UserTypes.coordinator:400>

>>> show_menu('martina')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
- Office : My expiring upload files, My Upload files, My Excerpts, Data problem messages assigned to me
- Activities : My Activities, Activities, -, Activity lines, Course planning
- Site : About


Secretary
=========

>>> rt.login('sandra').user.user_type
<users.UserTypes.secretary:410>

>>> show_menu('sandra')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
- Contacts : Persons, Organizations, Clients, My Clients, Households, Partner Lists
- Calendar : My appointments, My unconfirmed appointments, My tasks, My guests, My presences, My overdue appointments, Calendar
- Office : My Notification messages, My expiring upload files, My Upload files, My Excerpts, Data problem messages assigned to me
- Activities : My Activities, Activities, -, Activity lines, Course planning
- Explorer :
  - Contacts : Partners
  - Activities : Reminders
- Site : About



Social worker
=============

>>> show_menu('nathalie')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
- Contacts : Persons, Organizations, Clients, My Clients, Households, Partner Lists
- Calendar : My appointments, My unconfirmed appointments, My tasks, My guests, My presences, My overdue appointments, Calendar
- Office : My Comments, Recent comments, My Notification messages, My expiring upload files, My Upload files, My Excerpts, Data problem messages assigned to me
- Polls : My Polls, My Responses
- Activities : My Activities, Activities, -, Activity lines, Course planning, Absence control
- Configure :
  - Trends : Trend stages
- Explorer :
  - Contacts : Partners, Clients, Residences
  - Calendar : Calendar entries, Presences, Display colors
  - Activities : Activities, Enrolments, Reminders
- Site : About

Teacher
=======

>>> rt.login('laura').user.user_type
<users.UserTypes.teacher:100>

>>> show_menu('laura')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
- Calendar : My appointments, My unconfirmed appointments, My tasks, My guests, My presences, My overdue appointments
- Office : My Notification messages, My expiring upload files, My Upload files
- Activities : My Activities, -, My courses given
- Site : About

Supervisor
==========

>>> show_menu('audrey')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
- Calendar : My appointments, My unconfirmed appointments, My tasks, My guests, My presences, My overdue appointments
- Office : My Notification messages, My expiring upload files, My Upload files
- Activities : My Activities, Activities, -, Activity lines, Course planning
- Explorer :
  - Contacts : Clients, Residences
  - Calendar : Calendar entries, Display colors
  - Activities : Activities, Enrolments
- Site : About



Windows and permissions
=======================

Each window is **viewable** for a given set of user types.

>>> print(analyzer.show_window_permissions())
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- about.About.insert_reference : visible for all
- about.About.reset_password : visible for all
- about.About.show : visible for all
- about.About.sign_in : visible for all
- about.About.verify_user : visible for all
- avanti.Clients.detail : visible for user secretary staff admin
- avanti.Clients.merge_row : visible for admin
- cal.Calendars.detail : visible for staff admin
- cal.Calendars.insert : visible for staff admin
- cal.EntriesByGuest.insert : visible for teacher user coordinator secretary staff admin
- cal.EntriesByProject.insert : visible for teacher user coordinator secretary staff admin
- cal.EventTypes.detail : visible for staff admin
- cal.EventTypes.insert : visible for staff admin
- cal.EventTypes.merge_row : visible for admin
- cal.Events.detail : visible for teacher user auditor secretary staff admin
- cal.Events.insert : visible for teacher user secretary staff admin
- cal.GuestRoles.detail : visible for admin
- cal.GuestRoles.merge_row : visible for admin
- cal.Guests.detail : visible for teacher user staff admin
- cal.Guests.insert : visible for teacher user staff admin
- cal.RecurrentEvents.detail : visible for staff admin
- cal.RecurrentEvents.insert : visible for staff admin
- cal.Rooms.detail : visible for staff admin
- cal.Rooms.insert : visible for staff admin
- cal.Tasks.detail : visible for staff admin
- cal.Tasks.insert : visible for staff admin
- calview.DailyView.detail : visible for user secretary staff admin
- calview.MonthlyView.detail : visible for user secretary staff admin
- calview.WeeklyView.detail : visible for user secretary staff admin
- changes.Changes.detail : visible for admin
- checkdata.Checkers.detail : visible for admin
- checkdata.Messages.detail : visible for teacher user auditor coordinator secretary staff admin
- clients.ClientContactTypes.detail : visible for staff admin
- comments.CommentTypes.detail : visible for staff admin
- comments.CommentTypes.insert : visible for staff admin
- comments.Comments.detail : visible for user staff admin
- comments.Comments.insert : visible for user staff admin
- comments.CommentsByRFC.insert : visible for user staff admin
- contacts.Companies.detail : visible for user secretary staff admin
- contacts.Companies.insert : visible for user secretary staff admin
- contacts.Companies.merge_row : visible for admin
- contacts.Partners.merge_row : visible for admin
- contacts.Persons.create_household : visible for user secretary staff admin
- contacts.Persons.detail : visible for user secretary staff admin
- contacts.Persons.insert : visible for user secretary staff admin
- contacts.Persons.merge_row : visible for admin
- contacts.RolesByCompany.insert : visible for user secretary staff admin
- contacts.RolesByPerson.insert : visible for user secretary staff admin
- countries.Countries.detail : visible for staff admin
- countries.Countries.insert : visible for staff admin
- countries.Places.detail : visible for staff admin
- countries.Places.insert : visible for staff admin
- courses.Activities.detail : visible for teacher user auditor coordinator secretary staff admin
- courses.Activities.insert : visible for user coordinator secretary staff admin
- courses.Activities.print_description : visible for user auditor coordinator secretary staff admin
- courses.Activities.print_presence_sheet : visible for user auditor coordinator secretary staff admin
- courses.Activities.print_presence_sheet_html : visible for user auditor coordinator secretary staff admin
- courses.Enrolments.detail : visible for teacher user auditor coordinator secretary staff admin
- courses.Enrolments.insert : visible for teacher user coordinator secretary staff admin
- courses.EnrolmentsByCourse.insert : visible for teacher user coordinator secretary staff admin
- courses.EnrolmentsByPupil.insert : visible for user coordinator secretary staff admin
- courses.Lines.detail : visible for user auditor coordinator secretary staff admin
- courses.Lines.insert : visible for user coordinator secretary staff admin
- courses.Lines.merge_row : visible for admin
- courses.RemindersByEnrolment.detail : visible for user secretary staff admin
- courses.RemindersByEnrolment.insert : visible for user secretary staff admin
- courses.Slots.detail : visible for admin
- courses.Slots.insert : visible for admin
- courses.StatusReport.show : visible for user auditor coordinator secretary staff admin
- courses.Topics.detail : visible for admin
- cv.Durations.detail : visible for staff admin
- cv.EducationLevels.detail : visible for staff admin
- cv.Experiences.detail : visible for staff admin
- cv.ExperiencesByPerson.insert : visible for user staff admin
- cv.Functions.detail : visible for staff admin
- cv.LanguageKnowledgesByPerson.detail : visible for user staff admin
- cv.LanguageKnowledgesByPerson.insert : visible for user staff admin
- cv.Regimes.detail : visible for staff admin
- cv.Sectors.detail : visible for staff admin
- cv.Statuses.detail : visible for staff admin
- cv.Studies.detail : visible for staff admin
- cv.StudiesByPerson.insert : visible for user staff admin
- cv.StudyTypes.detail : visible for staff admin
- cv.StudyTypes.insert : visible for staff admin
- cv.Trainings.detail : visible for user staff admin
- cv.Trainings.insert : visible for user staff admin
- excerpts.ExcerptTypes.detail : visible for staff admin
- excerpts.ExcerptTypes.insert : visible for staff admin
- excerpts.Excerpts.detail : visible for user coordinator secretary staff admin
- gfks.ContentTypes.detail : visible for admin
- households.Households.detail : visible for user secretary staff admin
- households.Households.insert : visible for user secretary staff admin
- households.Households.merge_row : visible for admin
- households.HouseholdsByType.insert : visible for user secretary staff admin
- households.MembersByPerson.insert : visible for user secretary staff admin
- households.Types.detail : visible for staff admin
- languages.Languages.detail : visible for staff admin
- linod.SystemTasks.detail : visible for admin
- linod.SystemTasks.insert : visible for admin
- lists.Lists.detail : visible for user secretary staff admin
- lists.Lists.insert : visible for user secretary staff admin
- lists.Lists.merge_row : visible for admin
- lists.Members.detail : visible for user secretary staff admin
- lists.MembersByPartner.insert : visible for user secretary staff admin
- polls.AnswerRemarks.detail : visible for user staff admin
- polls.AnswerRemarks.insert : visible for user staff admin
- polls.ChoiceSets.detail : visible for staff admin
- polls.Polls.detail : visible for user staff admin
- polls.Polls.insert : visible for user staff admin
- polls.Polls.merge_row : visible for admin
- polls.Questions.detail : visible for staff admin
- polls.Responses.detail : visible for user staff admin
- polls.Responses.insert : visible for user staff admin
- system.SiteConfigs.detail : visible for admin
- trends.TrendAreas.detail : visible for staff admin
- trends.TrendStages.detail : visible for user staff admin
- trends.TrendStages.insert : visible for user staff admin
- trends.TrendStages.merge_row : visible for admin
- uploads.AllUploads.detail : visible for staff admin
- uploads.AllUploads.insert : visible for staff admin
- uploads.UploadTypes.detail : visible for staff admin
- uploads.UploadTypes.insert : visible for staff admin
- uploads.Uploads.camera_stream : visible for teacher user auditor coordinator secretary staff admin
- uploads.Uploads.detail : visible for teacher user auditor coordinator secretary staff admin
- uploads.Uploads.insert : visible for teacher user coordinator secretary staff admin
- uploads.UploadsByController.insert : visible for teacher user coordinator secretary staff admin
- uploads.UploadsByVolume.detail : visible for teacher user auditor coordinator secretary staff admin
- uploads.UploadsByVolume.insert : visible for teacher user coordinator secretary staff admin
- uploads.Volumes.detail : visible for staff admin
- uploads.Volumes.insert : visible for staff admin
- uploads.Volumes.merge_row : visible for admin
- users.AllUsers.change_password : visible for admin
- users.AllUsers.detail : visible for admin
- users.AllUsers.insert : visible for admin
- users.AllUsers.merge_row : visible for admin
- users.AllUsers.verify_me : visible for admin
<BLANKLINE>


Not everybody can see the names of participants
===============================================

The names of the participants are confidential data in :ref:`avanti`.

A :term:`site manager` can see the full names:

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


Teachers and coordinators can see the full names (they need it because they must
register presences and absences), but they cannot click on a name to see any
detail.

>>> rt.login('laura').show('courses.EnrolmentsByCourse', obj, show_urls=True)
... #doctest: +NORMALIZE_WHITESPACE -REPORT_UDIFF
==================================== ======== ============= ========== =========== ======== ============== ================================================== ==============
 Participant                          Gender   Nationality   Age        Childcare   Remark   Missing rate   Workflow                                           Municipality
------------------------------------ -------- ------------- ---------- ----------- -------- -------------- -------------------------------------------------- --------------
 *ARNOLD Alexei (30/nathalie)*        Male                   28 years   No                   50,00          **Confirmed** → [Cancelled] [Requested] [Trying]   4700 Eupen
 *ABDELNOUR Aámir (26/nelly)*         Male                   28 years   No                                  **Requested** → [Confirm] [Cancelled] [Trying]     4700 Eupen
 *ARENT Afánásiiá (25/robin)*         Female                 27 years   No                   50,00          **Trying** → [Requested]                           4700 Eupen
 *DEMEULENAERE Dorothée (22/nelly)*   Female                 unknown    No                                  **Confirmed** → [Cancelled] [Requested] [Trying]   4700 Eupen
 *ABBASI Aáishá (19/romain)*          Female                 20 years   No                                  **Requested** → [Confirm] [Cancelled] [Trying]     4700 Eupen
 *ALEKSANDROV Akim (17/nathalie)*     Male                   18 years   No                                  **Trying** → [Requested]                           4700 Eupen
 *ABBAS Aábid (16/nelly)*             Male                   17 years   No                                  **Confirmed** → [Cancelled] [Requested] [Trying]   4700 Eupen
 *ABEZGAUZ Adrik (13/nelly)*          Male                   16 years   No                                  **Requested** → [Confirm] [Cancelled] [Trying]     4700 Eupen
==================================== ======== ============= ========== =========== ======== ============== ================================================== ==============
<BLANKLINE>


>>> rt.login('martina').show('courses.EnrolmentsByCourse', obj, show_urls=True)
... #doctest: +NORMALIZE_WHITESPACE -REPORT_UDIFF
==================================== ======== ============= ========== =========== ======== ============== ================================================== ==============
 Participant                          Gender   Nationality   Age        Childcare   Remark   Missing rate   Workflow                                           Municipality
------------------------------------ -------- ------------- ---------- ----------- -------- -------------- -------------------------------------------------- --------------
 *ARNOLD Alexei (30/nathalie)*        Male                   28 years   No                   50,00          **Confirmed** → [Cancelled] [Requested] [Trying]   4700 Eupen
 *ABDELNOUR Aámir (26/nelly)*         Male                   28 years   No                                  **Requested** → [Confirm] [Cancelled] [Trying]     4700 Eupen
 *ARENT Afánásiiá (25/robin)*         Female                 27 years   No                   50,00          **Trying** → [Requested]                           4700 Eupen
 *DEMEULENAERE Dorothée (22/nelly)*   Female                 unknown    No                                  **Confirmed** → [Cancelled] [Requested] [Trying]   4700 Eupen
 *ABBASI Aáishá (19/romain)*          Female                 20 years   No                                  **Requested** → [Confirm] [Cancelled] [Trying]     4700 Eupen
 *ALEKSANDROV Akim (17/nathalie)*     Male                   18 years   No                                  **Trying** → [Requested]                           4700 Eupen
 *ABBAS Aábid (16/nelly)*             Male                   17 years   No                                  **Confirmed** → [Cancelled] [Requested] [Trying]   4700 Eupen
 *ABEZGAUZ Adrik (13/nelly)*          Male                   16 years   No                                  **Requested** → [Confirm] [Cancelled] [Trying]     4700 Eupen
==================================== ======== ============= ========== =========== ======== ============== ================================================== ==============
<BLANKLINE>



Auditors can't even see the name. They see only the pupil's number and place:

>>> rt.login('audrey').show('courses.EnrolmentsByCourse', obj, show_urls=True)
... #doctest: +NORMALIZE_WHITESPACE -REPORT_UDIFF
=================== ======== ============= ========== =========== ======== ============== =============== ==============
 Participant         Gender   Nationality   Age        Childcare   Remark   Missing rate   Workflow        Municipality
------------------- -------- ------------- ---------- ----------- -------- -------------- --------------- --------------
 *(30) from Eupen*   Male                   28 years   No                   50,00          **Confirmed**   4700 Eupen
 *(26) from Eupen*   Male                   28 years   No                                  **Requested**   4700 Eupen
 *(25) from Eupen*   Female                 27 years   No                   50,00          **Trying**      4700 Eupen
 *(22) from Eupen*   Female                 unknown    No                                  **Confirmed**   4700 Eupen
 *(19) from Eupen*   Female                 20 years   No                                  **Requested**   4700 Eupen
 *(17) from Eupen*   Male                   18 years   No                                  **Trying**      4700 Eupen
 *(16) from Eupen*   Male                   17 years   No                                  **Confirmed**   4700 Eupen
 *(13) from Eupen*   Male                   16 years   No                                  **Requested**   4700 Eupen
=================== ======== ============= ========== =========== ======== ============== =============== ==============
<BLANKLINE>



Teachers can see the names of their pupils, but must not see all the clients in
the database.  Accordingly they cannot create new enrolments or new presences
since this would require them to specify a client in the combobox (which would
show all clients). OTOH a teacher *can* edit other fields on these records (e.g.
change the workflow or write a remark).  Since we cannot make the whole record
read-only, we disable the fields.

>>> ar = rt.login("laura")
>>> def get_disabled_fields(Model):
...     sar = Model.get_default_table().request(parent=ar)
...     return Model.objects.first().disabled_fields(sar)

>>> "pupil" in get_disabled_fields(courses.Enrolment)
True
>>> "partner" in get_disabled_fields(cal.Guest)
True

For a coordinator these fields are not disabled:

>>> ar = rt.login("sandra")
>>> "pupil" in get_disabled_fields(courses.Enrolment)
False
>>> "partner" in get_disabled_fields(cal.Guest)
False
