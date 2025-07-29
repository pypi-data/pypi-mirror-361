===========================
The ``commondata`` packages
===========================

The :mod:`commondata` packages are a pythonic way of sharing structured common
data. They are used by Lino, but you don't need Lino to use them.

You can retrieve such data from Wikidata, but that requires SPARQL knowledge.
And then Wikidata is really complex while typical Lino applications have rather
humble requirements.

For example the list of all countries or currencies of the world. Or when you
are in a given country, the list of cities or well-known organisations or
official price indexes in that country.

Such data changes slowly enough to justify a Python package.

The :mod:`commondata` repository is special in that it contains an executable
script :xfile:`make_code.py`, which generates most of the Python code in this
package.


Main package: https://github.com/lsaffre/commondata
