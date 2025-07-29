# -*- coding: utf-8 -*-
# Copyright 2016-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# python manage.py test tests.test_notify

"""Runs some tests about the notification framework.

This started as a copy of the :file:`test_notify.py` in `noi1e` because I tried
to cover #5715 (ObjectDoesNotExist: Invalid primary key 114 for
storage.FillersByPartner). Reproducing #5715 didn't actually work out, but I
discovered an occurence of #5739 (Oops, get_atomizer(...) returned None).

"""

import datetime
# import time
# import unittest

# from unittest.mock import patch

from django.conf import settings
from django.utils.timezone import make_aware
from django.utils.html import escape
from asgiref.sync import async_to_sync

from lino.api import dd, rt
from lino.utils.djangotest import TestCase
from lino.core import constants
from lino.core.renderer import TestRenderer

from lino.modlib.users.choicelists import UserTypes

from lino.utils.instantiator import create

# from lino.modlib.notify.models import send_pending_emails_often
from lino.modlib.notify.choicelists import MailModes
from lino.modlib.linod.choicelists import Procedures
from lino.core.diff import ChangeWatcher

# from lino.utils import capture_stdout


# @unittest.skip("20210527")
class TestCase(TestCase):
    """Miscellaneous tests."""
    maxDiff = None

    def test_01(self):
        self.assertEqual(settings.SETTINGS_MODULE, None)
        self.assertEqual(settings.LOGGING, {})
        self.assertEqual(settings.SERVER_EMAIL, 'root@localhost')

    def test_comment(self):
        """Test what happens when a comment is posted on a ticket with
        watchers.

        """
        # use_linod = settings.SITE.use_linod
        # settings.SITE.use_linod = False
        # settings.SITE.use_multiprocessing = False
        Ticket = rt.models.tickets.Ticket
        # Project = rt.models.tickets.Project
        # Site = rt.models.tickets.Site
        MailModes = rt.models.notify.MailModes
        # Subscription = rt.models.tickets.Subscription
        Group = rt.models.groups.Group
        Membership = rt.models.groups.Membership
        # Vote = rt.models.votes.Vote
        # Star = rt.models.stars.Star
        Message = rt.models.notify.Message
        Comment = rt.models.comments.Comment
        User = settings.SITE.user_model
        # create(Project, name="Project")
        self.robin = create(User,
                            username='robin',
                            first_name="Robin",
                            user_type=UserTypes.admin)
        # robin.set_password("1234")
        # robin.full_clean()
        # robin.save()
        self.assertEqual(self.robin.mail_mode, MailModes.often)

        self.aline = create(User,
                            username='aline',
                            first_name="Aline",
                            email="aline@example.com",
                            language='fr',
                            user_type=UserTypes.admin)

        aline_group = create(Group, name="My Group")
        # foo = create(Site, name="Foo", group=aline_group)
        create(Membership, group=aline_group, user=self.aline)
        create(Membership, group=aline_group, user=self.robin)
        # create(Subscription, site=foo, user=aline)

        # We create ticket with explicit id 123456 because for reproducing #5715
        # (ObjectDoesNotExist: Invalid primary key 114 for
        # storage.FillersByPartner) we need a ticket id that does not exist in
        # Comments.
        ticket = create(Ticket,
                        summary="Après moi le déluge",
                        user=self.robin,
                        id=123456,
                        # site=foo,
                        group=aline_group)

        self.run_test_on_row(ticket,
                             """Robin a commenté <a href="/#/api/tickets/Tickets/123456" """
                             """style="text-decoration:none">#123456 ("""
                             """Après moi le déluge)</a>:<br><p>I don't agree (#foobar).</p>""")
        # """Robin a commenté [ticket 1] ("""\
        # """Après moi le déluge):<br>I don't agree (#foobar).""")
        # Message.objects.all().delete()
        # Comment.objects.all().delete()
        # self.run_test_on_row(foo,
        #     """Robin a commenté <a href="/api/tickets/Sites/1">Foo</a>:<br>I don't agree (#foobar).""")

        # removed 20250113 because i removed the reply (AddComment) field:
        # # #5613 (Stop notifying twice when Ticket.comment field was used):
        # from urllib.parse import quote
        # Message.objects.all().delete()
        # self.assertEqual(Message.objects.count(), 0)
        # obj = Comment.objects.last()
        # self.assertEqual(obj.body, "I don't agree (#foobar).")
        # url = "/api/comments/RecentComments/{}".format(obj.pk)
        # data = "an=submit_detail&body={}".format(quote(obj.body))
        # data += "&reply={}".format(quote("<p>foo</p>"))
        # # raise Exception(f"20240617 {data}")
        # self.client.force_login(self.robin)
        # response = self.client.put(url, data)
        # result = self.check_json_result(
        #     response, 'success message data_record refresh_delayed_value')
        # self.assertEqual(result['message'], 'Comment "Comment #1" : nothing to save.')
        # self.assertEqual(result['success'], True)
        # self.assertEqual(
        #     set(result['data_record'].keys()),
        #     {'data', 'disable_delete', 'id', 'navinfo', 'param_values', 'title'})
        #
        # self.assertEqual(
        #     set(result['data_record']['data'].keys()),
        #     {'userHidden', 'owner_type', 'owner', 'pick_my_emotion',
        #     'disabled_fields', 'comment_type', 'created', 'body_full_preview',
        #     'comments.RepliesByComment', 'disable_editing',
        #     'comments.ReactionsByComment', 'reply', 'private', 'reply_to',
        #     'user', 'modified', 'owner_id', 'reply_toHidden',
        #     'comment_typeHidden', 'owner_typeHidden', 'body', 'owner_idHidden',
        #     'body_short_preview', 'id'})
        #
        # self.assertEqual(
        #     result['data_record']['data']['comments.RepliesByComment'],
        #     {'delayed_value_url':
        #         'values/comments/RecentComments/1/comments.RepliesByComment'})
        #
        # self.assertEqual(result['refresh_delayed_value'], 'comments.RepliesByComment')
        # self.assertEqual(Message.objects.count(), 1)
        # msg = Message.objects.last()
        # self.assertEqual(msg.subject,
        #     "Robin a commenté #123456 (Après moi le déluge)")

        url = "/values/tickets/AllTickets/123456/comments.CommentsByRFC"

        # response = self.client.get(url)
        # self.assertEqual(response.content.decode(), """{ "data": """
        #                  """"Oops, get_atomizer(lino_xl.lib.tickets.ui.AllTickets, """
        #                  """lino.modlib.comments.ui.CommentsByRFC, 'comments.CommentsByRFC') """
        #                  """returned None" }""")

        # Above response was an occurence of #5739 (Oops, get_atomizer(...)
        # returned None). The funny thing was that the Oops came only for the
        # first request, so the workaround was to simply ask again. Now it
        # succeeds on first request:

        response = self.client.get(url)
        content = response.content.decode()
        # self.assertEqual(content[:20], '{ "data":')
        # self.assertEqual(content, '')
        self.assertEqual(
            content.startswith('{ "data": "<div class=\\"htmlText\\"><a href'),
            True)

        ##
        # 20241003 : reproduce #5768 (WorkedHours detail is broken)
        ##

        # we need a reporting rule before we can create a session:
        create(rt.models.working.ReportingRule)
        # avoid Lino putting the current time as start_date:
        settings.SITE.loading_from_dump = True
        # we need to be signed in as robin:
        self.client.force_login(self.robin)
        # create a session and make sure it contains what we expect:
        session = create(rt.models.working.Session,
                         ticket=ticket, start_date=dd.today(), start_time="9:00",
                         user=self.robin)
        self.assertEqual(str(dd.today()), "2015-05-22")
        self.assertEqual(str(session.start_date), "2015-05-22")
        # ses = rt.login('robin', renderer=TestRenderer())
        # s = ses.show('working.MySessionsByDay')
        # self.assertEqual(s, "")

        # simulate our use case user enters a manual end_time in the grid:
        url = f"/api/working/MySessionsByDay/{session.pk}"
        data = "an=grid_put&end_time=10:00&mk=0"
        # the react client also gives sr although this isn't needed:
        data += f"&sr={session.pk}"
        # raise Exception(f"20240617 {data}")
        response = self.client.put(url, data)
        result = self.check_json_result(
            response, 'success message rows master_data')
        self.assertEqual(
            result['message'], 'Working session "22/05/2015 09:00-10:00 Robin #123456" has been updated.')

        # settings.SITE.use_linod = use_linod

    def run_test_on_row(self, obj, expected_msg_body):
        Message = rt.models.notify.Message
        ContentType = rt.models.contenttypes.ContentType

        self.assertEqual(Message.objects.count(), 0)

        ar = rt.login('robin', renderer=settings.SITE.kernel.default_renderer)
        url = "/api/comments/CommentsByRFC"
        post_data = dict()
        post_data[constants.URL_PARAM_ACTION_NAME] = 'submit_insert'
        post_data.update(body="I don't agree (#foobar).")
        post_data[constants.URL_PARAM_MASTER_PK] = obj.pk
        ct = ContentType.objects.get_for_model(obj.__class__)
        post_data[constants.URL_PARAM_MASTER_TYPE] = ct.id
        # post_data[constants.URL_PARAM_REQUESTING_PANEL] = '123'
        self.client.force_login(self.robin)
        response = self.client.post(url,
                                    post_data,
                                    REMOTE_USER='robin',
                                    HTTP_ACCEPT_LANGUAGE='en')
        result = self.check_json_result(
            response, 'rows success message close_window navinfo refresh_all master_data')
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'],
                         """Comment "Comment #1" has been created.""")

        # intermezzo: also test for #4207
        rows = result['rows']
        ah = rt.models.comments.CommentsByRFC.get_handle()
        self.assertEqual([sf.name for sf in ah.store.grid_fields], [
            'body', 'created', 'user', 'id', 'modified', 'body_short_preview',
            'body_full_preview', 'owner_type', 'owner_id', 'reply_to',
            'private', 'comment_type', 'rowselect', 'owner', 'disabled_fields',
            'disable_editing'
        ])

        self.assertEqual(len(rows), 1)
        # print(rows[0])
        # ignore the timestamps to make it reproducible:

        for i in (3, 7):
            rows[0][i] = 'ignore'

        expected = [
            "<p>I don't agree (#foobar).</p>",
            "I don't agree (#foobar).",
            "<p>I don't agree (#foobar).</p>",
            'ignore',
            'Robin',
            1,
            1,
            'ignore',
            "I don't agree (#foobar).",
            "<p>I don't agree (#foobar).</p>",
            'Ticket',
            42,
            '#123456 (Après moi le déluge)',
            123456,
            None,
            None,
            False,
            None,
            None,
            None,
            '<a href="javascript:window.App.runAction({ &quot;action_full_name&quot;: &quot;tickets.Tickets.detail&quot;, '
            '&quot;actorId&quot;: &quot;tickets.Tickets&quot;, &quot;rp&quot;: null, '
            '&quot;status&quot;: { &quot;record_id&quot;: 123456 } '
            '})" style="text-decoration:none">#123456 (Apr&#232;s moi le d&#233;luge)</a>',
            {'body_full_preview': True,
             'body_short_preview': True,
             'created': True,
             'id': True,
             'modified': True,
             'user': True},
            False,
            {'meta': True}]

        # print(rows[0])

        self.assertEqual(rows[0], expected)

        # time.sleep(1)
        # raise Exception(str(Message.objects.__class__))
        # raise Exception(str(Message.objects._result_cache = None
        self.assertEqual(Message.objects.count(), 1)
        msg = Message.objects.all()[0]
        comment = rt.models.comments.Comment.objects.get(pk=1)
        # self.assertEqual(msg.message_type)
        self.assertEqual(msg.seen, None)
        self.assertEqual(msg.reply_to, comment)
        self.assertEqual(msg.user, self.aline)
        self.assertEqual(expected_msg_body, msg.body)

        # manually set created timestamp so we can test on it later.
        now = datetime.datetime(2016, 12, 22, 19, 45, 55)
        if settings.USE_TZ:
            now = make_aware(now)
        msg.created = now
        msg.save()

        settings.SERVER_EMAIL = 'root@example.com'

        # with capture_stdout() as out:
        #     async_to_sync(Procedures.send_pending_emails_often.run)(ar)
        # out = out.getvalue().strip()

        with ar.capture_logger("DEBUG") as out:
            # async_to_sync(Procedures.send_pending_emails_often.run)(ar)
            Procedures.send_pending_emails_often.run(ar)
        # out = ar.end_log_capture()

        # print(out)

        send_mail_expected = """send email
Sender: root+1@example.com
To: aline@example.com
Subject: [noi1r] Robin a commenté {}

<html><head><base href="http://127.0.0.1:8000" target="_blank"></head><body>

(22/12/2016 19:45 UTC)

{}

</body></html>
""".format(obj, expected_msg_body)
        # raise Exception(expected)
        expected = """Send out 'Mail often' summaries for 1 users.
Ignoring email because sender is root+1@example.com
""" + send_mail_expected
        self.assertEquivalent(expected, out.getvalue())

        # self.assertEqual(logger.debug.call_count, 1)
        # logger.debug.assert_called_with(
        #     'Send out %s summaries for %d users.',
        #     MailModes.often, 1)
        # logger.info.assert_called_with(
        #     'Notify %s users about %s', 1, 'Change by robin')

        Message.objects.all().delete()
        self.assertEqual(Message.objects.count(), 0)

        if isinstance(obj, rt.models.tickets.Ticket):
            cw = ChangeWatcher(obj)
            obj.priority = 20
            obj.save_watched_instance(ar, cw)

            with ar.capture_logger("DEBUG") as out:
                # async_to_sync(Procedures.send_pending_emails_often.run)(ar)
                Procedures.send_pending_emails_often.run(ar)
            # out = ar.end_log_capture()

            # with capture_stdout() as out:
            #     getattr(Procedures, "send_pending_emails_often").run(ar)
            # out = out.getvalue().strip()
            # print(out)
            # expected = ""
            # self.assertEquivalent(expected, out)

            # we do not test the output because the datetime changes and anyway we
            # actually just wanted to see if there is no UnicodeException. We
            # capture it in order to hide it from test runner output.

            # self.assertEqual(logger.debug.call_count, 2)
            # logger.debug.assert_called_with(
            #     'Send out %s summaries for %d users.',
            #     MailModes.often, 1)
