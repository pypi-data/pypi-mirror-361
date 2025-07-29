.. doctest docs/specs/avanti/general.rst
.. _avanti.specs.general:

===============================
General overview of Lino Avanti
===============================

.. contents::
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *



Miscellaneous
=============


>>> dd.plugins.beid.holder_model
<class 'lino_avanti.lib.avanti.models.Client'>

The following checks whether the dashboard displays for user robin:

>>> url = "/"
>>> test_client.force_login(rt.login('robin').user)
>>> res = test_client.get(url, REMOTE_USER="robin")
>>> res.status_code
200
>>> soup = BeautifulSoup(res.content, "lxml")
>>> links = soup.find_all('a')
>>> len(links)
0

Status report
=============

Here is a text variant of Robin's dashboard.

TODO: The following test is skipped because the show_dashboard() function needs
a review. It can cause false failures and it doesn't cover all issues.


>>> show_dashboard('robin')
... #doctest: +REPORT_UDIFF +ELLIPSIS +NORMALIZE_WHITESPACE +SKIP
Quick links: [[Search](javascript:Lino.about.SiteSearch.grid.run\(null\))]
[[My settings](javascript:Lino.users.MySettings.detail.run\(null,{
"record_id": 1 }\) "Open a detail window on this record.")] [[My
Clients](javascript:Lino.avanti.MyClients.grid.run\(null\))] [[New
Client](javascript:Lino.avanti.MyClients.insert.run\(null\) "Open a dialog
window to insert a new Client.")] [[Read eID
card](javascript:Lino.list_action_handler\('/avanti/MyClients','find_by_beid','POST',Lino.beid_read_card_processor\)\(\)
"Find or create card holder from eID card")]
[[Refresh](javascript:Lino.viewport.refresh\(\);)]
<BLANKLINE>
Hi, Robin Rood! [There are 5 data problems assigned to
you.](javascript:Lino.checkdata.MyMessages.grid.run\(null,{ "base_params": {
}, "param_values": { "checker": null, "checkerHidden": null, "user": "Robin
Rood", "userHidden": 1 } }\))
<BLANKLINE>
This is a Lino demo site. ...
## My appointments
...
## My unconfirmed appointments
...
## Daily planner [⏏](javascript:Lino.calview.DailyPlanner.grid.run\(null\)
"Show this table in own window")
...
## Recent comments
...
## My Notification messages
...
## Status Report [⏏](javascript:Lino.courses.StatusReport.show.run\(null,{
...
### Language courses
<BLANKLINE>
<BLANKLINE>


Window fields
=============

The following snippet verifies whether all window fields are visible.

>>> print(analyzer.show_window_fields()) #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- about.About.insert_reference : content_type, primary_key
- about.About.reset_password : email, username, new1, new2
- about.About.show : about_html
- about.About.sign_in : username, password
- about.About.verify_user : email, verification_code
- avanti.Clients.detail : overview, id, national_id, ref, birth_date, age, gender, starting_reason, professional_state, reason_of_stay, category, client_state, user, event_policy, ending_reason, image, cal.EntriesByProject, cal.EntriesByProject, cal.GuestsByPartner, cal.GuestsByPartner, cal.GuestsByPartner, first_name, middle_name, last_name, nationality, nationality_text, birth_country, birth_place, in_belgium_since, in_region_since, card_type, card_issuer, card_valid_from, card_valid_until, needs_work_permit, has_contact_pcsw, has_contact_work_office, clients.ContactsByClient, clients.ContactsByClient, uploads.UploadsByProject, excerpts.ExcerptsByProject, country, city, zip_code, addr1, street, street_no, addr2, email, phone, fax, gsm, avanti.ResidencesByPerson, ResidencesByPerson, language, translator_type, translator_notes, cv.LanguageKnowledgesByPerson, language_notes, courses.EnrolmentsByPupil, courses.EnrolmentsByPupil, households.MembersByPerson, households.SiblingsByPerson, households.SiblingsByPerson, comments.CommentsByRFC, cal.TasksByProject, courses.RemindersByPupil, courses.RemindersByPupil, cv.StudiesByPerson, cv.StudiesByPerson, cv.ExperiencesByPerson, cv.ExperiencesByPerson, polls.ResponsesByPartner, financial_notes, health_notes, integration_notes, remarks, family_notes, residence_notes, changes.ChangesByMaster, changes.ChangesByMaster, checkdata.MessagesByOwner, dupable.SimilarObjects
- avanti.Clients.merge_row : merge_to, avanti_Residence, cv_LanguageKnowledge, lists_Member, reason
- cal.Calendars.detail : name, name_de, name_fr, color, id, description, cal.SubscriptionsByCalendar, SubscriptionsByCalendar
- cal.Calendars.insert : name, name_de, name_fr, color
- cal.EntriesByGuest.insert : start_date, start_time, end_time, summary, event_type
- cal.EntriesByProject.insert : start_date, start_time, end_time, summary, event_type
- cal.EventTypes.detail : ref, id, planner_column, default_duration, name, name_de, name_fr, event_label, event_label_de, event_label_fr, start_date, max_days, max_conflicting, email_template, attach_to_email, is_appointment, is_public, force_guest_states, fill_presences, all_rooms, locks_user, transparent, cal.EntriesByType, EntriesByType
- cal.EventTypes.insert : name, name_de, name_fr, ref, event_label, event_label_de, event_label_fr
- cal.EventTypes.merge_row : merge_to, reason
- cal.Events.detail : event_type, summary, notify_before, notify_unit, start_date, start_time, end_date, end_time, room, project, owner, workflow_buttons, description, user, assigned_to, cal.GuestsByEvent, GuestsByEvent
- cal.Events.insert : start_date, start_time, end_date, end_time, summary
- cal.GuestRoles.detail : ref, name, name_de, name_fr, id, cal.GuestsByRole, cal.GuestsByRole
- cal.GuestRoles.merge_row : merge_to, reason
- cal.Guests.detail : event, partner, role, state, workflow_buttons, absence_reason, remark
- cal.Guests.insert : event, partner, role
- cal.RecurrentEvents.detail : name, name_de, name_fr, id, user, event_type, start_date, start_time, end_date, end_time, every_unit, every, positions, max_events, monday, tuesday, wednesday, thursday, friday, saturday, sunday, description, cal.EntriesByController
- cal.RecurrentEvents.insert : name, name_de, name_fr, start_date, end_date, every_unit, event_type
- cal.Rooms.detail : id, name, name_de, name_fr, company, contact_person, display_color, description, cal.EntriesByRoom, cal.EntriesByRoom
- cal.Rooms.insert : id, name, name_de, name_fr, display_color, company, contact_person
- cal.Tasks.detail : start_date, priority, due_date, id, workflow_buttons, summary, user, project, owner, created, modified, description
- cal.Tasks.insert : summary, user, project
- calview.DailyView.detail :
- calview.MonthlyView.detail :
- calview.WeeklyView.detail :
- changes.Changes.detail : time, user, type, master, object, id, diff
- checkdata.Checkers.detail : value, text, checkdata.MessagesByChecker, checkdata.MessagesByChecker
- checkdata.Messages.detail : checker, owner, message, user, id
- clients.ClientContactTypes.detail : id, name, name_de, name_fr, clients.PartnersByClientContactType, clients.PartnersByClientContactType, clients.PartnersByClientContactType, clients.ClientContactsByType, clients.ClientContactsByType
- comments.CommentTypes.detail : id, name, name_de, name_fr, comments.CommentsByType
- comments.CommentTypes.insert : name, name_de, name_fr, id
- comments.Comments.detail : owner, private, reply_to, pick_my_emotion, body, comments.RepliesByComment, id, user, owner_type, owner_id, created, modified, comment_type, comments.ReactionsByComment
- comments.Comments.insert : reply_to, owner, owner_type, owner_id, body, private
- comments.CommentsByRFC.insert : reply_to, body, private
- contacts.Companies.detail : overview, email, phone, gsm, fax, lists.MembersByPartner, remarks, prefix, name, street, street_box, addr2, country, zip_code, city, contacts.RolesByCompany, id, language, type, client_contact_type, addr1, url, clients.ClientContactsByCompany, clients.ClientContactsByCompany, checkdata.MessagesByOwner
- contacts.Companies.insert : name, email, type
- contacts.Companies.merge_row : merge_to, lists_Member, reason
- contacts.Partners.merge_row : merge_to, lists_Member, reason
- contacts.Persons.create_household : head, type, partner
- contacts.Persons.detail : overview, email, phone, gsm, lists.MembersByPartner, remarks, checkdata.MessagesByOwner, last_name, first_name, gender, street, street_box, country, zip_code, city, birth_date, age, contacts.RolesByPerson, id, language, url, addr1, addr2
- contacts.Persons.insert : first_name, last_name, gender, email
- contacts.Persons.merge_row : merge_to, lists_Member, reason
- contacts.RolesByCompany.insert : person, type
- contacts.RolesByPerson.insert : type, company
- countries.Countries.detail : isocode, name, name_de, name_fr, short_code, countries.PlacesByCountry, countries.PlacesByCountry
- countries.Countries.insert : isocode, short_code, name, name_de, name_fr
- countries.Places.detail : name, name_de, name_fr, country, type, parent, zip_code, id, countries.PlacesByPlace, PlacesByPlace, contacts.PartnersByCity
- countries.Places.insert : name, name_de, name_fr, country, zip_code, type, parent
- courses.Activities.detail : line, teacher, start_date, start_time, end_time, end_date, room, workflow_buttons, id, user, name, can_excuse, description, description_de, description_fr, max_events, max_date, every_unit, every, positions, monday, tuesday, wednesday, thursday, friday, saturday, sunday, cal.EntriesByController, enrolments_until, max_places, confirmed, free_places, print_actions, courses.EnrolmentsByCourse, EnrolmentsByCourse
- courses.Activities.insert : line, teacher, name, start_date
- courses.Activities.print_description : start_date, end_date, show_remarks, show_states
- courses.Activities.print_presence_sheet : start_date, end_date, show_remarks, show_states
- courses.Activities.print_presence_sheet_html : start_date, end_date, show_remarks, show_states
- courses.Enrolments.detail : request_date, user, start_date, end_date, course, pupil, needs_childcare, needs_school, needs_bus, needs_evening, remark, workflow_buttons, printed, missing_rate, confirmation_details, courses.PresencesByEnrolment, courses.RemindersByEnrolment
- courses.Enrolments.insert : request_date, user, course, pupil, remark
- courses.EnrolmentsByCourse.insert : pupil, remark, request_date, user
- courses.EnrolmentsByPupil.insert : course, remark, request_date, user
- courses.Lines.detail : id, name, name_de, name_fr, ref, company, contact_person, course_area, topic, body_template, event_type, guest_role, every_unit, every, excerpt_title, excerpt_title_de, excerpt_title_fr, description, description_de, description_fr
- courses.Lines.insert : name, name_de, name_fr, ref, topic, every_unit, every, event_type, description, description_de, description_fr
- courses.Lines.merge_row : merge_to, reason
- courses.RemindersByEnrolment.detail : date_issued, degree, workflow_buttons, remark, enrolment, user, id, printed, text_body
- courses.RemindersByEnrolment.insert : degree, remark, text_body
- courses.Slots.detail : name, start_time, end_time, courses.ActivitiesBySlot, courses.ActivitiesBySlot
- courses.Slots.insert : start_time, end_time, name
- courses.StatusReport.show : body
- courses.Topics.detail : id, name, name_de, name_fr, courses.LinesByTopic, courses.LinesByTopic, courses.ActivitiesByTopic, courses.ActivitiesByTopic
- cv.Durations.detail : id, name, name_de, name_fr, cv.ExperiencesByDuration, ExperiencesByDuration
- cv.EducationLevels.detail : name, name_de, name_fr, is_study, is_training, cv.StudyTypesByLevel, StudyTypesByLevel, cv.StudiesByLevel, StudiesByLevel
- cv.Experiences.detail : person, company, country, city, title, status, duration, regime, is_training, duration_text, termination_reason, remarks
- cv.ExperiencesByPerson.insert : start_date, end_date, company, function
- cv.Functions.detail : id, name, name_de, name_fr, sector, remark, cv.ExperiencesByFunction, cv.ExperiencesByFunction
- cv.LanguageKnowledgesByPerson.detail : language, native, has_certificate, cef_level, spoken_passively, spoken, written, entry_date
- cv.LanguageKnowledgesByPerson.insert : language, native, has_certificate, cef_level, spoken_passively, spoken, written, entry_date
- cv.Regimes.detail : id, name, name_de, name_fr, cv.ExperiencesByRegime, ExperiencesByRegime
- cv.Sectors.detail : id, name, name_de, name_fr, remark, cv.FunctionsBySector, FunctionsBySector, cv.ExperiencesBySector, cv.ExperiencesBySector
- cv.Statuses.detail : id, name, name_de, name_fr, cv.ExperiencesByStatus, ExperiencesByStatus
- cv.Studies.detail : person, duration_text, language, type, content, education_level, state, foreign_education_level, recognized, school, country, city, remarks
- cv.StudiesByPerson.insert : type, content, duration_text, language
- cv.StudyTypes.detail : name, name_de, name_fr, id, education_level, is_study, is_training, cv.StudiesByType, cv.StudiesByType, cv.TrainingsByType, cv.TrainingsByType
- cv.StudyTypes.insert : name, name_de, name_fr, is_study, is_training, education_level
- cv.Trainings.detail : person, start_date, end_date, duration_text, type, state, certificates, sector, function, school, country, city, remarks
- cv.Trainings.insert : person, start_date, end_date, type, state, certificates, sector, function, school, country, city
- excerpts.ExcerptTypes.detail : id, name, name_de, name_fr, content_type, build_method, template, body_template, email_template, shortcut, primary, print_directly, certifying, print_recipient, backward_compat, attach_to_email, excerpts.ExcerptsByType, excerpts.ExcerptsByType
- excerpts.ExcerptTypes.insert : name, name_de, name_fr, content_type, primary, certifying, build_method, template, body_template
- excerpts.Excerpts.detail : id, excerpt_type, project, user, build_method, company, contact_person, language, owner, build_time, body_template_content
- gfks.ContentTypes.detail : id, app_label, model, base_classes, gfks.BrokenGFKsByModel, BrokenGFKsByModel
- households.Households.detail : type, prefix, name, language, id, country, region, city, zip_code, street_prefix, street, street_no, street_box, addr2, phone, gsm, email, url, households.MembersByHousehold, households.MembersByHousehold
- households.Households.insert : type, name, language
- households.Households.merge_row : merge_to, households_Member, lists_Member, reason
- households.HouseholdsByType.insert : name, language
- households.MembersByPerson.insert : person, role, household, primary
- households.Types.detail : name, name_de, name_fr, households.HouseholdsByType, households.HouseholdsByType, HouseholdsByType
- languages.Languages.detail : id, iso2, name, name_de, name_fr, cv.KnowledgesByLanguage, cv.KnowledgesByLanguage
- linod.SystemTasks.detail : seqno, procedure, name, every, every_unit, log_level, disabled, status, requested_at, last_start_time, last_end_time, message
- linod.SystemTasks.insert : procedure, every, every_unit
- lists.Lists.detail : id, ref, list_type, print_actions, designation, designation_de, designation_fr, remarks, lists.MembersByList, MembersByList
- lists.Lists.insert : ref, list_type, designation, designation_de, designation_fr, remarks
- lists.Lists.merge_row : merge_to, lists_Member, reason
- lists.Members.detail : list, partner, remark
- lists.MembersByPartner.insert : list, remark
- polls.AnswerRemarks.detail : remark, response, question
- polls.AnswerRemarks.insert : remark, response, question
- polls.ChoiceSets.detail : name, name_de, name_fr, choice_type, polls.ChoicesBySet, ChoicesBySet
- polls.Polls.detail : ref, title, workflow_buttons, details, default_choiceset, default_multiple_choices, polls.QuestionsByPoll, polls.QuestionsByPoll, id, user, created, modified, state, polls.ResponsesByPoll, polls.ResponsesByPoll, polls.PollResult, PollResult
- polls.Polls.insert : ref, title, default_choiceset, default_multiple_choices, questions_to_add
- polls.Polls.merge_row : merge_to, polls_Question, reason
- polls.Questions.detail : poll, number, is_heading, choiceset, multiple_choices, title, details, polls.AnswersByQuestion, AnswersByQuestion
- polls.Responses.detail : poll, partner, date, workflow_buttons, polls.AnswersByResponseEditor, user, state, remark, polls.AnswersByResponsePrint
- polls.Responses.insert : user, date, poll
- system.SiteConfigs.detail : default_build_method, simulate_today, site_calendar, default_event_type, pupil_guestrole, max_auto_events, hide_events_before
- trends.TrendAreas.detail : id, name, name_de, name_fr, trends.StagesByArea, StagesByArea
- trends.TrendStages.detail : ref, trend_area, id, name, name_de, name_fr, trends.EventsByStage, EventsByStage
- trends.TrendStages.insert : name, name_de, name_fr, ref, trend_area
- trends.TrendStages.merge_row : merge_to, reason
- uploads.AllUploads.detail : user, project, id, type, description, start_date, end_date, needed, company, contact_person, contact_role, file, owner, remark, cal.TasksByController
- uploads.AllUploads.insert : type, description, file, volume, library_file, user
- uploads.UploadTypes.detail : id, upload_area, shortcut, name, name_de, name_fr, warn_expiry_unit, warn_expiry_value, wanted, max_number, uploads.UploadsByType, uploads.UploadsByType
- uploads.UploadTypes.insert : upload_area, name, name_de, name_fr, warn_expiry_unit, warn_expiry_value
- uploads.Uploads.camera_stream : type, description
- uploads.Uploads.detail : user, project, id, type, description, start_date, end_date, needed, company, contact_person, contact_role, file, owner, remark, cal.TasksByController
- uploads.Uploads.insert : file, type, project, start_date, end_date, needed, description
- uploads.UploadsByController.insert : file, type, end_date, needed, description
- uploads.UploadsByVolume.detail : user, project, id, type, description, start_date, end_date, needed, company, contact_person, contact_role, file, owner, remark, cal.TasksByController
- uploads.UploadsByVolume.insert : type, description, file, volume, library_file, user
- uploads.Volumes.detail : ref, root_dir, description, overview, uploads.UploadsByVolume, UploadsByVolume
- uploads.Volumes.insert : ref, root_dir, description
- uploads.Volumes.merge_row : merge_to, reason
- users.AllUsers.change_password : current, new1, new2
- users.AllUsers.detail : username, user_type, partner, first_name, last_name, initials, email, language, mail_mode, id, created, modified, users.AuthoritiesGiven, AuthoritiesGiven, remarks, users.AuthoritiesTaken, AuthoritiesTaken, event_type, cal.SubscriptionsByUser, cal.SubscriptionsByUser, cal.TasksByUser, cal.TasksByUser, dashboard.WidgetsByUser, dashboard.WidgetsByUser
- users.AllUsers.insert : username, email, first_name, last_name, partner, language, user_type
- users.AllUsers.merge_row : merge_to, cal_Subscription, comments_Reaction, reason
- users.AllUsers.verify_me : verification_code
<BLANKLINE>
