# Local customizations: Replace the label "Workflow" on invoices by "State". And
# change the hotkey used to toggle the state of an invoice from Ctrl+X to
# Ctrl+F2

# don't forget to import the default user_types_module:
from lino_cosi.lib.cosi.user_types import *

from django.utils.translation import gettext_lazy as _
from lino.core.keyboard import Hotkey
from lino.core.inject import update_field
from lino_xl.lib.accounting.mixins import LedgerRegistrable

# Ctrl+Y works, but CtrlF2 seems to not be configurable, at least in Firefox:
# LedgerRegistrable.toggle_state.hotkey = Hotkey(code="KeyY", ctrl=True)
# LedgerRegistrable.toggle_state.hotkey = Hotkey(code="F2", ctrl=True)

from lino_xl.lib.vat.mixins import VatDocument
update_field(VatDocument, 'workflow_buttons', verbose_name=_("State"))
