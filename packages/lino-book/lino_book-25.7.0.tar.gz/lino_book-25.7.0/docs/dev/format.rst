.. doctest docs/dev/format.rst
.. include:: /shared/include/defs.rst
.. _dev.format:

=================================
How to represent a database row
=================================

Lino offers a number of ways to customize how a :term:`database row` is to be
presented to the :term:`end user`.

.. note:: This page needs more work.

.. contents::
    :depth: 1
    :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.min1.startup import *
>>> from django.utils import translation
>>> from django.db.models import Q

Summary items, paragraphs and pages
===================================

Lino differentiates three levels of representation for a database row: "summary
item", "paragraph" and "page".


.. _dev.row_template:

Customize the summary item
===========================

When you don't give any instructions at all, Lino uses the :meth:`__str__`
method to represent a database row as a summary item.

More precisely, Lino calls :meth:`Model.as_str` when a context is known.

A context-sensitive variant of :meth:`__str__`.
The plain-text representation of a
database row can vary depending on whether certain elements are considered
"obvious".

For example when you are displaying a list of the periods in a given fiscal
year, it would be redundant to print the year for each of them. So the
StoredPeriod.as_str() method does not mention the year when
ar.is_obvious_field("year") returns True or when it is part of the current
fiscal year.

Other examples are the country of a city.

The :meth:`Model.as_summary_item` method is often customized on models for which
there is no :term:`detail window`. For example lists.Member, contacts.Role or
topics.Tag. These models have in common that they represent a simple relation.


.. currentmodule:: lino.core.model

.. class:: Model
  :noindex:

  .. method:: __str__(self)

    Return a translatable text that describes this :term:`database row`.

  .. method:: as_str(self, ar)

    Return a translatable text that describes this :term:`database row`. Unlike
    :meth:`__str__` this method gets an :term:`action request` when it is
    called, so it knows the context.

  .. method:: get_str_words(self, ar)

    Yield a series of words that describe this database row in plain text.

    Called by the default implementation of :meth:`as_str`, which then joins all
    words by a space (``" "``) into a single string.

  .. method:: as_summary_item(self, ar, text=None, **kwargs)

    Return a HTML element that represents this database row in a data window in
    display mode "summary".

    Default implementation calls :meth:`as_str` and passes this as ``text`` to
    :meth:`ar.obj2html <lino.api.core.Request.obj2html>`.

    Examples see :ref:`as_summary_item`.


.. currentmodule:: lino.core.actors

.. class:: Actor
  :noindex:

  .. attribute:: row_template

    A format template to make a plain text description of a row of this table
    in.

    Default value is `None`. If this is a `str` the default implementation of
    :meth:`Model.as_str` will parse by calling its :meth:`format` method with
    one keyword argument ``row``, which refers to the :term:`database row` being
    represented.

    Example::

      class RatingsByResponse(ChallengeRatings):
          ...
          row_template = '{row.rating}/{row.challenge.max_rating} {row.challenge.skill}'

.. _dev.as_paragraph:

Represent a row depending on the context
========================================

The :class:`Model` class has three methods used to represent a :term:`database
row`.

- :meth:`as_summary_item <Model.as_summary_item>` represents it as a **summary item**.
- :meth:`as_paragraph <Model.as_paragraph>` represents it as a single **paragraph**.
- :meth:`as_page <Model.as_page>` represents it as a whole **web page**.

Both methods require an :term:`action request` as argument, and the result may
vary depending on this action request. For example a partner model of a given
application may want to also show the city of a partner unless city is an
:term:`obvious field`::

  def as_summary_item(self, ar, *text, **kwargs):
      s = ar.obj2htmls(self)
      if self.city and not ar.is_obvious_field("city"):
          s = format_html("{} from {}", s, ar.obj2htmls(self.city))
      return s

.. glossary::

  obvious field

    A field for which the value is the same for alll rows of a table.


Default implementation returns :meth:`ar.obj2htmls(self)
<lino.core.requests.BaseRequest.obj2htmls>` or (when ``ar`` is `None`)
``str(self)``.

The returned HTML string should contain a single paragraph and must not include
any surrounding ``<li>`` or ``<p>`` or ``<td>`` tag (these will be added by the
caller as needed).


