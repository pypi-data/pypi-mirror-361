.. doctest docs/projects/polly.rst
.. _dg.projects.polly:

===========================================
``polly`` : A little polls manager
===========================================

.. module:: lino_book.projects.polly

A little application for managing polls, explained in :ref:`polly`.

>>> from lino import startup
>>> startup('lino_book.projects.polly.settings.demo')
>>> from lino.api.doctest import *


>>> analyzer.show_dialog_actions()
- about.About.reset_password : Reset password
  (main) [visible for all]: **e-mail address** (email), **Username (optional)** (username), **New password** (new1), **New password again** (new2)
- about.About.sign_in : Sign in
  (main) [visible for all]:
  - (login_panel): **Username** (username), **Password** (password)
- about.About.verify_user : Verify
  (main) [visible for all]: **e-mail address** (email), **Verification code** (verification_code)
- polls.Polls.merge_row : Merge
  (main) [visible for all]: **into...** (merge_to), **Questions** (polls_Question), **Reason** (reason)
- users.AllUsers.change_password : Change password
  (main) [visible for all]: **Current password** (current), **New password** (new1), **New password again** (new2)
- users.AllUsers.merge_row : Merge
  (main) [visible for all]: **into...** (merge_to), **Reason** (reason)
- users.AllUsers.verify_me : Verify
  (main) [visible for all]: **Verification code** (verification_code)
<BLANKLINE>

.. _bug20250517:

Demo dates and the timezone
===========================

Here is the problem that caused :ticket:`6108` (send_pending_emails_often runs
only once a day) and :ticket:`6101` (creation time of comment in jane is in the
future): On a :term:`production site` (when no demo date is set),
:meth:`dd.today <lino.core.site.Site.today>` ignored the :setting:`TIME_ZONE`
setting and returned the current date in timezone UTC. On Jane where
:setting:`TIME_ZONE` is GMT+3, this caused any comments written after 9pm to be
dated on the next day, 24 hours in the future. Similarly for the
`send_pending_emails_often` system task, which is supposed to run every 10
seconds, when it finished after 9pm, Lino didn't add 10 seconds but 24 hours +
10 seconds. Basically :meth:`dd.today <lino.core.site.Site.today>` was using
:func:`datetime.date.today` instead of :meth:`timezone.now().date`.

The following snippet doesn't actually get tested because the output depends on
the current system time, which we cannot set. Feel free to play around,
uncomment the print statements and change the `+SKIP` into `-SKIP`.

>>> settings.USE_TZ
True
>>> settings.TIME_ZONE
'Europe/Tallinn'

>>> import datetime
>>> from django.utils import timezone
>>> import time
>>> def test(tz):
...     os.environ['TZ'] = tz
...     time.tzset()
...     # print(dd.now().date())
...     if datetime.date.today() != timezone.now().date():
...         print(f"Dates differ in timezone {tz}")
...         # print(datetime.date.today(), timezone.now().date(), dd.now().date())

>>> test("UTC")
>>> test("GMT+11")  #doctest: +SKIP
Dates differ in timezone GMT+11
>>> test("GMT-11")  #doctest: +SKIP
>>> test(settings.TIME_ZONE)  #doctest: +SKIP
