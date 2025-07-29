.. doctest docs/dev/ar.rst
.. _dev.ar:

=====================
Using action requests
=====================

The traditional variable name for action requests in application code and method
signatures is ``ar``.  Except for the plain `BaseRequest` instance returned by
:func:`rt.login <lino.api.rt.login>`, which is sometimes called ``ses`` because
you can imagine it as a session.

As a rough approximation you can say that every incoming web request gets
wrapped into an action request.  The ActionRequest adds some more information
about the context (like the "renderer" being used) and provides methods for
communicating with the user.

But there are exceptions to this approximaton.

- :meth:`show <lino.core.requests.BaseRequest.show>`

- :meth:`set_response <lino.core.requests.BaseRequest.set_response>`

- :meth:`ba.request_from <lino.core.boundaction.BoundAction.request_from>`
- :meth:`lino.core.request.get_permission`
- :meth:`lino.core.request.set_action_param_values`
- :meth:`lino.core.request.ar2button`


Iterating over table requests

A table request has two iterators: :attr:`data_iterator` and
:attr:`sliced_data_iterator`.

>>> from lino_book.projects.min1.startup import *

>>> rt.show('countries.Places', limit=10)
============ ======================== ================== ================== ============ ========== ================================
 Country      Designation              Designation (de)   Designation (fr)   Place Type   zip code   Part of
------------ ------------------------ ------------------ ------------------ ------------ ---------- --------------------------------
 Bangladesh   Cumilla                                                        City
 Bangladesh   Dhaka                                                          City
 Belgium      Aalst                    Aalst              Alost              City         9300       Flandre de l'Est / Ostflandern
 Belgium      Aalst-bij-Sint-Truiden                                         Village      3800       Limbourg / Limburg
 Belgium      Angleur                                                        City         4031
 Belgium      Ans                                                            City         4430
 Belgium      Anvers                   Antwerpen          Anvers             Province
 Belgium      Baardegem                                                      Village      9310       9300 Aalst / Alost
 Belgium      Baelen                   Baelen             Baelen             City         4837       Liège / Lüttich
 Belgium      Blégny                                                         City         4670
============ ======================== ================== ================== ============ ========== ================================
<BLANKLINE>

>>> rt.show('countries.Places', offset=5, limit=3)
========= ============= ================== ================== ============ ========== ====================
 Country   Designation   Designation (de)   Designation (fr)   Place Type   zip code   Part of
--------- ------------- ------------------ ------------------ ------------ ---------- --------------------
 Belgium   Ans                                                 City         4430
 Belgium   Anvers        Antwerpen          Anvers             Province
 Belgium   Baardegem                                           Village      9310       9300 Aalst / Alost
========= ============= ================== ================== ============ ========== ====================
<BLANKLINE>

>>> rt.show('countries.Places', offset=-5, limit=3)
Traceback (most recent call last):
...
ValueError: Negative indexing is not supported.

>>> ar = countries.Places.create_request(offset=5, limit=3)  #doctest: +ELLIPSIS

>>> print(' '.join([pl.name for pl in ar]))
Cumilla Dhaka Aalst Aalst-bij-Sint-Truiden Angleur Ans Anvers Baardegem Baelen Blégny Brabant flamant Brabant wallon Brussels Burdinne Burg-Reuland Butgenbach Büllingen Cerfontaine Cuesmes Erembodegem Eupen Flandre de l'Est Flandre de l'Ouest Gijzegem Hainaut Herdersem Hofstade Kelmis Kettenis La Reid Limbourg Liège Liège Luxembourg Meldert Mons Moorsel Mortier Namur Namur Nieuwerkerken Nispert Ostende Ottignies Ouren Raeren Recht Sankt Vith Thieusies Trembleur Aachen Berlin Cologne Hamburg Monschau Munich Harju Kesklinn Narva Pärnu Pärnu Põhja-Tallinn Rapla Rapla Tallinn Tartu Vigala Ääsmäe Marseille Metz Nancy Nice Paris Strasbourg Amsterdam Breda Den Haag Maastricht Rotterdam Utrecht

>>> print(' '.join([pl.name for pl in ar.sliced_data_iterator]))
Ans Anvers Baardegem