>>> ar = rt.login("robin")
>>> hans = contacts.Person.objects.all().first()
>>> hans.as_paragraph(ar)
'<a href="…">Mr Hans Altenberg</a> (Aachener Straße, 4700 Eupen)'

>>> robin = ar.get_user()
>>> robin.as_paragraph(ar)
'<a href="…">Robin Rood</a>'

Lino usually doesn't call this method directly, it mostly calls the
:meth:`row_as_paragraph <lino.core.tables.AbstractTable.row_as_paragraph>`
method of a :term:`data table`, and this method, by default, calls our model
method. The following two calls give the same results as the former ones:

>>> contacts.Persons.row_as_paragraph(ar, hans)
'<a href="…">Mr Hans Altenberg</a> (Aachener Straße, 4700 Eupen)'

>>> users.Users.row_as_paragraph(ar, robin)
'<a href="…">Robin Rood</a>'

You can customize this by overriding either the model or the data table.

For example, :class:`lino.modlib.users.UsersOverview` customizes the data table::

    @classmethod
    def row_as_paragraph(cls, ar, self):
        pv = dict(username=self.username)
        if settings.SITE.is_demo_site:
            pv.update(password="1234")
        btn = rt.models.about.About.get_action_by_name("sign_in")
        btn = btn.request(
            action_param_values=pv, renderer=settings.SITE.kernel.default_renderer
        )
        btn = btn.ar2button(label=self.username)
        items = [tostring(btn), " : ", str(self), ", ", str(self.user_type)]
        if self.language:
            items += [
                ", ",
                "<strong>{}</strong>".format(
                    settings.SITE.LANGUAGE_DICT.get(self.language)
                ),
            ]
        return mark_safe("".join(items))

That's why we get:

>>> users.UsersOverview.row_as_paragraph(ar, robin)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
'<a href="javascript:Lino.about.About.sign_in.run(null,{
&quot;base_params&quot;: {  }, &quot;field_values&quot;: { &quot;password&quot;:
&quot;1234&quot;, &quot;username&quot;: &quot;robin&quot; }, &quot;record_id&quot;:
null })" style="text-decoration:none">robin</a> : Robin Rood, 900
(Administrator), <strong>English</strong>'

There is also a shortcut method :meth:`row_as_paragraph
<lino.core.tablerequests.TableRequest.row_as_paragraph>` on an action request.


Customize the title of an actor
=================================

.. currentmodule:: lino.core.actors

.. class:: Actor
  :noindex:

  .. attribute:: label

    The text to appear e.g. on a button that will call the default action of an
    actor.  This attribute is *not* inherited to subclasses.  If this is `None`
    (the default value), Lino will call :meth:`get_actor_label`.

  .. method:: get_title(self, ar)

    Return the title of this actor for the given action request `ar`.

    The default implementation calls :meth:`get_title_base` and
    :meth:`get_title_tags` and returns a string of type `BASE [
    (TAG, TAG...)]`.

    Override this if your table's title should mention for example
    filter conditions.  See also :meth:`Table.get_title
    <lino.core.dbtables.Table.get_title>`.

  .. method:: get_actor_label(self)

     Return the label of this actor.

  .. attribute:: title

    The text to appear e.g. as window title when the actor's default
    action has been called.  If this is not set, Lino will use the
    :attr:`label` as title.

  .. attribute:: button_text

    The text to appear on buttons of a ShowSlaveTable action for this
    actor.

  .. method:: get_title_base(self, ar)

    Return the base part of the title. This should be a translatable
    string. This is called by :meth:`get_title` to construct the
    actual title.

    It is also called by
    :meth:`lino.core.dashboard.DashboardItem.render_request`

  .. method:: get_title_tags(self, ar)

    Yield a list of translatable strings to be added to the base part
    of the title. This is called by :meth:`get_title` to construct
    the actual title.


Miscellaneous
=============================================

.. currentmodule:: lino.core.model

