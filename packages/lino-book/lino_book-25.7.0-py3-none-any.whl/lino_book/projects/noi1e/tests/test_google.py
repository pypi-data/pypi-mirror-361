# -*- coding: utf-8 -*-
# Copyright 2016-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# python manage.py test tests.test_google
"""Runs some tests about the google synchronization.

"""

import datetime
import json
import logging
import unittest

from pathlib import Path

from googleapiclient.errors import HttpError

from django.conf import settings

from lino.api import dd, rt
from lino.utils.djangotest import TestCase
from lino.utils import logging_disabled
from lino_xl.lib.google.exceptions import AccessLocked

DISABLE_LOG_DOWN_TO = logging.INFO
Country = rt.models.countries.Country
Calendar = rt.models.cal.Calendar
Event = rt.models.cal.Event
Room = rt.models.cal.Room
Guest = rt.models.cal.Guest
Partner = dd.resolve_model(dd.plugins.cal.partner_model)
CalendarSubscription = rt.models.google.CalendarSubscription
ContactSyncToken = rt.models.google.ContactSyncToken

UserSocialAuth = rt.models.social_django.UserSocialAuth
User = rt.models.users.User
Contact = rt.models.google.Contact
demo_google_user = Path(__file__).parent / "demo_google_user.json"
# demo_google_user = settings.SITE.media_root / "demo_google_user.json"
user: User = None
suser: UserSocialAuth = None


def prepare_db():
    global user
    user = User(username="robin")
    user.user_type = rt.models.users.UserTypes.admin
    user.set_password(dd.plugins.users.demo_password)
    user.full_clean()
    user.save()
    with demo_google_user.open('r') as f:
        data = json.load(f)
    global suser
    suser = UserSocialAuth(user=user, provider="google", **data)
    suser.full_clean()
    suser.save()

    cal = Calendar(name="General")
    cal.full_clean()
    cal.save_new_instance(Calendar.get_default_table().create_request(user=user))

    r = Room(calendar=cal, name="General")
    r.full_clean()
    r.save_new_instance(Room.get_default_table().create_request(user=user))

    sub = CalendarSubscription(calendar=cal, user=user)
    sub.full_clean()
    sub.save_new_instance(
        CalendarSubscription.get_default_table().create_request(user=user))
    e = Event(summary="dummy",
              start_date=dd.today(),
              start_time=(st_time__d_ := datetime.datetime.now()).time(),
              room=r)
    e.end_date = e.start_date
    e.end_time = (st_time__d_ + datetime.timedelta(hours=2)).time()
    e.full_clean()
    e.save_new_instance(Event.get_default_table().create_request(user=user))

    partner = Partner(name=user.first_name or user.username)
    partner.full_clean()
    partner.save_new_instance(Partner.get_default_table().create_request(user=user))

    guest = Guest(event=e, partner=partner)
    guest.full_clean()
    guest.save_new_instance(Guest.get_default_table().create_request(user=user))

    bd = Country(isocode="BD", name="Bangladesh")
    bd.full_clean()
    bd.save_new_instance(Country.get_default_table().create_request(user=user))

    ee = Country(isocode="EE", name="Estonia")
    ee.full_clean()
    ee.save_new_instance(Country.get_default_table().create_request(user=user))


def dump_user():
    suser = UserSocialAuth.objects.get(user__username='robin',
                                       provider='google')
    data = {"uid": suser.uid, "extra_data": suser.extra_data}
    with demo_google_user.open("w") as f:
        json.dump(data, f, indent=4)


