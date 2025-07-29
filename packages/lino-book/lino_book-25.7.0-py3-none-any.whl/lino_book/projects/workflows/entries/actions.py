# Copyright 2013-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.utils.translation import gettext_lazy as _
from lino.api import dd, rt
from lino.modlib.notify.actions import NotifyingAction


class StartEntry(dd.ChangeStateAction):
    label = _("Start")
    help_text = _(
        "This action is not allowed when company, body or subject is empty.")
    required_states = 'new cancelled'

    def get_action_permission(self, ar, obj, state):
        # cannot start entries with empty company, subject or body fields
        if not obj.company or not obj.subject or not obj.body:
            return False
        return super(StartEntry, self).get_action_permission(ar, obj, state)


class FinishEntry(StartEntry):
    icon_name = 'accept'
    label = _("Finish")
    required_states = 'new started'
    help_text = _(
        "Inherts from StartEntry and thus is not allowed when company, body or subject is empty."
    )


class WakeupEntry(dd.ChangeStateAction, NotifyingAction):
    label = _("Reopen")

    # label = _("Wake up")
    # required_states = 'sleeping'
    # in our example, waking up an antry will send a notification

    def get_notify_recipients(self, ar, obj):
        if not obj.state.name in ('done', 'cancelled'):
            return
        for u in rt.models.users.User.objects.all():
            yield (u, u.mail_mode)

    def get_notify_subject(self, ar, obj):
        return _("Entry %s has been reactivated!") % obj
