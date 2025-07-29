.. doctest docs/specs/memo.rst
.. _dev.memo:

==========================
``memo`` : The memo parser
==========================

The :mod:`lino.modlib.memo` plugin adds application-specific markup to
:doc:`text fields </dev/textfield>`. One facet of this plugin is a simple
built-in :term:`memo markup` format, another facet are :term:`suggesters
<suggester>`. A usage example is documented in :doc:`/apps/noi/memo`.

.. currentmodule:: lino.modlib.memo

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *

Glossary
========

.. glossary::

  suggester

    A suggester is when you define that a
    "trigger text" will pop up a list of suggestions for auto-completion.  For
    example ``#`` commonly refers to a topic or a ticket, or ``@`` refers to
    another site user.

  memo markup

    A simple markup language that replaces "memo commands" (expressions between
    [square brackets]) by their result. See :ref:`memo.builtin`.

Basic usage
===========

The :class:`lino.modlib.memo.parser.Parser` is a simple markup parser that
expands "commands" found in an input string to produce a resulting output
string.  Commands are in the form ``[KEYWORD ARGS]``.  The caller defines
itself all commands, there are no predefined commands.

Let's instantiate parser:

>>> from lino.modlib.memo.parser import Parser
>>> p = Parser()

We declare a **command handler** function `url2html` and register it:

>>> def url2html(parser, s, cmdname, mentions, context):
...     print("[DEBUG] url2html() got %r" % s)
...     if not s: return "XXX"
...     url, text = s.split(None,1)
...     return '<a href="%s">%s</a>' % (url,text)
>>> p.register_command('url', url2html)

The intended usage of our example handler is ``[url URL TEXT]``, where
URL is the URL to link to, and TEXT is the label of the link:

>>> print(p.parse('This is a [url http://xyz.com test].'))
[DEBUG] url2html() got 'http://xyz.com test'
This is a <a href="http://xyz.com">test</a>.

A command handler will be called with one parameter: the portion of
text between the KEYWORD and the closing square bracket.  Not
including the whitespace after the keyword.  It must return the text
which is to replace the ``[KEYWORD ARGS]`` fragment.  It is
responsible for parsing the text that it receives as parameter.

If an exception occurs during the command handler, the final exception
message is inserted into the result.

To demonstrate this, our example implementation has a bug, it doesn't
support the case of having only a URL without TEXT:

>>> print(p.parse('This is a [url http://xyz.com].'))  #doctest: +ELLIPSIS
[DEBUG] url2html() got 'http://xyz.com'
This is a [ERROR ... in ...'[url http://xyz.com]' at position 10-30].

We use an ellipsis in above code because the error message varies with Python
versions.

Newlines preceded by a backslash will be removed before the command
handler is called:

>>> print(p.parse('''This is [url http://xy\
... z.com another test].'''))
[DEBUG] url2html() got 'http://xyz.com another test'
This is <a href="http://xyz.com">another test</a>.

The whitespace between the KEYWORD and ARGS can be any whitespace,
including newlines:

>>> print(p.parse('''This is a [url
... http://xyz.com test].'''))
[DEBUG] url2html() got 'http://xyz.com test'
This is a <a href="http://xyz.com">test</a>.

The ARGS part is optional (it's up to the command handler to react
accordingly, our handler function returns XXX in that case):

>>> print(p.parse('''This is a [url] test.'''))
[DEBUG] url2html() got ''
This is a XXX test.

The ARGS part may contain pairs of square brackets:

>>> print(p.parse('''This is a [url
... http://xyz.com test with [more] brackets].'''))
[DEBUG] url2html() got 'http://xyz.com test with [more] brackets'
This is a <a href="http://xyz.com">test with [more] brackets</a>.

Fragments of text between brackets that do not match any registered
command will be left unchanged:

>>> print(p.parse('''This is a [1] test.'''))
This is a [1] test.

>>> print(p.parse('''This is a [foo bar] test.'''))
This is a [foo bar] test.