# @unittest.skip("20210527")
class TestCase(TestCase):
    """Miscellaneous tests."""
    maxDiff = None

    def setUp(self):
        prepare_db()
        global user
        self.synchronizer = rt.models.google.Synchronizer(user)

    @unittest.skip("debug skip")
    def test_calendar(self):
        global user
        res = rt.models.google.build("calendar",
                                     "v3",
                                     credentials=self.synchronizer.credentials)
        cals = rt.models.google.make_api_call(lambda x: x.calendarList().list(
            minAccessRole="reader", showHidden=True, showDeleted=True),
                                              args=(res, ))

        self.assertIsNotNone(
            cals, "There was something wrong in making the api call.")

        calendars = {
            'kind':
            'calendar#calendarList',
            'items': [{
                'kind': 'calendar#calendarListEntry',
                'id': 'en.bd#holiday@group.v.calendar.google.com',
                'summary': 'Holidays in Bangladesh',
                'description': 'Holidays and Observances in Bangladesh',
                'timeZone': 'Asia/Dhaka',
                'colorId': '8',
                'backgroundColor': '#16a765',
                'foregroundColor': '#000000',
                'selected': True,
                'accessRole': 'reader',
                'defaultReminders': [],
                'conferenceProperties': {
                    'allowedConferenceSolutionTypes': ['hangoutsMeet']
                }
            }, {
                'kind': 'calendar#calendarListEntry',
                'id': 'bh88s6ld4gm5o0rut44g1pv4d8@group.calendar.google.com',
                'summary': 'LinoAmici',
                'description':
                'A Lino Amici specific public calendar hosted on Google.',
                'timeZone': 'UTC',
                'colorId': '6',
                'backgroundColor': '#ffad46',
                'foregroundColor': '#000000',
                'selected': True,
                'accessRole': 'writer',
                'defaultReminders': [],
                'conferenceProperties': {
                    'allowedConferenceSolutionTypes': ['hangoutsMeet']
                }
            }, {
                'kind': 'calendar#calendarListEntry',
                'id': 'noi1euser@gmail.com',
                'summary': 'noi1euser@gmail.com',
                'timeZone': 'Asia/Dhaka',
                'colorId': '14',
                'backgroundColor': '#9fe1e7',
                'foregroundColor': '#000000',
                'selected': True,
                'accessRole': 'owner',
                'defaultReminders': [{
                    'method': 'popup',
                    'minutes': 30
                }],
                'notificationSettings': {
                    'notifications': [{
                        'type': 'eventCreation',
                        'method': 'email'
                    }, {
                        'type': 'eventChange',
                        'method': 'email'
                    }, {
                        'type': 'eventCancellation',
                        'method': 'email'
                    }, {
                        'type': 'eventResponse',
                        'method': 'email'
                    }]
                },
                'primary': True,
                'conferenceProperties': {
                    'allowedConferenceSolutionTypes': ['hangoutsMeet']
                }
            }, {
                'kind':
                'calendar#calendarListEntry',
                'id':
                'addressbook#contacts@group.v.calendar.google.com',
                'summary':
                'Birthdays',
                'description':
                'Displays birthdays, anniversaries, and other event dates of people in Google '
                'Contacts.',
                'timeZone':
                'Asia/Dhaka',
                'colorId':
                '13',
                'backgroundColor':
                '#92e1c0',
                'foregroundColor':
                '#000000',
                'selected':
                True,
                'accessRole':
                'reader',
                'defaultReminders': [],
                'conferenceProperties': {
                    'allowedConferenceSolutionTypes': ['hangoutsMeet']
                }
            }]
        }

        junk_from_last_sync_failure = None

        for cal in cals.get("items", []):
            if cal.get('summary') == 'General':
                junk_from_last_sync_failure = cal
                continue
            if cal.get("deleted", False):
                Calendar.delete_google_calendar(cal, self.synchronizer)
                continue
            calendar, room = Calendar.insert_or_update_google_calendar(
                cal, self.synchronizer)
            self.assertIsNotNone(calendar.pk)
            try:
                subscription = CalendarSubscription.objects.get(
                    user=user, calendar=calendar)
            except CalendarSubscription.DoesNotExist:
                subscription = CalendarSubscription(user=user,
                                                    calendar=calendar)
                ar = CalendarSubscription.get_default_table().create_request(
                    user=user)
                subscription.full_clean()
                subscription.save_new_instance(ar)
            subscription.primary = cal.get("primary", False)
            subscription.access_role = cal.get("accessRole", "reader")
            subscription.full_clean()
            subscription.save()

            events = rt.models.google.make_api_call(lambda x: x.events().list(
                calendarId=calendar.google_id, maxResults=5),
                                                    args=(res, ))

            self.assertIsNotNone(
                events, "There was something wrong in making the api call")

            if items := events['items']:
                for item in items:
                    event = Event.insert_or_update_google_event(
                        item, room, self.synchronizer)
                    self.assertIsNotNone(event.pk)

        if junk_from_last_sync_failure is not None:
            rt.models.google.make_api_call(lambda x: x.delete(
                calendarId=junk_from_last_sync_failure['id']),
                                           args=(res.calendars(), ))
            cals['items'].remove(junk_from_last_sync_failure)

        cals.pop("etag")
        nextPageToken = cals.pop('nextPageToken', None)
        nextSyncToken = cals.pop("nextSyncToken", None)

        items = []
        for item in cals['items']:
            if item.get('deleted'):
                continue
            item.pop("etag")
            items.append(item)
        cals['items'] = items

        self.assertDictEqual(cals, calendars)

        if nextPageToken:
            while True:
                cals = rt.models.google.make_api_call(
                    lambda x: x.calendarList().list(minAccessRole="reader",
                                                    showHidden=True,
                                                    showDeleted=True,
                                                    pageToken=nextPageToken),
                    args=(res, ))

                self.assertIsNotNone(
                    cals, "There was something wrong in making the api call")

                nextPageToken = cals.pop('nextPageToken', None)
                if nextPageToken is None:
                    nextSyncToken = cals.pop("nextSyncToken")
                    break

        # ======================================================================================= #
        # Do outward calendar sync
        # ======================================================================================= #

        settings.SITE.is_demo_site = False

        crs = res.calendars()
        insertable_cals = Calendar.get_outward_insert_update_queryset(user)

        general = insertable_cals[0]

        def delete_all_children(cal):
            rooms = cal.room_calendars.all()
            for room in rooms:
                events = room.event_set.all()
                for event in events:
                    event.guest_set.all().delete()
                events.delete()
            rooms.delete()

        try:
            synchronizer = rt.models.google.Synchronizer(user)
            with logging_disabled(DISABLE_LOG_DOWN_TO):
                synchronizer.sync(cal_only=True)

            ers = res.events()

            general = Calendar.objects.get(pk=general.pk)

            result = rt.models.google.make_api_call(
                lambda x: x.list(calendarId=general.google_id), args=(ers, ))
            event_nextSyncToken = result["nextSyncToken"]
            self.assertEqual(len(result.get('items')), 1)

            result = rt.models.google.make_api_call(
                lambda x: x.calendarList().list(syncToken=nextSyncToken),
                args=(res, ))
            nextSyncToken = result['nextSyncToken']
            for item in result.pop("items"):
                if "items" not in result:
                    result["items"] = []
                if "deleted" not in item or not item['deleted']:
                    result['items'].append(item)
            self.assertEqual(len(result.get('items')), 1)

            for cal in insertable_cals:
                delete_all_children(cal)

            insertable_cals.delete()

            with logging_disabled(DISABLE_LOG_DOWN_TO):
                synchronizer.sync(cal_only=True)

            result = rt.models.google.make_api_call(lambda x: x.list(
                calendarId=general.google_id, syncToken=event_nextSyncToken),
                                                    args=(ers, ))
            self.assertEqual(result['items'], [])

        finally:
            # this is just clean up in case of a failure
            try:
                general = Calendar.objects.get(pk=general.pk)
                delete_all_children(general)
                general.delete()
                Event.sync_deleted_records(ers, self.synchronizer)
                Calendar.sync_deleted_records(crs, self.synchronizer)
            except:
                pass

        res.close()
        crs.close()

    # @unittest.skip("debug skip")
    def test_contacts(self):
        global user
        res = rt.models.google.build("people",
                                     "v1",
                                     credentials=self.synchronizer.credentials)
        people = res.people()

        try:
            token = ContactSyncToken.objects.get(user=user)
        except ContactSyncToken.DoesNotExist:
            token = ContactSyncToken(user=user)
            token.full_clean()
            token.save_new_instance(
                ContactSyncToken.get_default_table().create_request())

        def sync_inward():
            res = rt.models.google.make_api_call(lambda x: x.list(
                resourceName="people/me",
                personFields=rt.models.google.Contact.person_fields,
                pageToken=token.page_token,
                syncToken=token.sync_token,
                pageSize=10,
                requestSyncToken=True),
                                                 args=(people.connections(), ))

            if "connections" not in res:
                return res

            for item in res["connections"]:
                if (ks := len(item.keys())) == 2:
                    Contact.delete_google_contact(item, self.synchronizer)
                    continue
                self.assertGreater(ks, 2)
                Contact.insert_or_update_google_contact(
                    item, self.synchronizer)

            token.sync_token = res.get("nextSyncToken", None)
            token.page_token = res.get("nextPageToken", None)
            token.full_clean()
            token.save()

            return res

        resp = sync_inward()
        del resp["nextSyncToken"]

        valid_resourceNames = [
            'people/c7919126001186964561', 'people/c1857006344923552494'
        ]

        contacts = {
            'connections': [{
                'addresses': [{
                    'city': 'Vana-Vigala',
                    'country': 'EE',
                    'countryCode': 'EE',
                    'formattedValue':
                    'Uus 1\n'
                    'Vana-Vigala\n'
                    '78003 Rapla maakond\n'
                    'EE',
                    'metadata': {
                        'primary': True,
                        'source': {
                            'id': '19c5696e8ed09aee',
                            'type': 'CONTACT'}
                    },
                    'postalCode': '78003',
                    'region': 'Rapla maakond',
                    'streetAddress': 'Uus 1'
                }],
                'names': [{
                    'displayName': 'Luc Saffre',
                    'displayNameLastFirst': 'Saffre, Luc',
                    'familyName': 'Saffre',
                    'givenName': 'Luc',
                    'metadata': {
                        'primary': True,
                        'source': {
                            'id': '19c5696e8ed09aee',
                            'type': 'CONTACT'},
                        'sourcePrimary': True
                    },
                    'unstructuredName': 'Luc Saffre'
                }],
                'phoneNumbers': [{
                    'canonicalForm': '+37256672435',
                    'metadata': {
                        'primary': True,
                        'source': {
                            'id': '19c5696e8ed09aee',
                            'type': 'CONTACT'
                        }
                    },
                    'value': '+372 5667 2435'
                }],
                'resourceName':
                'people/c1857006344923552494'
            }, {
                'addresses': [{
                    'city':
                    'Cumilla',
                    'country':
                    'BD',
                    'countryCode':
                    'BD',
                    'formattedType':
                    'Home',
                    'formattedValue':
                    'Kadaba Bangodda Nangalkot\n'
                    'N/A\n'
                    'Cumilla 3580\n'
                    'BD',
                    'metadata': {
                        'primary': True,
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'poBox':
                    'N/A',
                    'postalCode':
                    '3580',
                    'streetAddress':
                    'Kadaba Bangodda Nangalkot',
                    'type':
                    'home'
                }, {
                    'city':
                    'Cumilla',
                    'country':
                    'BD',
                    'countryCode':
                    'BD',
                    'extendedAddress':
                    'WTF',
                    'formattedType':
                    'Work',
                    'formattedValue':
                    '6th floor Bacchu tower '
                    'Bangodda Nangalkot\n'
                    'N/A\n'
                    'WTF, Cumilla 3580\n'
                    'BD',
                    'metadata': {
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'poBox':
                    'N/A',
                    'postalCode':
                    '3580',
                    'streetAddress':
                    '6th floor Bacchu tower '
                    'Bangodda Nangalkot',
                    'type':
                    'work'
                }],
                'birthdays': [{
                    'date': {
                        'day': 5,
                        'month': 11,
                        'year': 1993
                    },
                    'metadata': {
                        'primary': True,
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'text': '11/05/1993'
                }],
                'emailAddresses': [{
                    'formattedType': 'Home',
                    'metadata': {
                        'primary': True,
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'home',
                    'value': 'sharifmehedi24@gmail.com'
                }, {
                    'formattedType': 'Work',
                    'metadata': {
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'work',
                    'value': 'sharifmehedi24@outlook.com'
                }, {
                    'formattedType': 'Other',
                    'metadata': {
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'other',
                    'value': 'sharifmehedi24@yahoo.com'
                }],
                'names': [{
                    'displayName': 'Md Sharif N/A Mehedi N/A',
                    'displayNameLastFirst': 'Mehedi, Md Sharif N/A, '
                    'N/A',
                    'familyName': 'Mehedi',
                    'givenName': 'Sharif',
                    'honorificPrefix': 'Md',
                    'honorificSuffix': 'N/A',
                    'metadata': {
                        'primary': True,
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'},
                        'sourcePrimary': True
                    },
                    'middleName': 'N/A',
                    'phoneticFamilyName': 'Mehedi',
                    'phoneticGivenName': 'Sharif',
                    'phoneticMiddleName': 'N/A',
                    'unstructuredName': 'Md Sharif N/A Mehedi N/A'
                }],
                'nicknames': [{
                    'metadata': {
                        'primary': True,
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'value': 'Blurry'
                }],
                'phoneNumbers': [{
                    'canonicalForm': '+8801831914124',
                    'formattedType': 'Main',
                    'metadata': {
                        'primary': True,
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'main',
                    'value': '1831914124'
                }, {
                    'canonicalForm': '+8801922010499',
                    'formattedType': 'Work',
                    'metadata': {
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'work',
                    'value': '1922010499'
                }, {
                    'canonicalForm': '+8801827612168',
                    'formattedType': 'Home',
                    'metadata': {
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'home',
                    'value': '1827612168'
                }, {
                    'formattedType': 'Mobile',
                    'metadata': {
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'mobile',
                    'value': '81000555'
                }, {
                    'formattedType': 'Home Fax',
                    'metadata': {
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'homeFax',
                    'value': '2545455221'
                }, {
                    'canonicalForm': '+8801555235446',
                    'formattedType': 'Work Fax',
                    'metadata': {
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'workFax',
                    'value': '1555235446'
                }, {
                    'metadata': {
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'value': '45667533234'
                }],
                'resourceName':
                'people/c7919126001186964561',
                'urls': [{
                    'formattedType': 'Work',
                    'metadata': {
                        'primary': True,
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'work',
                    'value': '8lurry.com'
                }, {
                    'formattedType': 'Home Page',
                    'metadata': {
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'homePage',
                    'value': 'saffre-rumma.net/team/sharif'
                }, {
                    'formattedType': 'Blog',
                    'metadata': {
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'blog',
                    'value': '8lurry.com'
                }, {
                    'formattedType': 'Profile',
                    'metadata': {
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'profile',
                    'value': 'github.com/8lurry'
                }, {
                    'formattedType': 'Profile',
                    'metadata': {
                        'source': {
                            'id': '6de66324084f0451',
                            'type': 'CONTACT'
                        }
                    },
                    'type': 'profile',
                    'value': 'gitlab.com/8lurry'
                }]
            }]
        }

        junk_from_last_sync_failure = []
        for item in resp['connections']:
            item.pop("etag")
            if item['resourceName'] not in valid_resourceNames:
                junk_from_last_sync_failure.append(item)

        if junk_from_last_sync_failure:
            for item in junk_from_last_sync_failure:
                resp['connections'].remove(item)
                rt.models.google.make_api_call(lambda x: x.deleteContact(
                    resourceName=item['resourceName']),
                                               args=(people, ))

        self.assertGreaterEqual(resp.pop("totalItems"), 2)
        self.assertGreaterEqual(resp.pop("totalPeople"), 2)

        resp['connections'].sort(key=lambda x: x['resourceName'])

        self.assertDictEqual(resp, contacts)

        token.full_clean()
        token.save()

        sharif = 'people/c7919126001186964561'

        sharif = Contact.objects.get(google_id=sharif)
        sharif.google_id = ""
        sharif.contact.first_name = "S"
        sharif.contact.save()
        sharif.insert_or_update_into_google(people, self.synchronizer)
        sharif.delete()
        Contact.sync_deleted_records(people, self.synchronizer)

        people.close()

        # Contact having no country
        mk = {
            'resourceName':
            'people/c8329834837438475894',
            'names': [{
                'metadata': {
                    'primary': True,
                    'source': {
                        'type': 'CONTACT',
                        'id': '147c7e6b8d875a55'
                    }
                },
                'displayName': 'Maurice Konn',
                'familyName': 'Konn',
                'givenName': 'Maurice',
                'displayNameLastFirst': 'Konn, Maurice',
                'unstructuredName': 'Maurice Konn'
            }],
            'addresses': [{
                'metadata': {
                    'primary': True,
                    'source': {
                        'type': 'CONTACT',
                        'id': '147c7e6b8d875a55'
                    }
                },
                'formattedValue': 'Spordi 5-34',
                'type': 'home',
                'formattedType': 'Home',
                'streetAddress': 'Spordi 5-34'
            }],
            'phoneNumbers': [{
                'metadata': {
                    'primary': True,
                    'source': {
                        'type': 'CONTACT',
                        'id': '147c7e6b8d875a55'
                    }
                },
                'value': '6443 2343',
                'canonicalForm': '+37264432343',
                'type': 'mobile',
                'formattedType': 'Mobile'
            }]
        }

        Contact.insert_or_update_google_contact(mk, self.synchronizer)

    def test_access_lockable(self):
        global user

        d = ContactSyncToken(user=user)
        d.full_clean()
        d.save_new_instance(d.get_default_table().create_request())
        self.assertEqual([obj.pk for obj in ContactSyncToken.objects.all()],
                         [1])

        try:
            [obj for obj in ContactSyncToken.objects.all()
             ]  # truly make the db call by iterating over the queryset
        except AccessLocked:
            pass
        else:
            # Failed to lock access
            raise Exception

        try:
            ContactSyncToken.objects.get(pk=d.pk)
        except AccessLocked:
            pass
        else:
            # Failed to lock access
            raise Exception

        self.assertEqual(ContactSyncToken.get_locked_objects_pk(), [1])
        d = ContactSyncToken._force_get(pk=1)
        d.save()
        self.assertEqual(
            ContactSyncToken.objects.filter(locked=True).count(), 0)

        d.delete()
        d, created = ContactSyncToken.objects.get_or_create(user=user)
        self.assertEqual(created, True)
        self.assertEqual(d.locked, False)

    def tearDown(self):
        global user
        rt.models.google.update_creds(user, self.synchronizer.credentials)
        dump_user()
        super().tearDown()
