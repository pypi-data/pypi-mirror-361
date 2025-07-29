.. doctest docs/plugins/google.rst
.. _dg.plugins.google:

====================================
``google`` : Synchronize with Google
====================================

.. module:: lino_xl.lib.google

.. currentmodule:: lino_xl.lib.google

The :mod:`lino_xl.lib.google` plugin adds functionality and database models to
synchronize calendar and contacts data between a :term:`Lino site` and the
Google data of its users.  See also the :ref:`end-user documentation
<ug.plugins.google>`.

.. contents::
  :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *


Overview
========

The :term:`site operator` must define a web application with the People API and
the Calendar API on the Google developer console.

More precisely it synchronizes three database models:

- :class:`contacts.Person`
- :class:`cal.Entry`
- :class:`cal.Calendar`

Plugin configuration
====================

The following plugin attributes can be configured in the :xfile:`settings.py`.

.. setting:: google.contacts_model

    The :term:`database model` used to represent a :term:`person` on this site.
    If this is a :class:`str`. Lino will resolve it into a :term:`database
    model` during :term:`site startup`.

    Default value is ``'contacts.Person'``.

.. setting:: google.application_name

    The application's name defined in the Google API Console

.. setting:: google.num_retries

    How many times to call GoogleAPI in case of
    :class:`googleapiclient.errors.HttpError`

    :type: int
    :value: 3

.. setting:: google.client_secret_file

    JSON-formatted GoogleAPI client secret. To be obtained from Google.

    If this is a :class:`str`, Lino will convert it into a :class:`pathlib.Path`
    during :term:`site startup`.

    Default value is a file named :xfile:`google_creds.json` in the
    :attr:`site_dir <lino.core.site.Site.site_dir>`.

    See `How to get GoogleAPI credentials`_ below.


.. setting:: google.scopes

    The list of scopes to which Lino will ask access to when connecting to the
    Google API.

    :type: list

    >>> pprint(dd.plugins.google.scopes)
    ['https://www.googleapis.com/auth/userinfo.profile',
     'https://www.googleapis.com/auth/userinfo.email',
     'https://www.googleapis.com/auth/contacts',
     'https://www.googleapis.com/auth/calendar',
     'https://www.googleapis.com/auth/calendar.events']

    After modifying these scopes, delete all database entries for this auth
    provider and reauthenticate.

.. setting:: google.entry_state_translation

    Translate :class:`EntryState <lino_xl.lib.cal.EntryState>` into google status.

    :type: tuple[tuple[str, tuple[str, ...]]]
    :value: (('confirmed', ('confirmed', )), ('tentative', ('tentative', )), ('cancelled', ('cancelled', )))

    The first value of the inner tuples is the corresponding Google event status
    for the EntryState names in the second value (which is also a tuple).