(TODO: write much more text. we would need a good explanation of how
to create subrequests etc.)


Pointing to a database object
=============================

Every database object (in Lino) has a method :meth:`as_summary_item
<lino.core.model.Model.as_summary_item>`, which you can call to generate a HTML tree
element that is going to output a `<a href>` tag.  (Read more about where you
need them in :doc:`html`.)

>>> ar = rt.login('robin')
>>> obj = contacts.Person.objects.get(pk=51)
>>> def example(x):
...     print(tostring(x))

Basic usage is:

>>> example(ar.obj2html(obj))
<a href="…">Mr Erwin Emontspool</a>

When you don't specify a `text` for the link, obj2html calls the object's
:meth:`__str__` method and use the result as `text`.  You can specify your own
``text`` by giving a second positional argument:

>>> example(ar.obj2html(obj, "Foo"))
<a href="…">Foo</a>

.. note::

    The URL ("…" in above examples) is something you aren't supposed to worry
    about as an :term:`application developer`. It depends on the :term:`front
    end`, which is known to the action request as :attr:`renderer`. In a tested
    document the default :attr:`renderer` is a
    :class:`lino.core.renderer.TextRenderer`, which uses these fake URLs "…". If
    you manuall set a real renderer, you'll get real URLs.

    >>> ar.renderer  #doctest: +ELLIPSIS
    <lino.core.renderer.TextRenderer object at ...>
    >>> real_renderer = settings.SITE.kernel.default_renderer
    >>> real_renderer  #doctest: +ELLIPSIS
    <lino.modlib.extjs.ext_renderer.ExtRenderer object at ...>
    >>> ar2 = rt.login("robin", renderer=real_renderer)
    >>> example(ar2.obj2html(obj))
    <a href="javascript:Lino.contacts.Persons.detail.run(null,{ &quot;record_id&quot;: 51 })" style="text-decoration:none">Mr Erwin Emontspool</a>

    For the remaining examples in this document we use the text renderer.

Your text should usually be a translatable string:

>>> from lino.ad import _
>>> with translation.override("de"):
...     example(ar.obj2html(obj, _("Today")))
<a href="…">Heute</a>

Your text will be escaped:

>>> example(ar.obj2html(obj, "Foo & bar"))
<a href="…">Foo &amp; bar</a>

That's why the following does not yield the expected result:

>>> example(ar.obj2html(obj, "<img src=\"foo\"/>"))
<a href="…">&lt;img src="foo"/&gt;</a>

In above situation you can specify another HTML tree element as
"text". Here is what you expected:

>>> example(ar.obj2html(obj, E.img(src="foo")))
<a href="…"><img src="foo"/></a>

You can also specify a tuple with text chunks:

>>> text = ("Formatted ", E.b("rich"), " text")
>>> example(ar.obj2html(obj, text))
<a href="…">Formatted <b>rich</b> text</a>

If you want your text to be that of another database object, then you
must explicitly call that object's :meth:`__str__` method:

>>> other = contacts.Person.objects.get(pk=52)
>>> example(ar.obj2html(obj, str(other)))
<a href="…">Mrs Erna Emonts-Gast</a>

More examples:

>>> with translation.override("de"):
...     example(ar.obj2html(obj, (_("Monday"), " & ", _("Tuesday"))))
<a href="…">Montag &amp; Dienstag</a>


.. _as_summary_item:

The ``summary`` display mode
============================




Programmatically doing requests
===============================

>>> u = rt.models.users.User.objects.get(username="robin")
>>> r = rt.models.contacts.Persons.request(
...     user=u, renderer=dd.plugins.extjs.renderer)
>>> print(r.renderer.request_handler(r))
Lino.contacts.Persons.grid.run(null,{ "base_params": {  }, "param_values": { "end_date": null, "observed_event": null, "start_date": null } })

.. Lino.contacts.Persons.grid.run(null,{ "base_params": {  }, "param_values": { "aged_from": null, "aged_to": null, "end_date": null, "gender": null, "genderHidden": null, "observed_event": null, "start_date": null } })

.. Above test changed with 20200430 and I didn't understand why.
