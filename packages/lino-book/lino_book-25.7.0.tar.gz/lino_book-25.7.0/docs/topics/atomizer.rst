.. _book.topics.atomizer:

===================================
About data elements, atomizers & Co
===================================

.. glossary::

  actor handle

    An object in memory, one instance for each :term:`actor`, created lazily by
    calling :meth:`Actor.get_handle`.

  data store

    Responsible for mapping data exchanges between the Django ORM and the web
    front end.

    providing row2dict and row2list

    An object in memory, created at startup, assigned to each :term:`actor
    handle`.

    Has a list of :term:`store fields <store field>`. All store fields are in
    :attr:`list_fields`,  and it has several lists that contain their own
    "selection" of fields: :attr:`list_fields` (which we should rename to
    :attr:`grid_fields`), :attr:`detail_fields`, :attr:`card_fields` and
    :attr:`item_fields`.

  ah

    Common variable name for :term:`actor handle`.

  rh

    Common variable name for "report handle",  the ancient term for :term:`actor
    handle`.

  data element

    A named element of a layout. This can be a *field element* (which refers to
    a database field or virtual field of the :term:`table` or :term:`dialog
    action`) or a *panel* (a container of elements).

  store field

    The part of a data store that is responsible for one data element.

  atomizer

    Synonym of :term:`store field`.

  choicelist of actors

    A recipe where the choices of a :term:`choicelist` point to a :term:`data
    table`.
