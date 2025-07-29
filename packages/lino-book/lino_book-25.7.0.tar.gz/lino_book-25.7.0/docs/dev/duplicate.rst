.. doctest docs/dev/duplicate.rst

============================
Duplicating database objects
============================

.. class:: Model
  :noindex:


  .. method:: on_duplicate(self, ar, master)

    Called after duplicating a row on the new row instance.

    `ar` is the action request that asked to duplicate.

    If `master` is not None, then this is a cascaded duplicate
    initiated by a :meth:`duplicate` on the specified `master`.

    Also called recursively on all related objects.  Where "related
    objects" means those which point to the master using a FK which is
    listed in :attr:`allow_cascaded_delete`.

    Called by the :class:`lino.mixins.duplicable.Duplicate` action.

    Note that this is called *before* saving the object for the
    first time.

    Obsolete: On the master (i.e. when `master` is `None`), this
    is called *after* having saved the new object for a first
    time, and for related objects (`master` is not `None`) it is
    called *before* saving the object.  But even when an
    overridden :meth:`on_duplicate` method modifies a master, you
    don't need to :meth:`save` because Lino checks for
    modifications and saves the master a second time when needed.



  .. method:: after_duplicate(self, ar, master)

    Called by :class:`lino.mixins.duplicable.Duplicate` on
    the new copied row instance, after the row and it's related fields
    have been saved.

    `ar` is the action request that asked to duplicate.

    `ar.selected_rows[0]` contains the original row that is being
    copied, which is the `master` parameter.


  .. method:: delete_veto_message(self, m, n)

    Return the message :message:`Cannot delete X because N Ys refer to it.`

  .. attribute:: allow_cascaded_copy

    A set of names of `ForeignKey` or `GenericForeignKey` fields of
    this model that cause objects to be automatically duplicated when
    their master gets duplicated.

    If this is a simple string, Lino expects it to be a space-separated list of
    field names and convert it into a `set` during startup.


During startup, Lino installs a `disable_delete` handler on each model.
Preventing accidental deletes

>>> from lino_book.projects.min1.startup import *

The output of :meth:`lino.utils.diag.analyzer.show_foreign_keys` gives an
overview of the rules that apply for your application.

>>> print(analyzer.show_foreign_keys())
... #doctest: +REPORT_UDIFF +NORMALIZE_WHITESPACE
- contacts.Company :
  - PROTECT : contacts.Role.company
- contacts.CompanyType :
  - PROTECT : contacts.Company.type
- contacts.Partner :
  - CASCADE : contacts.Company.partner_ptr, contacts.Person.partner_ptr
  - PROTECT : users.User.partner
- contacts.Person :
  - PROTECT : contacts.Role.person
- contacts.RoleType :
  - PROTECT : contacts.Role.type
- countries.Country :
  - PROTECT : contacts.Partner.country, countries.Place.country
- countries.Place :
  - PROTECT : contacts.Partner.city, contacts.Partner.region, countries.Place.parent
- users.User :
  - PROTECT : users.Authority.authorized, users.Authority.user
<BLANKLINE>
