.. doctest docs/dev/instantiate_or_not.rst

=====================================
To instantiate or not to instantiate?
=====================================

While this design choice of never instantiating actors has advantages,
it also has some disadvantages:

- Every method of an actor must have a `@classmethod` decorator.
  That's a bit surprising for newbies.

- Concepts like :class:`lino.core.utils.Parametrizable` are common to
  actions and actors, but need a "class method" and an "instance
  method" version of their logic.

Here is an example:

.. literalinclude:: actors1.py

The output will be::

    This is <class '__main__.MyJournals'> with parameters = {'foo': 1, 'bar': 2}
    This is <class '__main__.Action'> with parameters = None


We might decide one day that Lino creates an automatic singleton
instance for each Actor at startup.