>>> print(p.parse('''Text with only [opening square bracket.'''))
Text with only [opening square bracket.

Special handling
================

Leading and trailing spaces are always removed from command text:

>>> print(p.parse("[url http://example.com Trailing space  ]."))
[DEBUG] url2html() got 'http://example.com Trailing space'
<a href="http://example.com">Trailing space</a>.

>>> print(p.parse("[url http://example.com   Leading space]."))
[DEBUG] url2html() got 'http://example.com   Leading space'
<a href="http://example.com">Leading space</a>.

Non-breaking and zero-width spaces are treated like normal spaces:

>>> print(p.parse(u"[url\u00A0http://example.com example.com]."))
[DEBUG] url2html() got 'http://example.com example.com'
<a href="http://example.com">example.com</a>.

>>> print(p.parse(u"[url \u200bhttp://example.com example.com]."))
[DEBUG] url2html() got 'http://example.com example.com'
<a href="http://example.com">example.com</a>.

>>> print(p.parse(u"[url&nbsp;http://example.com example.com]."))
[DEBUG] url2html() got 'http://example.com example.com'
<a href="http://example.com">example.com</a>.

Limits
======

A single closing square bracket as part of ARGS will not produce the
desired result:

>>> print(p.parse(r'''This is a [url
... http://xyz.com The character "\]"].'''))
[DEBUG] url2html() got 'http://xyz.com The character "\\'
This is a <a href="http://xyz.com">The character "\</a>"].

Execution flow statements like `[if ...]` and `[endif ...]` or ``[for
...]`` and ``[endfor ...]`` would be nice.



The ``[=expression]`` form
==========================


>>> print(p.parse('''<ul>[="".join(['<li>%s</li>' % (i+1) for i in range(5)])]</ul>'''))
<ul><li>1</li><li>2</li><li>3</li><li>4</li><li>5</li></ul>

You can specify a run-time context:

>>> ctx = { 'a': 3 }
>>> print(p.parse('''\
... The answer is [=a*a*5-a].''', context=ctx))
The answer is 42.


.. _dg.memo.Previewable:

The ``Previewable`` mixin
==============================

The :class:`Previewable` model mixin adds three database fields  :attr:`body
<Previewable.body>`, :attr:`body_short_preview <Previewable.body_short_preview>`
and :attr:`body <Previewable.body_full_preview>`. The two preview fields contain
the parsed version of the body, they are read-only and get updated automatically
when the body is updated.  :attr:`body_short_preview
<Previewable.body_short_preview>` contains only the first paragraph and a "more"
indication if the full preview has more. See also :func:`truncate_comment`.

This mixin is used for example by
:class:`lino.modlib.comments.Comment`,
:class:`lino.modlib.publisher.Page` and
:class:`lino_xl.lib.blog.Entry`.

>>> from lino.modlib.memo.mixins import Previewable
>>> print("\n".join([full_model_name(m) for m in rt.models_by_base(Previewable)]))
comments.Comment


>>> def test(body):
...     short, full = comments.Comment().parse_previews(body)
...     print(short)
...     print("------")
...     print(full)

>>> test("Foo bar baz")
Foo bar baz
------
Foo bar baz

>>> test("<p>Foo</p><p>bar baz</p>")
Foo bar baz
------
<p>Foo</p><p>bar baz</p>


>>> test("Foo\n\nbar baz")
Foo
<BLANKLINE>
bar baz
------
Foo
<BLANKLINE>
bar baz


.. _memo.builtin:

Built-in memo commands
======================

.. _memo.url:

url
===

20250605: This command doesn't exist any more, see :ref:`dg.topics.urls`.

Insert a link to an external web page. The first argument is the URL
(mandatory). If no other argument is given, the URL is used as
text. Otherwise the remaining text is used as the link text.

The link will always open in a new window (``target="_blank"``)

Usage examples:

