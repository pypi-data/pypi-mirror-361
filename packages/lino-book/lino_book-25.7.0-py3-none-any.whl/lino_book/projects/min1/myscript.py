# used by docs/specs/lino.rst
import sys
from lino.api import rt

print(rt.models.contacts.Partner.objects.get(pk=sys.argv[1]))
