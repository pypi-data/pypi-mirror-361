.. doctest docs/specs/avanti/db.rst
.. _avanti.specs.db:

=================================
Database structure of Lino Avanti
=================================

This document describes the database structure.

.. contents::
  :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *

Complexity factors
==================


>>> print(analyzer.show_complexity_factors())
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
- 41 plugins
- 82 models
- 8 user types
- 308 views
- 24 dialog actions
<BLANKLINE>

The database models
===================


>>> analyzer.show_db_overview()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
41 plugins: lino, about, jinja, react, printing, system, help, users, office, xl, countries, contacts, contenttypes, gfks, cal, calview, avanti, memo, comments, linod, notify, changes, clients, uploads, checkdata, dupable, households, lists, beid, languages, cv, trends, polls, courses, export_excel, weasyprint, excerpts, dashboard, appypod, staticfiles, sessions.
82 models:
=========================== ============================ ========= =======
 Name                        Default table                #fields   #rows
--------------------------- ---------------------------- --------- -------
 avanti.Category             avanti.Categories            4         6
 avanti.Client               avanti.Clients               73        58
 avanti.EndingReason         avanti.EndingReasons         4         6
 avanti.Residence            avanti.Residences            9         0
 cal.AbsenceReason           cal.AbsenceReasons           4         4
 cal.Calendar                cal.Calendars                6         1
 cal.EntryRepeater           cal.EntryRepeaterTable       17        0
 cal.Event                   cal.Events                   26        278
 cal.EventPolicy             cal.EventPolicies            20        6
 cal.EventType               cal.EventTypes               24        6
 cal.Guest                   cal.Guests                   7         840
 cal.GuestRole               cal.GuestRoles               5         2
 cal.RecurrentEvent          cal.RecurrentEvents          22        15
 cal.RemoteCalendar          cal.RemoteCalendars          7         0
 cal.Room                    cal.Rooms                    10        0
 cal.Subscription            cal.Subscriptions            4         0
 cal.Task                    cal.Tasks                    17        5
 calview.DailyPlannerRow     calview.DailyPlannerRows     7         2
 changes.Change              changes.Changes              10        0
 checkdata.Message           checkdata.Messages           6         7
 clients.ClientContact       clients.ClientContacts       7         29
 clients.ClientContactType   clients.ClientContactTypes   5         6
 comments.Comment            comments.Comments            12        540
 comments.CommentType        comments.CommentTypes        4         5
 comments.Reaction           comments.Reactions           6         0
 contacts.Company            contacts.Companies           23        24
 contacts.CompanyType        contacts.CompanyTypes        7         16
 contacts.Partner            contacts.Partners            21        100
 contacts.Person             contacts.Persons             28        70
 contacts.Role               contacts.Roles               4         3
 contacts.RoleType           contacts.RoleTypes           5         7
 contenttypes.ContentType    gfks.ContentTypes            3         82
 countries.Country           countries.Countries          6         10
 countries.Place             countries.Places             9         80
 courses.Course              courses.Activities           31        3
 courses.Enrolment           courses.Enrolments           18        70
 courses.Line                courses.Lines                21        6
 courses.Reminder            courses.Reminders            9         0
 courses.Slot                courses.Slots                5         0
 courses.Topic               courses.Topics               4         2
 cv.Duration                 cv.Durations                 4         5
 cv.EducationLevel           cv.EducationLevels           7         5
 cv.Experience               cv.Experiences               18        0
 cv.Function                 cv.Functions                 6         0
 cv.LanguageKnowledge        cv.LanguageKnowledges        11        80
 cv.Regime                   cv.Regimes                   4         3
 cv.Sector                   cv.Sectors                   5         0
 cv.Status                   cv.Statuses                  4         7
 cv.Study                    cv.Studies                   17        0
 cv.StudyType                cv.StudyTypes                7         11
 cv.Training                 cv.Trainings                 17        0
 dashboard.Widget            dashboard.Widgets            5         0
 dupable.PhoneticWord        dupable.PhoneticWords        4         121
 excerpts.Excerpt            excerpts.Excerpts            12        0
 excerpts.ExcerptType        excerpts.ExcerptTypes        17        4
 households.Household        households.Households        23        6
 households.Member           households.Members           16        12
 households.Type             households.Types             4         6
 languages.Language          languages.Languages          5         5
 linod.SystemTask            linod.SystemTasks            25        8
 lists.List                  lists.Lists                  7         8
 lists.ListType              lists.ListTypes              4         3
 lists.Member                lists.Members                5         100
 memo.Mention                memo.Mentions                5         216
 notify.Message              notify.Messages              12        5
 polls.AnswerChoice          polls.AnswerChoices          5         0
 polls.AnswerRemark          polls.AnswerRemarks          4         0
 polls.Choice                polls.Choices                6         35
 polls.ChoiceSet             polls.ChoiceSets             5         8
 polls.Poll                  polls.Polls                  11        1
 polls.Question              polls.Questions              9         23
 polls.Response              polls.Responses              7         1
 sessions.Session            users.Sessions               3         ...
 system.SiteConfig           system.SiteConfigs           9         1
 trends.TrendArea            trends.TrendAreas            4         6
 trends.TrendEvent           trends.TrendEvents           7         174
 trends.TrendStage           trends.TrendStages           7         28
 uploads.Upload              uploads.Uploads              20        10
 uploads.UploadType          uploads.UploadTypes          10        9
 uploads.Volume              uploads.Volumes              4         0
 users.Authority             users.Authorities            3         0
 users.User                  users.AllUsers               24        9
=========================== ============================ ========= =======
<BLANKLINE>