- ``[url http://www.example.com]``
- ``[url http://www.example.com example]``
- ``[url http://www.example.com another example]``

..  test:
    >>> p = dd.plugins.memo.parser
    >>> print(p.parse("See [url http://www.example.com]."))  #doctest: +SKIP
    See <a href="http://www.example.com" target="_blank">http://www.example.com</a>.
    >>> print(p.parse("See [url http://www.example.com example]."))  #doctest: +SKIP
    See <a href="http://www.example.com" target="_blank">example</a>.

    >>> print(p.parse("""See [url https://www.example.com
    ... another example]."""))  #doctest: +SKIP
    See <a href="https://www.example.com" target="_blank">another example</a>.

    A possible situation is that you forgot the space:

    >>> print(p.parse("See [urlhttp://www.example.com]."))  #doctest: +SKIP
    See [urlhttp://www.example.com].


.. _memo.py:

py
==

Refer to a Python object. This is not being used on the field. A fundamental
problem is that it works only in the currently running Python environment.

Usage examples:

- ``[py lino]``
- ``[py lino.modlib.memo.parser]``
- ``[py lino_xl.lib.tickets.models.Ticket]``
- ``[py lino_xl.lib.tickets.models.Ticket tickets.Ticket]``

The global memo parser contains two "built-in commands":

>>> p = dd.plugins.memo.parser

The ``py`` command  is disabled since 20240920 because I don't know anybody who
used it (except myself a few times for testing it) and because it requires
`SETUP_INFO`, which has an uncertain future.

>>> print(p.parse("[py lino]."))  #doctest: +SKIP
<a href="https://gitlab.com/lino-framework/lino/blob/master/lino/__init__.py" target="_blank">lino</a>.

>>> print(p.parse("[py lino_xl.lib.tickets.models.Ticket]."))  #doctest: +SKIP
<a href="https://gitlab.com/lino-framework/xl/blob/master/lino_xl/lib/tickets/models.py" target="_blank">lino_xl.lib.tickets.models.Ticket</a>.

>>> print(p.parse("[py lino_xl.lib.tickets.models.Ticket.foo]."))  #doctest: +SKIP
<a href="Error in Python code (type object 'Ticket' has no attribute 'foo')" target="_blank">lino_xl.lib.tickets.models.Ticket.foo</a>.

>>> print(p.parse("[py lino_xl.lib.tickets.models.Ticket Ticket]."))  #doctest: +SKIP
<a href="https://gitlab.com/lino-framework/xl/blob/master/lino_xl/lib/tickets/models.py" target="_blank">Ticket</a>.

Non-breaking spaces are removed from command text:

>>> print(p.parse("[py lino]."))  #doctest: +SKIP
<a href="https://gitlab.com/lino-framework/lino/blob/master/lino/__init__.py" target="_blank">lino</a>.


Configuration
=============

.. setting:: memo.short_preview_length

  How many characters to accept into the short preview.

  Default is 300, cms sets it to 1200.

.. setting:: memo.short_preview_image_height

  Default value is ``8em``.  This setting was removed 2025-02-09.


Mentions
========

>>> obj = comments.Comment.objects.filter(body__contains="[person 13]").first()
>>> print(obj.body)
<p>This is a comment about [person 15] and [person 13].</p>

>>> print(obj.body_short_preview)  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
This is a comment about <a href="/api/contacts/Persons/15"
style="text-decoration:none">Hans Altenberg</a> and <a
href="/api/contacts/Persons/13" style="text-decoration:none">Andreas
Arens</a>.

>>> hans = contacts.Person.objects.get(pk=13)
>>> rt.show(memo.MentionsByTarget, hans)  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
`Comment #122 <…>`__

>>> rt.show(memo.Mentions)  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
====================== ===========================================
 Referrer               Target
---------------------- -------------------------------------------
 `Comment #1 <…>`__     `Screenshot 20250124 104858.png <…>`__
 `Comment #2 <…>`__     `screenshot-toolbar.png <…>`__
 `Comment #11 <…>`__    `Rumma & Ko OÜ <…>`__
 `Comment #11 <…>`__    `Bäckerei Ausdemwald <…>`__
 `Comment #12 <…>`__    `Bäckerei Mießen <…>`__
 `Comment #12 <…>`__    `Bäckerei Schmitz <…>`__
 `Comment #21 <…>`__    `Screenshot 20250124 104858.png <…>`__
 `Comment #22 <…>`__    `Garage Mergelsberg <…>`__
 ...
 `Comment #472 <…>`__   `Managers <…>`__
 `Comment #472 <…>`__   `Sales team <…>`__
 `Comment #481 <…>`__   `screenshot-toolbar.png <…>`__
 `Comment #482 <…>`__   `Screenshot 20250124 104858.png <…>`__
 `Comment #491 <…>`__   `screenshot-toolbar.png <…>`__
 `Comment #492 <…>`__   `Screenshot 20250124 104858.png <…>`__
 `Comment #501 <…>`__   `#1 (Föö fails to bar when baz) <…>`__
 `Comment #501 <…>`__   `#2 (Bar is not always baz) <…>`__
 `Comment #502 <…>`__   `#3 (Baz sucks) <…>`__
 `Comment #502 <…>`__   `#4 (Foo and bar don't baz) <…>`__
====================== ===========================================
<BLANKLINE>



Technical reference
===================

.. function:: parse_previews(src, ar)

.. function:: truncate_comment(html_str, max_length=300)

    Return the first paragraph of a string that can be either HTML or plain
    text, containing at most one paragraph with at most `max_p_len` characters.

    :html_str: the raw string of html
    :max_length: max number of characters to leave in the paragraph.

    See usage examples in
    :doc:`/specs/comments` and
    :doc:`/apps/noi/memo` and
    :doc:`/topics/truncate`.


.. function:: rich_text_to_elems(ar, description)

    A RichTextField can contain either HTML markup or plain text.


.. function:: body_subject_to_elems(ar, title, description)

    Convert the given `title` and `description` to a list of HTML
    elements.

    Used by :mod:`lino.modlib.notify` and by :mod:`lino_xl.lib.trading`


.. class:: Previewable

  See :ref:`dg.memo.Previewable`.

  Adds three rich text fields and their behaviour.

  .. attribute:: body

    An editable text body.

    This is a :class:`lino.core.fields.PreviewTextField`.

  .. attribute:: body_short_preview

    A read-only preview of the first paragraph of :attr:`body`.

  .. attribute:: body_full_preview

    A read-only full preview of :attr:`body`.


.. class:: BabelPreviewable

  A :class:`Previewable` where the :attr:`body` field is a babel field.


.. class:: PreviewableChecker

  Check for previewables needing update.


.. class:: Mention

    Django model to represent a mention, i.e. the fact that some memo text of
    the owner points to some other database row.

    .. attribute:: owner

        The database row that mentions another one in a memo text.

    .. attribute:: source

        The mentioned database row.


.. class:: MemoReferrable

  Makes your model referable by a memo command.

  Overrides :meth:`lino.core.model.Model.on_analyze` to call
  :meth:`parser.Parser.register_django_model` when :attr:`memo_command` is
  given.

  .. attribute:: memo_command

    The name of the memo command to define.



The ``[url]`` memo command has been removed
===========================================

When we introduced the clickable URLs feature, we decided to remove the old
``[url]`` memo command because it wasn't used very much and  because keeping it
would make things complicated.

To remove [url] memo tags from existing data, the site maintainer can run the
:manage:`removeurls` admin command.

.. management_command:: removeurls

  Convert [url] memo commands in the text fields of this database into <a href>
  tags.


>>> from atelier.sheller import Sheller
>>> shell = Sheller(settings.SITE.project_dir)

>>> shell('python manage.py removeurls --help')
... #doctest: +REPORT_UDIFF +NORMALIZE_WHITESPACE
usage: manage.py removeurls [-h] [-b] [--version] [-v {0,1,2,3}]
                            [--settings SETTINGS] [--pythonpath PYTHONPATH]
                            [--traceback] [--no-color] [--force-color]
                            [--skip-checks]
<BLANKLINE>
Convert [url] memo commands in the text fields of this database into <a href>
tags.
<BLANKLINE>
options:
  -h, --help            show this help message and exit
  -b, --batch, --noinput
                        Do not prompt for input of any kind.
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output,
                        2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g.
                        "myproject.settings.main". If this isn't provided, the
                        DJANGO_SETTINGS_MODULE environment variable will be
                        used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g.
                        "/home/djangoprojects/myproject".
  --traceback           Display a full stack trace on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.

>>> shell('python manage.py removeurls --batch')
... #doctest: +REPORT_UDIFF +NORMALIZE_WHITESPACE
Search for [url] memo commands in accounting.PaymentTerm...
Search for [url] memo commands in cal.Calendar...
Search for [url] memo commands in cal.Event...
Search for [url] memo commands in cal.EventType...
Search for [url] memo commands in cal.RecurrentEvent...
Search for [url] memo commands in cal.Room...
Search for [url] memo commands in cal.Task...
Search for [url] memo commands in comments.Comment...
Search for [url] memo commands in groups.Group...
Search for [url] memo commands in products.Category...
Search for [url] memo commands in products.Product...
Search for [url] memo commands in tickets.Ticket...
Search for [url] memo commands in tinymce.TextFieldTemplate...
Search for [url] memo commands in topics.Interest...
Search for [url] memo commands in trading.InvoiceItem...
Search for [url] memo commands in working.Session...

Here is what you get it you forget to convert existing data:

>>> from lino.utils.soup import url2a
>>> print(url2a('Here is [url https://www.example.com an example].'))
Here is [url <a href="https://www.example.com" target="_blank">www.example.com</a> an example].
