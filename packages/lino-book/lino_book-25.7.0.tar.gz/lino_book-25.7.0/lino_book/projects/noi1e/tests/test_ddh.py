# -*- coding: utf-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Runs some tests about the disable-delete handler and cascading deletes.

You can run only these tests by issuing::

  $ go noi1e
  $ python manage.py test tests.test_ddh

"""

import datetime
from django.core.exceptions import ValidationError
from lino.utils.djangotest import RemoteAuthTestCase
from lino.utils.quantities import Duration
from lino.api import rt
from lino.utils import i2d
from lino.utils.instantiator import create_row as create


class DDHTests(RemoteAuthTestCase):
    maxDiff = None

    def test01(self):
        from lino.modlib.users.choicelists import UserTypes
        Ticket = rt.models.tickets.Ticket
        User = rt.models.users.User
        #Subscription = rt.models.tickets.Subscription
        Group = rt.models.groups.Group
        Membership = rt.models.groups.Membership
        # Site = rt.models.tickets.Site
        # ContentType = rt.models.contenttypes.ContentType
        # ct_Ticket = ContentType.objects.get_for_model(Ticket)

        robin = create(User,
                       username='robin',
                       first_name="Robin",
                       user_type=UserTypes.admin,
                       language="en")
        robin_group = create(Group, name="My Group")
        # site = create(Site, name='project', group=robin_group)
        #create(Subscription, site=site, user=robin)
        create(Membership, group=robin_group, user=robin)

        def createit():
            return create(Ticket, summary="Test", user=robin, group=robin_group)

        #
        # If there are no vetos, user can ask to delete it
        #
        ticket = createit()
        ticket.delete()

        ticket = createit()

        # we cannot delete the user because a ticket refers to it:

        try:
            robin.delete()
            self.fail("Expected veto")
        except Warning as e:
            self.assertEqual(
                str(e), "Cannot delete User Robin "
                "because 1 Tickets refer to it.")

        self.assertEqual(Membership.objects.count(), 1)
        self.assertEqual(Ticket.objects.count(), 1)

        # when we have deleted the ticket, deleting the user works
        # because the subscription is deleted in cascade:

        ticket.delete()
        #robin_group.delete()
        robin.delete()
        self.assertEqual(Membership.objects.count(), 0)
        self.assertEqual(Ticket.objects.count(), 0)
        self.assertEqual(User.objects.count(), 0)

        # another issue:

        robin = create(User,
                       username='robin',
                       first_name="Robin",
                       user_type=UserTypes.admin,
                       language="en")
        ar = rt.login("robin")
        Session = rt.models.working.Session
        Message = rt.models.checkdata.Message
        ReportingRule = rt.models.working.ReportingRule
        create(ReportingRule)  # avoid No reporting rule for 29.12.2023
        sd = i2d(20231229)
        st = datetime.time(hour=10, second=10)
        et = datetime.time(hour=10, second=20)
        ses = Session(ticket=createit(),
                      start_date=sd,
                      start_time=st,
                      end_time=et)
        ses.on_create(ar)
        ses.full_clean()
        self.assertEqual('0:00', str(ses.duration))
        self.assertEqual('0:00', str(ses.computed_duration))
        ses.save()

        ZEROD = Duration('0:00')
        self.assertEqual('0:00', str(ZEROD))
        self.assertFalse(ZEROD)  # Duration('0:00') is considered false
        self.assertTrue('0:00')  # but a str '0:00' is considered true

        self.assertEqual(1, Session.objects.count())
        ses = Session.objects.first()
        self.assertEqual(ses.start_date, sd)
        self.assertEqual(ses.end_date, sd)
        self.assertEqual(ses.start_time, st)
        self.assertEqual(ses.end_time, et)
        self.assertTrue(ses.start_date)
        self.assertTrue(ses.start_time)
        self.assertTrue(ses.end_time)
        self.assertFalse(ses.end_time < ses.start_time)
        self.assertEqual('0:00', str(ses.duration))
        self.assertEqual('0:00', str(ses.computed_duration))

        with ar.capture_logger("WARNING"):
            ses.check_data.run_from_ui(ar)

        # before 20231230 we had:
        # msg = Message.objects.get(owner_id=ses.pk)
        # self.assertEqual("(★) Duration is None but should be 0:00", msg.message)

        self.assertEqual(Message.objects.count(), 0)