.. class:: Model
  :noindex:

  .. method:: as_paragraph(self, ar)

    Return a safe HTML string that represents this :term:`database row` as a
    paragraph.

    See :ref:`dev.as_paragraph`.

    This is called by the default implementation of
    :meth:`lino.core.actors.Actor.row_as_paragraph`.

  .. attribute:: preferred_foreignkey_width = None

    The default preferred width (in characters) of widgets that display a
    :term:`foreign key` to this model.

    If not specified, the default default `preferred_width`
    for ForeignKey fields is *20*.

  .. method:: set_widget_options(self, name, **options)

    Set default values for the :term:`widget options` of a given element.

  .. method:: get_overview_elems(self, ar)

    Return a list of HTML elements to be shown in :attr:`overview` field.


Customize actor methods and attributes
======================================

See
:doc:`/dev/layouts/more`.
:doc:`/dev/layouts/more`.


When you define a :attr:`detail_layout`, you probably also want to define an
:attr:`insert_layout`.

When a table has no :attr:`insert_layout`, it won't have any (+) button
(|insert|) to create a new row via a dialog window, but users can still
create rows by writing into the :term:`phantom row`. Example of this is
:class:`lino_xl.lib.courses.Topics` which has a detail layout with slave
tables, but the model itself has only two fields (id and name) and it makes
no sense to have an insert window.

.. currentmodule:: lino.core.actors

.. class:: Actor
  :noindex:

  .. attribute:: detail_layout

    Define the layout to use for the detail window.  Actors with
    :attr:`detail_layout` will get a `show_detail` action.

  .. attribute:: insert_layout

    Define the form layout to use for the insert window.

Miscellaneous
=============

.. class:: Actor
  :noindex:

  .. classmethod:: get_row_classes(self, ar)

    If a method of this name is defined on an actor, then it must
    be a class method which takes an :class:`ar
    <lino.core.requests.BaseRequest>` as single argument and
    returns either None or a string "red", "green" or "blue"
    (todo: add more colors and styles). Example::

        @classmethod
        def get_row_classes(cls,obj,ar):
            if obj.client_state == ClientStates.newcomer:
                return 'green'

    Defining this method will cause an additional special
    `RowClassStoreField` field in the :class:`lino.core.Store`
    objects of this actor.

  .. attribute:: details_of_master_template

    Used to build the title of a request on this table when it is a
    slave table (i.e. :attr:`master` is not None). The default value
    is defined as follows::

        details_of_master_template = _("%(details)s of %(master)s")

  .. attribute:: display_mode

    The default :term:`display mode` to use when rendering this table.

    See :doc:`/dev/display_modes`.


  .. attribute:: window_size = None

    Set this to a tuple of `(height, width)` to have this actor
    display in a modal non-maximized window.

    - `height` must be either an integer expressing a number of rows
      or the string "auto".  If it is auto, then the window should not
      contain any v-flexible component.

    - `width` must be either an integer expressing a number of rows
      or a string of style "90%".

      Note that a relative width will be converted to a number of
      pixels when the window is rendered for the first time. That is,
      if you close the window, resize your browser window and reopen
      the same window, you will get the old size.

  .. attribute:: insert_layout_width = 60

    When specifying an :attr:`insert_layout` using a simple a multline
    string, then Lino will instantiate a FormPanel with this width.

  .. attribute:: hide_window_title = False

    This is set to `True` e.h. in home pages
    (e.g. :class:`lino_welfare.modlib.pcsw.models.Home`).

  .. attribute:: hide_headers = False

    Set this to True in order to hide the column headers.

    This is ignored when the table is rendered in an ExtJS grid.

  .. attribute:: hide_top_toolbar = False

    Whether a Detail Window should have navigation buttons, a "New"
    and a "Delete" buttons.  In ExtJS UI also influences the title of
    a Detail Window to specify only the current element without
    prefixing the Tables's title.

    If used in a grid view in React will remove the top toolbar
    and selection tools.

    This option is `True` in
    :class:`lino.models.SiteConfigs`,
    :class:`lino_welfare.pcsw.models.Home`,
    :class:`lino.modlib.users.desktop.MySettings`,
    :class:`lino_xl.cal.CalenderView`.

  .. attribute:: simple_slavegrid_header

    Whether to simplify the slave grid in a detail.

    This is used only in :class:`lino.modlib.comments.RepliesByComment`
    and should probably be replaced by something else.

  .. attribute:: preview_limit

    The maximum number of rows to fetch when this table is being
    displayed in "preview mode", i.e. (1) as a slave table in a detail
    window or (2) as a dashboard item (:meth:`get_dashboard_items
    <lino.core.site.Site.get_dashboard_items>`) in
    :xfile:`admin_main.html`.

    The default value for this is the :attr:`preview_limit
    <lino.core.site.Site.preview_limit>` class attribute of your
    :class:`Site <lino.core.site.Site>`, which itself has a hard-coded
    default value of 15 and which you can override in your
    :xfile:`settings.py`.

    If you set this to `0`, preview requests for this table will
    request all rows.  Since preview tables usually have no paging
    toolbar, that's theoretically what we want (but can lead to waste
    of performance if there are many rows).
    When this is 0, there will be no no paginator.

    In React if set to `0` the paging toolbar which usually is
    present in the detail view, will be removed, as it has no use, as
    all rows will be displayed.

    Test case and description in the tested docs of :ref:`cosi`.

    For non-table actors this is always `None`.

  .. attribute:: help_text = None

    A help text that shortly explains what the default action of this
    actor does.  In a graphical user interface this will be rendered
    as a **tooltip** text.

    If this is not given by the code, Lino will potentially set it at
    startup when loading the :xfile:`help_texts.py` files.

  .. method:: summary_row(cls, ar, obj, **kw)

    Return a HTML representation of the given data row `obj` for usage in a
    summary panel.

    The default implementation calls
    :meth:`lino.core.model.Model.summary_row`.

