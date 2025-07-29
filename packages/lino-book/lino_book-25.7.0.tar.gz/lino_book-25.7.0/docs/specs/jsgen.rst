.. doctest docs/specs/jsgen.rst
.. _lino.specs.jsgen:

========================================
Utilities for generating JavaScript code
========================================


>>> from lino import startup
>>> startup('lino_book.projects.min9.settings')
>>> from lino.api.doctest import *

Introduction
============

Some basic examples are in the docstring :mod:`lino.utils.jsgen`.

>>> from lino.utils.jsgen import py2js, js_line

Another example...

>>> def onReady(name):
...     yield js_line("hello = function() {")
...     yield js_line("console.log(%s)" % py2js("Hello, " + name + "!"))
...     yield js_line("}")
>>> print(py2js(onReady("World")))
hello = function() {
console.log("Hello, World!")
}
<BLANKLINE>


And yet another example (`/blog/2012/0208`)...

>>> chunk = '<a href="javascript:alert({&quot;record_id&quot;: 122 })">Test</a>'
>>> print(py2js(chunk))
"<a href=\"javascript:alert({&quot;record_id&quot;: 122 })\">Test</a>"

>>> data_record = dict(
...   title="Upload \"Aufenthaltserlaubnis\"",
...   data=dict(owner=chunk))
>>> print(py2js(data_record))
{ "data": { "owner": "<a href=\"javascript:alert({&quot;record_id&quot;: 122 })\">Test</a>" }, "title": "Upload \"Aufenthaltserlaubnis\"" }
>>> response = dict(
...   message="Upload \"Aufenthaltserlaubnis\" wurde erstellt.",
...   success=True,
...   data_record=data_record)
>>> print(py2js(response)) #doctest: +NORMALIZE_WHITESPACE
{ "data_record": { "data": { "owner": "<a href=\"javascript:alert({&quot;record_id&quot;: 122 })\">Test</a>" }, "title": "Upload \"Aufenthaltserlaubnis\"" }, "message": "Upload \"Aufenthaltserlaubnis\" wurde erstellt.", "success": true }




Dates before 1900 and JSON
==========================

Representing dates before year 1900 via the web interface failed in
versions before 2017-07-27, but this is now fixed.

>>> import datetime
>>> from lino.utils.jsgen import py2js
>>> print(py2js(datetime.date(2017, 7, 27)))
"27.07.2017"
>>> print(py2js(datetime.date(17, 7, 27)))
"27.07.17"


What is a table handle and why do we need it?
=============================================

>>> from lino.utils.jsgen import declare_vars
>>> tbl = contacts.Persons
>>> print(repr(tbl))
lino_book.projects.min9.modlib.contacts.models.Persons

>>> th = tbl.get_handle()
>>> print(repr(th))  #doctest: +ELLIPSIS
<lino.core.tables.TableHandle object at ...>

>>> ll = th.get_grid_layout()
>>> with users.UserTypes.admin.context():
...     print("\n".join(declare_vars(ll.main)))  #doctest: +ELLIPSIS
var main_grid... = new Lino.contacts.Persons.GridPanel({ "containing_panel": this, "hideCheckBoxLabels": true, "listeners": { "render": Lino.quicktip_renderer("Persons","Persons (contacts.contacts.Persons) : Shows all persons.") }, "params_panel_hidden": true });
