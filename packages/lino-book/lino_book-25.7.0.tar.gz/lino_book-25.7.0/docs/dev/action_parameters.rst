.. doctest docs/dev/action_parameters.rst

=================================
Introduction to action parameters
=================================

Any action in Lino can have an optional :term:`dialog window` that pops up
before the action is actually executed. The fields of this dialog window are
called :term:`action parameters <action parameter>`.

Action parameters are defined in the :attr:`parameters
<lino.core.actions.Action.parameters>` attribute of their :class:`Action
<lino.core.actions.Action>` class.

An :class:`lino.core.actions.Action` is a :term:`dialog action` if it has
:attr:`parameters <lino.core.actions.Action.parameters>` defined (and
:attr:`no_params_window <lino.core.actions.Action.no_params_window>` has not
been enabled).

.. contents::
    :depth: 2
    :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *

.. glossary::

  action parameter

    The parameters of an action that can be given by the :term:`end user` in a
    :term:`dialog window` that is shown before executing the action.

  dialog action

    An action that opens a dialog window where the :term:`end user`  can specify
    :term:`action parameters <action parameter>`  before actually running the
    action.

The merge action (:class:`lino.core.merge.MergeAction`) is an example of an
action with parameters.  When you click the merge button on a ticket, Lino
reacts by popping up a dialog window asking for parameters.  The action request
is submitted only when you confirm this window.

.. image:: /apps/noi/tickets.Ticket.merge.png
   :width: 80%


>>> ba = rt.models.tickets.AllTickets.get_action_by_name('merge_row')
>>> action = ba.action
>>> p = action.parameters
>>> p['merge_to']
<django.db.models.fields.related.ForeignKey: merge_to>

>>> p['reason']
<django.db.models.fields.CharField: reason>


How to get the layout elements of an action parameter window.

You need the layout handle:

>>> lh = action.params_layout.get_layout_handle()
>>> lh #doctest: +ELLIPSIS
<lino.core.layouts.LayoutHandle object at ...>

>>> lh.main
<ActionParamsPanel main in lino.core.layouts.ActionParamsLayout on <lino.core.merge.MergeAction merge_row ('Merge')>>

>>> lh['main'] is lh.main
True

>>> lh['merge_to']
<ForeignKeyElement merge_to in lino.core.layouts.ActionParamsLayout on <lino.core.merge.MergeAction merge_row ('Merge')>>

>>> lh['reason']
<CharFieldElement reason in lino.core.layouts.ActionParamsLayout on <lino.core.merge.MergeAction merge_row ('Merge')>>

You can **walk** over the elements of a panel:

>>> ses = rt.login('robin')
>>> with ses.get_user().user_type.context():
...     for e in lh.walk():
...        print("{} {}".format(e.name, e.__class__.__name__))
merge_to ForeignKeyElement
merge_to_ct Wrapper
nicknames_Naming BooleanFieldElement
nicknames_Naming_ct Wrapper
reason CharFieldElement
reason_ct Wrapper
main ActionParamsPanel




Calling a parameter action programmatically
===========================================

In doctests we sometimes want to call an action programmatically
without doing a web request.

In that case we must specify the `action_param_values`.  It must be a
dict.  Lino checks whether the keys of the dict corresponds to the
names of the parameter fields:

>>> pv = dict(foo=1, reason="test")
>>> ar = ba.request_from(ses, action_param_values=pv)
Traceback (most recent call last):
...
Exception: Invalid key 'foo' in action_param_values of tickets.AllTickets request (possible keys are ['merge_to', 'reason', 'nicknames_Naming'])


Lino does not validate the values when calling it programmatically.
For example `merge_to` should be a Ticket instance.
But here we specify an integer value instead, and Lino does not complain:

>>> pv = dict(merge_to=1, reason="test")
>>> ar = ba.request_from(ses, action_param_values=pv)
>>> pprint(ar.action_param_values)
{'merge_to': 1, 'nicknames_Naming': False, 'reason': 'test'}

Basically the following should work as well. (But nobody ever asked us
to make it possible).

>>> o1 = rt.models.tickets.Ticket.objects.get(pk=1)
>>> o2 = rt.models.tickets.Ticket.objects.get(pk=2)
>>> pv = dict(merge_to=o2, reason="test")
>>> ar = ba.request_from(ses, action_param_values=pv)
>>> ar.set_confirm_answer(False)
>>> o1.merge_row.run_from_ui(ar)
>>> 'xcallback' in ar.response
True
>>> msg = ar.response['message']
>>> print(tostring(msg))
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
<div class="htmlText"><p>Are you sure you want to merge #1 (Föö fails to bar
when baz) into #2 (Bar is not always baz)?</p><ul><li>1 Nicknamings <b>will be
deleted.</b></li><li>1 Tickets, 1 Mentions, 1 Tags <b>will get reassigned.</b></li><li>#1
(Föö fails to bar when baz) will be deleted</li></ul></div>


Here is a list of all :term:`dialog actions <dialog action>` in :ref:`noi`:

>>> analyzer.show_dialog_actions()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- about.About.create_account : Create Account
  (main) [visible for all]:
  - (main_1): **First name** (first_name), **Last name** (last_name)
  - **Email** (email)
  - **Username** (username)
  - **Password** (password)
- about.About.insert_reference : Insert reference
  (main) [visible for all]: **content type** (content_type), **primary key** (primary_key)
- about.About.reset_password : Reset password
  (main) [visible for all]: **e-mail address** (email), **Username (optional)** (username), **New password** (new1), **New password again** (new2)
