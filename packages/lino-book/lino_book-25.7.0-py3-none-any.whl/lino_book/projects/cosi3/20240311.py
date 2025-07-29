from lino.api.shell import *
from pprint import pprint

PLACES_IN_ESTONIA = []
for obj in countries.Place.objects.filter(country__isocode="EE"):
    args = [obj.id, obj.name, obj.zip_code]
    if obj.parent is None:
        args.append(None)
    else:
        args.append(obj.parent.id)
    if obj.type is None:
        args.append(None)
    else:
        args.append(obj.type.name)
    PLACES_IN_ESTONIA.append(tuple(args))

pprint(PLACES_IN_ESTONIA)
