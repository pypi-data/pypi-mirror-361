====================================
``lino.core.requests``
====================================

.. contents::
    :depth: 1
    :local:

This defines action requests.

See :doc:`/dev/ar`

.. class:: Request

  Represents an :term:`action request`, i.e. the context in which an action is
  running.

  You don't instantiate this yourself, you get it as an argument in methods you
  override, or as the return value of :func:`rt.login` in a :term:`tested
  document`.

  Implemented in :mod:`lino.core.requests` and :mod:`lino.core.tablerequests`

  .. attribute:: renderer

    The renderer to use when processing this request.

  .. attribute:: known_values

    A dict of known values used for filtering and when inserting new rows.

  .. attribute:: is_on_main_actor

    Whether this request is on the main actor.

    Set this explicitly to False if the JS client should remove certain
    information when issuing AJAX requests.


  .. attribute:: permalink_uris

    Set this explicitly to True if you want Lino to generate permalink URIs
    instead of javascript URIs.  Used e.g. when sending email notifications with
    actions.  Used only by renderers that make a difference (i.e. extjs).
    See :ref:`permalink_uris` for details and test coverage.

  .. attribute:: master_instance

    The database object which acts as master. This is `None` for master
    requests.

  .. attribute:: request

    The incoming Django HttpRequest object that caused this action request.


  .. method:: override_attrs(self, **kwds)

    Context manager for temporarily overriding some attribute. Usage example::

      def file2html(self, ar, text, **ctx):
          ...
          with ar.override_attrs(permalink_uris=True):
              ctx.update(href=ar.obj2url(self))
          ...
          return format_html('<a href="{href}"><img src="{src}"/></a>',**ctx)


  .. method:: obj2html(self, obj, text=None, **kwargs)

    Return a HTML anchor that opens a :term:`detail window` on the given
    :term:`database row` `obj`.

    The default representation returns the text returned by :meth:`__str__` in a
    link that opens the :term:`detail window` on the given database row.
