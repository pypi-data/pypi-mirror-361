.. doctest docs/specs/humanlinks.rst
.. _lino.specs.humanlinks:
.. _book.plugins.humanlinks:

==============================================
``humanlinks`` : managing family relationships
==============================================

.. currentmodule:: lino_xl.lib.humanlinks

The :mod:`lino_xl.lib.humanlinks` module adds functionality for managing `Links
between humans`_.

It is often used in combination with :mod:`lino_xl.lib.households`.

.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.min9.settings')
>>> from lino.api.doctest import *

Links between humans
====================

The links between humans are directed: they have a :attr:`Link.parent` and a
:attr:`Link.child` (i.e. they go from one person to another person).

Human links also have a type.

Assume that we have two persons F and S, and a human link of type  "parent"
between them, which says that F is the father of S. The link will be of type
:attr:`LinkTypes.parent` and go from F to S.

In the :term:`detail window` of S, we want that link to say "father" (because S
says that F is my *father*). But in the :term:`detail window` of F, we want that
link to say "son" (because F says that S is my *son*).

>>> rt.show(humanlinks.LinkTypes)
======= ================= ================== ==================== ================= ===================
 value   name              male parent text   female parent text   male child text   female child text
------- ----------------- ------------------ -------------------- ----------------- -------------------
 01      parent            Father             Mother               Son               Daughter
 02      adoptive_parent   Adoptive father    Adoptive mother      Adopted son       Adopted daughter
 03      grandparent       Grandfather        Grandmother          Grandson          Granddaughter
 05      spouse            Husband            Wife                 Husband           Wife
 06      friend            Friend             Friend               Friend            Friend
 07      partner           Partner            Partner              Partner           Partner
 08      stepparent        Stepfather         Stepmother           Stepson           Stepdaughter
 09      foster_parent     Foster father      Foster mother        Foster son        Foster daughter
 10      sibling           Brother            Sister               Brother           Sister
 11      cousin            Cousin             Cousin               Cousin            Cousin
 12      uncle             Uncle              Aunt                 Nephew            Niece
 80      relative          Relative           Relative             Relative          Relative
 90      other             Other              Other                Other             Other
======= ================= ================== ==================== ================= ===================
<BLANKLINE>


.. class:: Link

  A link between two persons.

  .. attribute:: parent

    Pointer to the person who is "parent".

  .. attribute:: child

    Pointer to the person who is "child".

  .. attribute:: type

    The type of link.  Pointer to :class:`LinkTypes`.

  .. attribute:: type_as_parent

    Displays :meth:`LinkTypes.as_parent` for this link.

  .. attribute:: type_as_child

    Displays :meth:`LinkTypes.as_child` for this link.

  .. method:: check_autocreate(self, parent, child)

    Check whether there is a human link of type "parent" between the given
    persons. Create one if not. If the child has already another parent of
    same sex, then it becomes a foster child, otherwise a natural child.

    Note that the ages are ignored here, Lino will shamelessly
    create a link even when the child is older than the parent.

    This is called from :meth:`full_clean` of
    :class:`lino_xl.lib.households.Member` to
    automatically create human links between two household
    members.


.. class:: LinkTypes

  The global list of human link types.  This is used as choicelist for the
  :attr:`Link.type` field of a human link.

  The default list contains the following choices:

  .. attribute:: adoptive_parent

      A person who adopts a child of other parents as his or her own child.

  .. attribute:: stepparent

      Someone that your mother or father marries after the marriage
      to or relationship with your other parent has ended

  .. attribute:: foster_parent

      A man (woman) who looks after or brings up a child or children
      as a father (mother), in place of the natural or adoptive
      father (mother). [`thefreedictionary
      <https://www.thefreedictionary.com/foster+father>`_]


.. class:: LinkType

  .. attribute:: symmetric

    Whether this link is symmetric (i.e. text is the same for both directions).
    For example sibling, friend, spouse are symmetric links.

.. class:: LinksByHuman

    Show all links for which this human is either parent or child.

    Display all human links of the master, using both the parent and
    the child directions.

    This is a usage example for having a :meth:`get_request_queryset
    <lino.core.actors.dbtable.Table.get_request_queryset>` method instead of
    :attr:`master_key <lino.core.actors.dbtable.Table.master_key>`.

    It is also a cool usage example for the :meth:`get_table_summary
    <lino.core.actors.Actor.get_table_summary>` method.


Lars
====

Lars Braun is the natural son of Bruno Braun and Eveline Evrard.
Here is what Lars would say about them:

>>> Person = rt.models.contacts.Person
>>> Link = rt.models.humanlinks.Link
>>> lars = Person.objects.get(first_name="Lars", last_name="Braun")
>>> for lnk in Link.objects.filter(child=lars):
...    print(u"{} is my {}".format(lnk.parent,
...         lnk.type.as_parent(lnk.parent)))
Mr Bruno Braun is my Father
Mrs Eveline Evrard is my Mother
Mr Albert Adam is my Foster father
Mrs Françoise Freisen is my Foster mother
Mrs Daniela Radermacher is my Foster mother