.. _dev.actors.react:

React-specific actor attributes
===============================

.. currentmodule:: lino.core.actors

.. class:: Actor
  :noindex:

  .. attribute:: use_detail_param_panel

      Whether to show parameter panel in a detail view.

  .. attribute:: use_detail_params_value

      Whether to use the parent's parameter values in grid

  .. attribute:: react_big_search

    Whether the quick search field should be rendered on a line on its own.

    This is set to `True` only for `contacts.Persons` in :ref:`amici`
    and should probably be replaced by something else.

  .. attribute:: max_render_depth

    This is not used.

  .. attribute:: paginator_template

    Paginator elements can be customized using the template property using the
    predefined keys, default value is "FirstPageLink PrevPageLink PageLinks
    NextPageLink LastPageLink RowsPerPageDropdown". Here are the available
    elements that can be placed inside a paginator.

    FirstPageLink
    PrevPageLink
    PageLinks
    NextPageLink
    LastPageLink
    RowsPerPageDropdown
    CurrentPageReport

    This is used only in :class:`lino.modlib.comments.RepliesByComment`
    and should probably be replaced by something else.

  .. attribute:: hide_if_empty

    Don't show any DataTable at all when there is no data.

    This is used only in :class:`lino.modlib.comments.RepliesByComment`
    and should probably be replaced by something else.



.. _dev.actors.sums:

Showing, hiding and formatting sums
===================================

.. currentmodule:: lino.core.actors

.. class:: Actor
  :noindex:

  .. attribute:: sum_text_column = 0

    The index of the column that should hold the text to display on the totals
    row (returned by :meth:`get_sum_text`).

  .. method:: get_sum_text(self, ar, sums)

    Return the text to display on the totals row.
    The default implementation returns "Total (N rows)".



Lino automatically assumes that you want a sum for every numeric field.
Sometimes this is now waht you want.  In that case you can say::

    MyModel.set_widget_option('year", show_sum=False)

When a table has at least one column with a sum, Lino adds a "totals" line when
printing the table.  The first empty column in that line will receive a text
"Total (9 rows)".  That text is customizable by overriding
:meth:`Actor.get_sum_text`.

If you don't want that text to appear in the first empty column, you can
specify a value for :attr:`Actor.sum_text_column`.  Usage example:  the first
screenshot below is without :attr:`Actor.sum_text_column`, the second is with
:attr:`sum_text_column` set to 2:

.. image:: sum_text_column_a.png
.. image:: sum_text_column_b.png


Start at bottom
===============

.. currentmodule:: lino.core.actors

.. class:: Actor
  :noindex:

  .. attribute:: start_at_bottom

    When set to True, this table will start at the last page rather than on the
    first page.

    Usage example is :class:`lino_xl.lib.trading.InvoicesByJournal`.

    Doctests in :doc:`/specs/ajax`.
