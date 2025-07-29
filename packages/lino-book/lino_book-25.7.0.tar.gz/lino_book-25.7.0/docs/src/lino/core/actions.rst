=====================
``lino.core.actions``
=====================

.. module:: lino.core.actions

This module defines the :class:`Action` class and some of the standard actions.

See :ref:`dev.actions`.



.. class:: Action

  Abstract base class for all actions.

  The first argument is the optional `label`, other arguments should
  be specified as keywords and can be any of the existing class
  attributes.

  .. attribute:: button_color

    The color to be used on icon-less buttons for this action
    (i.e. which have no :attr:`icon_name`).  See also
    :attr:`lino.core.site.Site.use_silk_icons`.

    Not yet implemented. This is currently being ignored.

  .. attribute:: disable_primary_key

    Whether primary key fields should be disabled when using this
    action. This is `True` for all actions except :class:`ShowInsert`.

  .. attribute:: keep_user_values

    Whether the parameter window should keep its values between
    different calls. If this is True, Lino does not fill any default
    values and leaves those from a previous call.

    Deprecated because it (1) is not used on any production site, (2) has a
    least two side effect: the fields *never* get a default value, even not on
    first execution, and you cannot explicitly specify programmatic field
    values. And (3) we actually wouldn't want to specify this per action but per
    field.


  .. attribute:: icon_name

    The class name of an icon to be used for this action when
    rendered as toolbar button.  Allowed icon names are defined in
    :data:`lino.core.constants.ICON_NAMES`.

  .. attribute:: combo_group

    The name of another action to which to "attach" this action.
    Both actions will then be rendered as a single combobutton.

  .. attribute:: parameters

    See :attr:`lino.core.utils.Parametrizable.parameters`.

  .. attribute:: use_param_panel


    Used internally. This is True for window actions whose window use
    the parameter panel: grid and emptytable (but not showdetail)


  .. attribute:: no_params_window


    Set this to `True` if your action has :attr:`parameters` but you
    do *not* want it to open a window where the user can edit these
    parameters before calling the action.

    Setting this attribute to `True` means that the calling code must
    explicitly set all parameter values.  Usage example are the
    :attr:`lino_xl.lib.polls.models.AnswersByResponse.answer_buttons`
    and :attr:`lino_xl.lib-tickets.Ticket.quick_assign_to`
    virtual fields.



  .. attribute:: sort_index


    Determines the sort order in which the actions will be presented
    to the user.

    List actions are negative and come first.

    Predefined `sort_index` values are:

    ===== =================================
    value action
    ===== =================================
    -1    :class:`as_pdf <lino_xl.lib.appypod.PrintTableAction>`
    10    :class:`ShowInsert`
    11    :attr:`duplicate <lino.mixins.duplicable.Duplicable.duplicate>`
    20    :class:`detail <ShowDetail>`
    30    :class:`delete <DeleteSelected>`
    31    :class:`merge <lino.core.merge.MergeAction>`
    50    :class:`Print <lino.mixins.printable.BasePrintAction>`
    51    :class:`Clear Cache <lino.mixins.printable.ClearCacheAction>`
    52    :attr:`lino.modlib.users.UserPlan.start_plan`
    53    :attr:`lino.modlib.users.UserPlan.update_plan`
    60    :class:`ShowSlaveTable`
    90    default for all custom row actions
    100   :class:`SubmitDetail`
    200   default for all workflow actions (:class:`ChangeStateAction <lino.core.workflows.ChangeStateAction>`)
    ===== =================================




  .. attribute:: auto_save


    What to do when this action is being called while the user is on a
    dirty record.

    - `False` means: forget any changes in current record and run the
      action.

    - `True` means: save any changes in current record before running
      the action.  `None` means: ask the user.



  .. attribute:: extjs_main_panel


    Used by :mod:`lino_xl.lib.extensible` and
    :mod:`lino.modlib.awesome_uploader`.

    Example::

        class CalendarAction(dd.Action):
            extjs_main_panel = "Lino.CalendarApp().get_main_panel()"
            ...




  .. attribute:: js_handler


    This is usually `None`.  Otherwise it is the name of a Javascript
    callable to be called without arguments. That callable must have
    been defined in a :attr:`lino.core.plugin.Plugin.site_js_snippets`
    of the plugin.

    Also can be defined as a class method, that takes the actor as the only
    argument and should return a JavaScript executable.
    An example use case is defined in
    :class:`lino.modlib.help.OpenHelpWindow` where the return string
    follows the format::

        return "let _ = window.open('URL')"

    Callable Example::

        def js_handler(self, actor):
            ...
            return JS_EXECUTABLE



  .. attribute:: action_name

    Internally used to store the name of this action within the
    defining Actor's namespace.

  .. attribute:: defining_actor


    The :class:`lino.core.actors.Actor` who uses this action for the
    first time.  This is set during :meth:`attach_to_actor`.  This is
    used internally e.g. by :mod:`lino.modlib.extjs` when generating
    JavaScript code for certain actions.


  .. attribute:: hotkey


    An instance of :class:`lino.core.keyboard.Hotkey`. Used as a keyboard
    shortcut to trigger actions.


  .. attribute:: default_format


    Used internally.


  .. attribute:: editable



    Whether the parameter fields should be editable.
    Setting this to False seems nonsense.


  .. attribute:: hide_top_toolbar


    This is set to `True` for :class:`ShowInsert`.

    As an applicationdeveloper you don't need this action attribute, but
    see :attr:`lino.core.actors.Actor.hide_top_toolbar`.



  .. attribute:: hide_navigator


    Hide navigator actions on window opened by this action.


  .. attribute:: never_collapse


    When `True` the action will always be visible, regardless of whether
    the toolbar collapsed or not.



  .. attribute:: show_in_plain


    Whether this action should be displayed as a button in the toolbar
    of a plain html view.


  .. attribute:: show_in_toolbar



    Whether this action should be displayed in the toolbar.

    In ExtJS this will also cause it to be in the context menu of a grid.

    For example the :class:`CheckinVisitor
    <lino_xl.lib.reception.CheckinVisitor>`,
    :class:`ReceiveVisitor
    <lino_xl.lib.reception.ReceiveVisitor>` and
    :class:`CheckoutVisitor
    <lino_xl.lib.reception.CheckoutVisitor>` actions have this
    attribute explicitly set to `False` because otherwise they would be
    visible in the toolbar.



  .. attribute:: show_in_workflow


    Whether this action should be displayed in the
    :attr:`workflow_buttons <lino.core.model.Model.workflow_buttons>`
    column.  If this is True, then Lino will automatically set
    :attr:`custom_handler` to True.


  .. attribute:: custom_handler


    Whether this action is implemented as Javascript function call.
    This is necessary if you want your action to be callable using an
    "action link" (html button).


  .. attribute:: select_rows

    True if this action needs an object to act on.

    Set this to `False` if this action is a list action, not a row
    action.


  .. attribute:: http_method


    HTTP method to use when this action is called using an AJAX call.




  .. attribute:: preprocessor

    Name of a Javascript function to be invoked on the web client when
    this action is called.


  .. attribute:: window_type

    On actions that opens_a_window this must be a unique one-letter
    string expressing the window type.

    See `constants.WINDOW_TYPES`.

    Allowed values are:

    - None : opens_a_window is False
    - 't' : ShowTable
    - 'd' : ShowDetail
    - 'i' : ShowInsert

    This can be used e.g. by a summary view to decide how to present the
    summary data (usage example
    :meth:`lino.modlib.uploads.AreaUploads.get_table_summary`).



  .. attribute:: callable_from

    A string that specifies from which :attr:`window_type` this action
    is callable.  None means that it is only callable from code.

    Default value is 'td' which means from both table and detail
    (including ShowEmptyTable which is subclass of ShowDetail). But
    not callable from ShowInsert.


    .. method:: __get__(self, instance, owner)


        When a model has an action "foo", then getting an attribute
        "foo" of a model instance will return an :class:`InstanceAction`.


    .. classmethod:: decorate(cls, *args, **kw)


        Return a decorator that turns an instance method on a model or a
        class method on an actor into an action of this class.

        The decorated method will be installed as the actions's
        :meth:`run_from_ui <Action.run_from_ui>` method.

        All arguments are forwarded to :meth:`Action.__init__`.



    .. method:: is_callable_from(self, caller)

        Return `True` if this action makes sense as a button from within
        the specified `caller` (an action instance which must have a
        :attr:`window_type`).  Do not override this method on your
        subclass ; rather specify :attr:`callable_from`.


    .. method:: is_window_action(self)

        Return `True` if this is a "window action" (i.e. which opens a GUI
        window on the client before executing).



    .. method:: get_label(self)


        Return the `label` of this action, or the `action_name` if the
        action has no explicit label.


    .. method:: attach_to_actor(self, owner, name)


        Called once per actor and per action on startup before a
        :class:`BoundAction` instance is created.  If this returns
        False, then the action won't be attached to the given actor.

        The owner is the actor which "defines" the action, i.e. uses
        that instance for the first time.  Subclasses of the owner may
        re-use the same instance without becoming the owner.


    .. method:: get_action_permission(self, ar, obj, state)

        Return (True or False) whether the given :class:`ActionRequest
        <lino.core.requests.BaseRequest>` `ar` should get permission
        to run on the given Model instance `obj` (which is in the
        given `state`).

        Derived Action classes may override this to add vetos.
        E.g. the MoveUp action of a Sequenced is not available on the
        first row of given `ar`.

        This should be used only for light-weight tests. If this
        requires a database lookup, consider disabling the action in
        :meth:`disabled_fields
        <lino.core.model.Model.disabled_fields>` where you can disable
        multiple actions and fields at once.



    .. method:: get_view_permission(self, user_type)


        Backwards-compatibility for ext_renderer, which does::

            for ds in lh.layout.get_datasources():
                if ds.get_view_permission(user_type):
                    return True


    .. method:: get_action_view_permission(self, actor, user_type)


        Return True if this action is visible on the given actor for users of
        the given user_type.


    .. method:: run_from_ui(self, ar, **kwargs)


        Execute the action.  `ar` is a :class:`BaseRequest
        <lino.core.requests.BaseRequest>` object.


    .. method:: run_from_code(self, ar=None, *args, **kwargs)


        Probably to be deprecated.
        Execute the action.  The default calls :meth:`run_from_ui`.  You
        may override this to define special behaviour


    .. method:: action_param_defaults(self, ar, obj, **kw)

        Same as :meth:`lino.core.actors.Actor.param_defaults`, except that
        on an action it is a instance method.

        Note that this method is not called for actions which are rendered
        in a toolbar (:ticket:`1336`).

        Usage examples:
        :class:`lino.modlib.users.actions.SendWelcomeMail`




    .. method:: get_layout_aliases(self)



        Yield a series of (ALIAS, repl) tuples that cause a name ALIAS in a
        layout based on this action to be replaced by its replacement `repl`.



.. class:: ShowEmptyTable

    The default action for :class:`lino.utils.report.EmptyTable`.


.. class:: SaveGridCell

    Called when user edited a cell of a non-phantom record in a grid.
    Installed as `update_action` on every :class:`Actor`.



.. class:: SubmitDetail

    Save changes in the detail form.

    This is rendered as the "Save" button of a :term:`detail window`.

    Installed as `submit_detail` on every actor.



.. class:: CreateRow

    Called when user edited a cell of a phantom record in a grid.


.. class:: ShowSlaveTable

    An action that opens a window showing another table (to be
    specified when instantiating the action).


.. class:: WrappedAction

    On instantiation it takes a :class:`BoundAction
    <lino.core.boundaction.BoundAction>` as a positional argument and returns an
    action instance that behaves as a wrapper around the given
    *BoundAction.action* useful when binding to another :class:`Actor
    <lino.core.actors.Actor>`.


.. class:: MultipleRowAction

    Base class for actions that update something on every selected row.

.. class:: DeleteSelected

    Delete the selected row(s).

    This action is automatically installed on every editable actor.