.. setting:: google.guest_state_translation

    Translate between possible values in Google and Lino guest state choices.

    :type: tuple[tuple[str, tuple[str, ...]]
    :value: (('needsAction', ('needsAction', )), ('declined', ('decliend', )), ('tentative', ('tentative', )), ('accepted', ('accepted', )))

    Add more items on the second item of the inner toples so that
    they translate to the first item on the inner tuple.

Utilities
=========

The plugin also provides a utility function:

.. function:: has_scope(scope_type, user)

    :param str scope_type: Should be either 'calendar' or 'contact'
    :return bool: Tells whether a certain type of scope is available for the user.


.. _mixins:

Model mixins
============

.. class:: AccessLockable

    A model mixin to lock access to the database object (on each database query), allowing only one transaction to such objects.

    Inherits from :class:`Modified<lino.mixins.Modified>`.

    On calling the `save` method. The object is unlocked automatically and should not be used at all afterwards.
    To use it further fetch it from the database again, and further access will be locked automatically.

    This might be dangerous in case a locked instance is lost from a python session, and could be hard to get
    this object back from the database.
    Workarounds:
    Use the :meth:`unlock_all` or :meth:`unlock_objects` to modify them at the database level.
    Or get a list of pk(s) using :meth:`get_locked_objects_pk` and use :meth:`_force_get` instead.
    The following methods are available for troubleshooting:

    .. classmethod:: unlock_all()

        Unlocks all database objects.

    .. classmethod:: unlock_objects(pk_list: list)

        Given a list of pk(s) it unlocks them at the database level.

    .. classmethod:: get_locked_objects_pk()

        Returns a list of pk(s) of the currently locked objects.

    .. classmethod:: _force_get(pk: int)

        Given a pk it returns a locked database object. Use this method only for troubleshooting.

.. class:: SyncToken

    A model mixin inherits from :class:`AccessLockable` and :class:`UserAuthored<lino.modlib.users.UserAuthored>`.

    .. attribute:: sync_token

        A CharField to store nextSyncToken retrieved from Google API call.

    .. attribute:: page_token

        A CharField to store nextPageToken retrieved from Google API call.

.. class:: GoogleSynchronized

    Google's related database models inherits from this mixin.

    .. attribute:: google_id

        Used in making reference to the object stored in Google's database.

    .. method:: synchronize_with_google(self, user: Optional[User]) -> bool

        Decides whether the entry is synchronizable with Google.

        :param user: The user who's Google account lino is synchronizing with.
        :type user: Optional[\ :class:`User <lino.modlib.users.User>`]

.. class:: GoogleCalendarSynchronized

    A subclass of :class:`GoogleSynchronized`.

    .. attribute:: modified

        Keeps the timestamp of the last modification of the
        :class:`Calendar <lino_xl.lib.cal.Calendar>` as an entry.

        :type: datetime.datetime

        Helps in synchronization with Google.

    .. method:: insert_or_update_into_google(self, resource, synchronizer) -> None

        Insert or updates the calendar entry with google.

        :param resource: Google calendar API resource. Can be obtained by calling Resource.calendars()
        :param synchronizer: An instance of :class:`Synchronizer`

    .. classmethod:: get_outward_insert_update_queryset(cls, user)

        This method returns a queryset of :class:`Calendar <lino_xl.lib.cal.Calendar>`
        that are not stored in Google or should be updated.

        :param user: An instance of :class:`User <lino.modlib.users.User>`
        :return: django.db.models.query.QuerySet

    .. classmethod:: delete_google_calendar(cls, cal: dict, synchronizer) -> None

        This method deletes a :class:`Calendar <lino_xl.lib.cal.Calendar>` at
        sync time when the calendar is deleted from the Google calendar.

        :param dict cal: Dictionary of attributes of the deleted calendar.
        :param synchronizer: An instance of :class:`Synchronizer`

        Also deletes the :class:`DeletedEntry` record from the database to keep it clean.

    .. classmethod:: sync_deleted_records(cls, resource, synchronizer) -> None

        Deletes calendars by looking at :class:`DeletedEntry` from Google calendar.

        :param resource: Google calendar API resource. Can be obtained by calling Resource.calendars()
        :param synchronizer: An instance of :class:`Synchronizer`

    .. classmethod:: insert_or_update_google_calendar(cls, cal: dict, synchronizer)

        Inserts or updates a calendar entry and the default :class:`Room
        <lino_xl.lib.cal.Room>`.

        :param cls: A subclass of :class:`GoogleCalendarSynchronized`.
        :param dict cal: A dictionary of calendar attibutes.
        :param synchronizer: An instance of :class:`Synchronizer`
        :return: A tuple of the saved calendar entry and the default room.
        :rtype: tuple[\ :class:`Calendar <lino_xl.lib.cal.Calendar>`, :class:`Room <lino_xl.lib.cal.Room>`]

.. class:: GoogleCalendarEventSynchronized

    A subclass of :class:`GoogleSynchronized`.

    .. classmethod:: delete_google_event(cls, cal: dict, synchronizer) -> None

        This method deletes a :class:`Event <lino_xl.lib.cal.Event>` at sync time
        when the event is deleted from the Google calendar.

        :param dict event: Dictionary of attributes of the deleted event.
        :param synchronizer: An instance of :class:`Synchronizer`

        Also deletes the :class:`DeletedEntry` record from the database to keep it clean.

    .. classmethod:: sync_deleted_records(cls, resource, synchronizer) -> None

        Deletes events by looking at :class:`DeletedEntry` from Google calendar.

        :param resource: Google calendar API resource. Can be obtained by calling Resource.events()
        :param synchronizer: An instance of :class:`Synchronizer`

    .. classmethod:: get_outward_insert_update_queryset(cls, user)

        This method yields :class:`Event <lino_xl.lib.cal.Event>` (s)
        which are not stored in Google or should be updated.

        :param user: An instance of :class:`User <lino.modlib.users.User>`
        :return: Generator[\ :class:`Event<lino_xl.lib.cal.Event>`, None, None]

    .. method:: insert_or_update_into_google(self, resource, synchronizer) -> None

        Insert or updates the events into Google.

        :param resource: Google calendar API resource. Can be obtained by calling Resource.events()
        :param synchronizer: An instance of :class:`Synchronizer`

    .. classmethod:: insert_or_update_google_event(cls, event: dict, room, synchronizer)

        Inserts or updates a :term:`calendar entry` and related
        :class:`Room <lino_xl.lib.cal.Room>` and :class:`Guest <lino_xl.lib.cal.Guest>` 's.

        :param cls: A subclass of :class:`GoogleCalendarEventSynchronized`.
        :param dict event: A dictionary of an :class:`Event <lino_xl.lib.cal.Event>` attributes.
        :param room: The room this event belongs to.
        :type room: :class:`Room <lino_xl.lib.cal.Room>`.
        :param synchronizer: An instance of :class:`Synchronizer`
        :return: Saved calendar event entry.
        :rtype: :class:`Event <lino_xl.lib.cal.Event>`.


.. class:: GoogleContactSynchronized

    A subclass of :class:`GoogleSynchronized`.

    .. classmethod:: delete_google_contact(cls, contact: dict, synchronizer) -> None

        This method deletes a :class:`Contact` at sync time
        when the contact is deleted from Google.

        :param dict contact: Dictionary of attributes of the deleted contact.
        :param synchronizer: An instance of :class:`Synchronizer`

        Also deletes the :class:`DeletedContact` record from the database to keep it clean.

    .. classmethod:: sync_deleted_records(cls, resource, synchronizer) -> None

        Deletes contacts by looking at :class:`DeletedContact` from Google.

        :param resource: Google people API resource. Can be obtained by calling Resource.people()
        :param synchronizer: An instance of :class:`Synchronizer`

    .. classmethod:: get_outward_insert_update_queryset(cls, user: users.User = None)

        Returns contacts insertable or updatable into Google.

        :param user: An instance of :class:`User <lino.modlib.users.User>`
        :return: django.db.models.QuerySet

    .. method:: insert_or_update_into_google(self, resource, synchronizer)

        Insert or updates the contact into Google.

        :param resource: Google people API resource. Can be obtained by calling Resource.people()
        :param synchronizer: An instance of :class:`Synchronizer`

    .. classmethod:: insert_or_update_google_contact(cls, contact: dict, synchronizer)

        Inserts or updates a contact :class:`Contact`.

        :param dict contact: A dictionary of attributes of a :class:`Contact`
        :param synchronizer: An instance of :class:`Synchronizer`
        :return: Saved contact entry
        :rtype: :class:`Contact`


Choices and choicelists
=======================

Defines ChoiceList(s) and some utility functions.


.. function:: google_status(state: Union[EntryState, GuestState]) -> Optional[str]

    :param state: Takes either a :class:`EntryState <lino_xl.lib.cal.EntryState>` or a :class:`GuestState<lino_xl.lib.cal.GuestState>`.

    :return: An str as status acceptable by Google.

    Internally it works by looking at state_translation either
    :setting:`google.entry_state_translation` when the input parameter is an
    instance of an :class:`EntryState <lino_xl.lib.cal.EntryState>` or
    :setting:`google.guest_state_translation` when the input parameter is an
    instance of a :class:`GuestState <lino_xl.lib.cal.GuestState>`. It returns
    `None` if a value is not found for a corresponding state.

    >>> google.google_status(cal.EntryStates.tentative)
    'tentative'


.. class:: AccessRoles

    Keeps the choices for the type of access to a Google calendar.

    Used for checking whether a user can insert into a Google calendar. The
    available values are ``freeBusyReader`` (read public info only), ``reader``,
    ``writer`` and ``owner``.

    >>> rt.show(google.AccessRoles)
    ======= ================ ==================
     value   name             text
    ------- ---------------- ------------------
     p       freeBusyReader   Free busy reader
     r       reader           Reader
     w       writer           Writer
     o       owner            Owner
    ======= ================ ==================
    <BLANKLINE>


.. _models:

Database objects
================

.. class:: CalendarSubscription

    A subclass of :class:`BaseSubscription <lino_xl.lib.cal.BaseSubscription>`.

    .. attribute:: primary

        A boolean field which indicated whether calendar referenced in this
        subscription is the primary calendar for the user in Google.

    .. attribute:: access_role

        User's access role on the subscribed calendar.

        See: :class:`AccessRoles`

.. class:: EventSyncToken

    A subclass of :class:`SyncToken`, stores necessary tokens to sync the events updated in a user's google calendar.

    .. attribute:: subscription

        A ForeignKey pointing to a :class:`CalendarSubscription` object.

.. class:: CalendarSyncToken

    A subclass of :class:`SyncToken`, store the necessary tokens to sync the calendars updated on a user's google account.

.. class:: DeletedEntry

    Keeps a record of the natively deleted :class:`Calendar
    <lino_xl.lib.cal.Calendar>` or :class:`Event <lino_xl.lib.cal.Event>` for
    deleting from Google when the next sync is run.

    .. attribute:: calendar

        A boolean field which says whether the deleted item is a Calendar if not it is
        an Event.

        :type: bool
        :value: False

    .. attribute:: event_id

        Takes the value of the :attr:`Event.google_id
        <GoogleSynchronized.google_id>` when the deleted record is an
        :class:`Event <lino_xl.lib.cal.Event>` otherwise an empty string.

        :type: str

    .. attribute:: calendar_id

        Takes the value of the :attr:`Calendar.google_id
        <GoogleSynchronized.google_id>`

        :type: str

        If the deleted record is an `Event` it takes the `google_id` from the Calendar
        in which the deleted `Event` belongs to.


.. class:: Contact

    Keeps a reference to a google contact.

    A subclass of :class:`UserAuthored <lino.modlib.users.UserAuthored>`,
    :class:`GoogleContactSynchronized` and :class:`Modified
    <lino.mixins.Modified>`.

    .. attribute:: contact

        A ForeignKey pointing to :setting:`google.contacts_model`.


.. class:: DeletedContact

    Keeps meta information of a deleted contact to sync with google upon next
    synchronization.

    A subclass of :class:`UserAuthored <lino.modlib.users.UserAuthored>`.

    .. attribute:: contact_id

        The google resourceName.


.. class:: ContactSyncToken

    Stores the nextSyncToken and nextPageToken from google.

    A subclass of :class:`SyncToken`.

.. class:: SyncSummary

    Database model to store the summaries of a :meth:`Synchronizer.sync` session.

    Subclass of :class:`UserAuthored<lino.modlib.users.UserAuthored>` and :class:`Created<lino.mixins.Created>`

    .. attribute:: halted

        A BooleanField indicate whether the sync session has failed.

    .. attribute:: stats

        A TextField containing the textual representation of synchronization session statistics.

.. class:: FailedForeignItem

    Database model to store the foreign objects failed to put into the local database.

    .. attribute:: job

        A ForeignKey pointing to the corresponding :class:`SyncSummary`.

    .. attribute:: value

        A JSONField containing the actual remote object.

    .. attribute:: item_class

        A ForeignKey pointing to the related database model (contenttypes.ContentType)
        specifying the item synchronization class.


Interaction with other plugins
==============================

This plugin adds the following method :meth:`get_country <lino.modlib.users.User.get_country>` to
:class:`lino.modlib.users.User` model:

.. currentmodule:: lino.modlib.users

.. class:: User
  :noindex:

  .. method:: get_contact()

    Returns the user's country.

.. currentmodule:: lino_xl.lib.google

Synchronization
===============

Calendar and contacts synchronization in Lino with Google works in both ways. Lino application
can fetch entries from Google as well as it can insert and update entries into Google.

By default :setting:`google.contacts_model` are not synchronisable with google
unless they pointed to by some :class:`Contact` instance.


.. class:: FailedEntries

    A subclass of typing.NamedTuple. And has the following attributes.

    .. attribute:: calendars

        Contains reference to the :class:`Calendar <lino_xl.lib.cal.Calendar>`
        instance(s) that failed to sync with Google.

        :type: list[django.db.models.QuerySet]
        :value: []

    .. attribute:: events

        Contains reference to the :class:`Event <lino_xl.lib.cal.Event>`
        instance(s) that failed to sync with Google.

        :type: list[django.db.models.Model]
        :value: []

    .. attribute:: contacts

        Contains reference to the :class:`Contact` instance(s) that failed to
        sync with Google.

        :type: list[django.db.models.QuerySet]
        :value: []

    .. attribute:: foreign_item

        Objects fetched from the remote and failed to update (/ put) on the local database.

        :type: list[tuple[dd.Model, dict]]

        The first item of the tuple is any non-abstract subclass of dd.Model and the second item is the
        fetched object from the remote.

        :value: []


.. class:: Synchronizer

    The class that wraps the synchronization functionality.

    .. attribute:: _failed_entries

        Keeps reference to the database objects that failed to sync with google
        from the last :meth:`sync` call.

        :type: :class:`FailedEntries`

    .. attribute:: failed_entries

        Keeps reference to the database objects that failed to sync with google
        in the running :meth:`sync` call.

        :type: :class:`FailedEntries`

    .. attribute:: user

        The :class:`User <lino.modlib.users.User>`, whose records should be
        synchronized.

    .. method:: setup(user) -> None

        Sets up the user scope and initializes necessary data objects.

    .. method:: sync() -> self

        Synchronizes latest changes with Google.


How to get GoogleAPI credentials
================================

Log in to your `Google Developer Console
<https://console.developers.google.com>`__.

Create a project in the console if you don't have one already.

In the Google console, navigate to :menuselection:`APIs & Services --> Enabled
APIs & Services` and then

- click on :guilabel:`+ ENABLE APIS AND SERVICES`
- search for :guilabel:`Google People API` and enable this API
- search for :guilabel:`Google Calendar API` and enable this API

For detailed information follow this `Google API Console Help page
<https://support.google.com/googleapi/answer/6158841?hl=en>`__.

Navigate to :menuselection:`APIs & Services --> Credentials` then

- click on :menuselection:`+ CREATE CREDENTIALS`
- choose `OAuth client ID`.
- Set the `Application type` to `Web application`.
- In the `Authorized redirect URIs` section click on `+ ADD URI` and
  put your matching URI to the following regex and hit `CREATE`::

    >>> your_server_host_name = r".*"
    >>> uri_pattern = r"^http(s)?://" + your_server_host_name + r"/oauth/complete/google/$"

Click on the :guilabel:`DOWNLOAD JSON` button to download the credentials. Save
them as a file named :xfile:`google_creds.json` in the :attr:`site_dir
<lino.core.site.Site.site_dir>`.

You can also store them in a different place and specify the file's full path
name in :setting:`google.client_secret_file` in your :xfile:`settings.py`::

  class Site(...):
      ...
      def get_plugin_configs(self):
          ...
          yield 'google', 'client_secret_file', '/path/to/my/credentials.json'
      ...

Navigate to :menuselection:`APIs & Services --> OAuth consent screen` and put
the email addresses of some test users.

And that's almost it for getting Google API credentials.

Otherwise see `this thread <https://support.google.com/cloud/answer/6158849?hl=en>`__.
