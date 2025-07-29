# -*- coding: UTF-8 -*-
# Copyright 2013-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _


class EntryStates(dd.Workflow):
    pass


add = EntryStates.add_item
add('10', _("New"), 'new', button_text="☐")
add('20', _("Started"), 'started', button_text="⚒")
add('30', _("Done"), 'done', button_text="☑")
add('40', _("Sleeping"), 'sleeping', button_text="☾")
add('50', _("Cancelled"), 'cancelled', button_text="☒")