- about.About.sign_in : Sign in
  (main) [visible for all]:
  - (main_1):
    - (login_panel): **Username** (username), **Password** (password)
    - (social_auth_links)
- about.About.verify_user : Verify
  (main) [visible for all]: **e-mail address** (email), **Verification code** (verification_code)
- accounting.Accounts.merge_row : Merge
  (main) [visible for all]: **into...** (merge_to), **Reason** (reason)
- accounting.Journals.merge_row : Merge
  (main) [visible for all]:
  - **into...** (merge_to)
  - **Also reassign volatile related objects** (keep_volatiles): **Match rules** (accounting_MatchRule), **Follow-up rules** (invoicing_FollowUpRule)
  - **Reason** (reason)
- accounting.PaymentTerms.merge_row : Merge
  (main) [visible for all]: **into...** (merge_to), **Reason** (reason)
- cal.EventTypes.merge_row : Merge
  (main) [visible for all]: **into...** (merge_to), **Reason** (reason)
- cal.GuestRoles.merge_row : Merge
  (main) [visible for all]: **into...** (merge_to), **Reason** (reason)
- contacts.Companies.merge_row : Merge
  (main) [visible for all]:
  - **into...** (merge_to)
  - **Also reassign volatile related objects** (keep_volatiles):
    - (keep_volatiles_1): **Addresses** (addresses_Address), **Invoicing suggestions** (invoicing_Item)
    - (keep_volatiles_2): **List memberships** (lists_Member), **Contact details** (phones_ContactDetail)
    - (keep_volatiles_3): **Bank accounts** (sepa_Account), **Trading rules** (trading_TradingRule)
  - **Reason** (reason)
- contacts.Partners.merge_row : Merge
  (main) [visible for all]:
  - **into...** (merge_to)
  - **Also reassign volatile related objects** (keep_volatiles):
    - (keep_volatiles_1): **Addresses** (addresses_Address), **Invoicing suggestions** (invoicing_Item)
    - (keep_volatiles_2): **List memberships** (lists_Member), **Contact details** (phones_ContactDetail)
    - (keep_volatiles_3): **Bank accounts** (sepa_Account), **Trading rules** (trading_TradingRule)
  - **Reason** (reason)
- contacts.Persons.merge_row : Merge
  (main) [visible for all]:
  - **into...** (merge_to)
  - **Also reassign volatile related objects** (keep_volatiles):
    - (keep_volatiles_1): **contacts** (google_Contact), **Addresses** (addresses_Address)
    - (keep_volatiles_2): **Invoicing suggestions** (invoicing_Item), **List memberships** (lists_Member)
    - (keep_volatiles_3): **Contact details** (phones_ContactDetail), **Bank accounts** (sepa_Account)
    - **Trading rules** (trading_TradingRule)
  - **Reason** (reason)
- groups.Groups.merge_row : Merge
  (main) [visible for all]: **into...** (merge_to), **Group memberships** (groups_Membership), **Reason** (reason)
- lists.Lists.merge_row : Merge
  (main) [visible for all]: **into...** (merge_to), **List memberships** (lists_Member), **Reason** (reason)
- periods.StoredPeriods.merge_row : Merge
  (main) [visible for all]: **into...** (merge_to), **Reason** (reason)
- periods.StoredYears.merge_row : Merge
  (main) [visible for all]: **into...** (merge_to), **Reason** (reason)
- subscriptions.Subscriptions.merge_row : Merge
  (main) [visible for all]:
  - **into...** (merge_to)
  - **Also reassign volatile related objects** (keep_volatiles):
    - (keep_volatiles_1): **Subscription items** (subscriptions_SubscriptionItem), **Order summaries** (working_OrderSummary)
    - (keep_volatiles_2): **Movements** (accounting_Movement), **Storage movements** (storage_Movement)
  - **Reason** (reason)
- tickets.Tickets.merge_row : Merge
  (main) [visible for all]: **into...** (merge_to), **Nicknamings** (nicknames_Naming), **Reason** (reason)
- tickets.Tickets.spawn_ticket : Spawn child ticket
  (main) [visible for all]: **Summary** (ticket_summary)
- topics.Topics.merge_row : Merge
  (main) [visible for all]: **into...** (merge_to), **Reason** (reason)
- uploads.Uploads.camera_stream : Camera
  (main) [visible for all]: **Upload type** (type), **Description** (description)
- uploads.Volumes.merge_row : Merge
  (main) [visible for all]: **into...** (merge_to), **Reason** (reason)
- users.AllUsers.change_password : Change password
  (main) [visible for all]: **Current password** (current), **New password** (new1), **New password again** (new2)
- users.AllUsers.merge_row : Merge
  (main) [visible for all]:
  - **into...** (merge_to)
  - **Also reassign volatile related objects** (keep_volatiles):
    - (keep_volatiles_1): **Subscriptions** (cal_Subscription), **Reactions** (comments_Reaction)
    - (keep_volatiles_2): **calendar subscriptions** (google_CalendarSubscription), **Group memberships** (groups_Membership)
    - (keep_volatiles_3): **Nicknamings** (nicknames_Naming), **subscriptions** (notify_Subscription)
    - (keep_volatiles_4): **Interests** (topics_Interest), **User summaries** (working_UserSummary)
  - **Reason** (reason)
- users.AllUsers.verify_me : Verify
  (main) [visible for all]: **Verification code** (verification_code)
<BLANKLINE>
