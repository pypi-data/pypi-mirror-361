=========================================
Generating HTML
=========================================

Although Lino is made to *avoid* writing HTML, CSS and JavaScript, there are
cases where even the most design-agnostic :term:`application developer`  is
asked to provide some "rich" ("formatted") text.  And the most natural and best
known language for writing rich text remains HTML.

For example the return value of a :class:`DisplayField
<lino.core.fields.DisplayField>` or a :class:`HtmlBox
<lino.core.fields.HtmlBox>`, or the :meth:`get_table_summary
<lino.core.actors.Actor.get_table_summary>` method are places where the
application developer is expected to write "rich text" that contains formatting,
hyperlinks, widgets.

But how to generate HTML from application code?

You might ask "Where's the problem?" Python is a great language for generating
HTML, you just do it. For example::

  class Message:
      title = "Invitation"
      name = "Joe"

      def as_html(self):
        return f"<h1>{self.title}</h1><p>Hello, {self.name}!</p>"

  p = Message()
  print(p.as_html())


The problem in above example is that it forgets to escape the `title` and
`name`. If a `title` or `name` contains HTML special characters like ``<`` or
``&``, they might not get rendered correctly.

Another problem is that a valid HTML text can get escaped by mistake, because of
a bug or some API change.

The problem with these problems is that they can be difficult to track and to
fix.

Lino exposes two different approaches for handling these challenges: The
`ElementTree <https://docs.python.org/3/library/xml.etree.elementtree.html>`__
module of the Standard Library and Django's `safestring tools
<https://docs.djangoproject.com/en/5.0/ref/utils/#module-django.utils.html>`_.

Both approaches introduce some kind of "discipline": their usage requires a bit
of additional learning, but as a reward they increase stability of your code.

With ElementTree, the above example becomes::

  from lino.utils.html import E, tostring

  class Message:
      title = "Invitation"
      name = "Joe"

      def as_html(self):
        return [E.h1(self.title), E.p(f"Hello, {self.name}!")]

  p = Message()
  print(tostring(p.as_html()))

See :ref:`etgen` for more information about this approach.

With Django's ``safestring`` tools it becomes::

  from django.utils.html import format_html

  class Message:
      title = "Invitation"
      name = "Joe"

      def as_html(self):
        return format_html("<h1>{}</h1><p>Hello, {}!</p>", self.title, self.name)

  p = Message()
  print(p.as_html())


As a Lino :term:`application developer` you should get used to both approaches.
