from django.db import models
from lino.api import dd, _

from lino.modlib.users.mixins import My, UserAuthored


class Entry(UserAuthored):

    class Meta:
        verbose_name = _("Entry")
        verbose_name_plural = _("Entries")

    subject = models.CharField(_("Subject"), blank=True, max_length=200)
    body = dd.RichTextField(_("Body"), blank=True)
    company = dd.ForeignKey('contacts.Company')


class Entries(dd.Table):
    model = Entry

    detail_layout = """
    id user
    company
    subject
    body
    """

    insert_layout = """
    company
    subject
    """


class EntriesByCompany(Entries):
    master_key = 'company'


class MyEntries(My, Entries):
    pass


# @dd.receiver(dd.post_startup)
# def my_change_watchers(sender, **kw):