Both parents married another partner. These new households
automatically did not create automatic foster parent links between
Lars and the new partners of his natural parents.


.. _reproduce.4185:

Reproduce #4185
========================

The following snippet covers :ticket:`4185` (Human link, "Create relationship as
... Brother but Lino sets it to Father"). It uses `BeautifulSoup
<https://www.crummy.com/software/BeautifulSoup/bs4/doc/>`__. Read the docs in
case you don't yet know this tool.

>>> LinksByHuman = humanlinks.LinksByHuman
>>> ses = rt.login("robin", renderer=settings.SITE.kernel.web_front_ends[0].renderer)
>>> html = tostring(humanlinks.LinksByHuman.get_slave_summary(lars, ses))
>>> soup = BeautifulSoup(html)
>>> print(soup.get_text(" ", strip=True))  #doctest: +NORMALIZE_WHITESPACE
Lars is Son of Eveline EVRARD (40 years), Bruno (41 years) Foster son of Albert
ADAM (41 years), Françoise FREISEN (40 years), Daniela RADERMACHER (unknown)
Create relationship as Father / Son Adoptive father / Adopted son Foster father
/ Foster son Husband Partner Stepfather / Stepson Brother Cousin Uncle / Nephew
Relative Other


>>> links = soup.body.find_all('a')
>>> len(links)
21

The first link after "Create relationship as" is "Father".  This link works as
expected, it pops up a window in which the field :attr:`Link.type` is set to
"Father".

>>> print(links[5].get_text().strip())
Father
>>> print(links[5])  #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
<a href='javascript:Lino.humanlinks.LinksByHuman.insert.run(...
"type": "Father (Mother)"...">Father</a>


Our problem is that when clicking on any of the following links, the pop-up
window still has its field :attr:`Link.type` set to "Father" instead of the link
type on which I clicked.

For example let's click on the "Adopted son" link.

>>> print(links[8].get_text().strip())
Adopted son

>>> print(links[8])  #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
<a href='javascript:Lino.humanlinks.LinksByHuman.insert.run(...
"type": "Adoptive father (Adoptive mother)"...">Adopted son</a>

Here is the code (in the :meth:`get_table_summary
<lino.core.actors.Actor.get_table_summary>` method of
:class:`LinksByHuman`) that creates these links::

  # Buttons for creating relationships:
  if self.insert_action is not None:
      sar = self.insert_action.request_from(ar)
      if sar.get_permission():
          actions = []
          for lt in self.addable_link_types:
              sar.known_values.update(type=lt, parent=obj)
              sar.known_values.pop('child', None)
              btn = sar.ar2button(None, lt.as_parent(obj), icon_name=None)
              actions.append(btn)
              if not lt.symmetric:
                  actions.append('/')
                  sar.known_values.update(type=lt, child=obj)
                  sar.known_values.pop('parent', None)
                  btn = sar.ar2button(None, lt.as_child(obj), icon_name=None)
                  actions.append(btn)
              actions.append(' ')

          if len(actions) > 0:
              elems += [E.br(), gettext("Create relationship as ")] + actions

Note that we use a same action request instance (``sar``) to create all those
links after the text "Create relationship as".

Note how :meth:`ar2button <lino.core.requests.BaseRequest.ar2button>` works.
It creates a temporary instance of :class:`Link` that will never be saved, its
"only" use is to get filled with values, which are used to generate the `status`
information, which is needed to generate the values of the javascript href that
puts the values of the fields into the popup window. This status information is
cached, for performance reasons. But when we change `known_values`, Lino does
not detect automatically that it should update the cached status information.

The problem was that we didn't call :meth:`clear_cached_status
<lino.core.requests.BaseRequest.clear_cached_status>` between subsequent
calls to :meth:`ar2button <lino.core.requests.BaseRequest.ar2button>`.



Don't read this
===============

TypeError: bad argument type: __proxy__('Foster mother')
--------------------------------------------------------

The following snippet caused a traceback "TypeError: bad argument type:
__proxy__('Foster mother')" before :ticket:`5687` (Yet another bad argument
type: __proxy__('Foster mother')).

>>> ses = rt.login("robin") # , renderer=settings.SITE.kernel.default_renderer)
>>> p = contacts.Person.objects.get(first_name="Paul", last_name="Frisch")
>>> ses.renderer = settings.SITE.kernel.default_renderer
>>> ses = humanlinks.LinksByHuman.create_request(parent=ses)
>>> s = ses.show(humanlinks.LinksByHuman, p, display_mode="html")
>>> from etgen.html2rst import html2rst
>>> from lxml.etree import fromstring
>>> e = fromstring(s)
>>> print(html2rst(e))
... #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
Who is... Type To whom...
<BLANKLINE>
<BLANKLINE>
<BLANKLINE>
`Mr Hubert Frisch <...>`__ Father `Mr Paul Frisch <...>`__
<BLANKLINE>
`Mrs Gaby Frogemuth <...>`__ Mother `Mr Paul Frisch <...>`__
<BLANKLINE>
...
<BLANKLINE>
