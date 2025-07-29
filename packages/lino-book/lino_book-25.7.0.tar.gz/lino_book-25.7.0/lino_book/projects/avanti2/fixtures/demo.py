# -*- coding: UTF-8 -*-
# Copyright 2017-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""General demo data for Lino Avanti.

- Course providers and courses

"""

# from django.conf import settings
# from lino.utils import mti
from lino.utils import Cycler  # join_words
from lino.utils.mldbc import babel_named as named
from lino.api import rt, dd, _

from lino.modlib.users.choicelists import UserTypes
from lino.modlib.system.choicelists import Recurrences
from lino_xl.lib.courses.choicelists import EnrolmentStates

course_stages = [
    _("Dispens"),
    _("Eingeschrieben"),
    _("Abgeschlossen"),
    _("Abgebrochen"),
    _("Ausgeschlossen")
]

trends_config = []
trends_config.append((_("Info Integration"), [
    "!Erstgespräch", "Sprachtest", "Einschreibung in Sprachkurs",
    "Einschreibung in Integrationskurs", "!Bilanzgespräch"
]))
trends_config.append((_("Alphabetisation"), course_stages))
trends_config.append((_("A1"), course_stages))
trends_config.append((_("A2"), course_stages))
trends_config.append((_("Citizen course"), course_stages))
trends_config.append((_("Professional integration"), [
    "Begleitet vom DSBE",
    "Begleitet vom ADG",
    "Erwerbstätigkeit",
]))


def objects():

    User = rt.models.users.User
    EventType = rt.models.cal.EventType
    Guest = rt.models.cal.Guest
    GuestRole = rt.models.cal.GuestRole
    GuestStates = rt.models.cal.GuestStates
    EntryStates = rt.models.cal.EntryStates
    Event = rt.models.cal.Event
    Person = rt.models.contacts.Person
    CommentType = rt.models.comments.CommentType
    TrendStage = rt.models.trends.TrendStage
    TrendArea = rt.models.trends.TrendArea

    for area, stages in trends_config:
        ta = named(TrendArea, area)
        yield ta
        for stage in stages:
            kw = dict(trend_area=ta)
            if stage[0] == "!":
                stage = stage[1:]
                kw.update(subject_column=True)
            yield named(TrendStage, stage, **kw)

    yield EventType(**dd.str2kw('name', _("First contact")))

    kw = dd.str2kw('name', _("Lesson"))
    kw.update(dd.str2kw('event_label', _("Lesson")))
    event_type = EventType(**kw)
    yield event_type

    pupil = named(GuestRole, _("Pupil"))
    yield pupil
    yield named(GuestRole, _("Assistant"))

    yield named(CommentType, _("Phone call"))
    yield named(CommentType, _("Visit"))
    yield named(CommentType, _("Individual consultation"))
    yield named(CommentType, _("Internal meeting"))
    yield named(CommentType, _("Meeting with partners"))

    yield User(username="nathalie", user_type=UserTypes.user)
    yield User(username="nelly", user_type=UserTypes.user)
