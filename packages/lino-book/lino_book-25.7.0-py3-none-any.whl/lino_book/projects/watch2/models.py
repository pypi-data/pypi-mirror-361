# Copyright 2013-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from lino.api import dd
from lino import mixins
from lino.modlib.users.mixins import UserAuthored

# contacts = dd.resolve_app('contacts')


class Company(dd.Model):

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    name = models.CharField(_("Name"), blank=True, max_length=200)
    street = models.CharField(_("Street"), blank=True, max_length=200)
    city = models.CharField(_("City"), blank=True, max_length=200)

    def __str__(self):
        return self.name


class EntryType(mixins.BabelDesignated):

    class Meta:
        verbose_name = _("Entry Type")
        verbose_name_plural = _("Entry Types")


class EntryTypes(dd.Table):
    model = EntryType


class Entry(UserAuthored):

    class Meta:
        verbose_name = _("Entry")
        verbose_name_plural = _("Entries")

    date = models.DateField(_("Date"))
    entry_type = dd.ForeignKey(EntryType)
    subject = models.CharField(_("Subject"), blank=True, max_length=200)
    body = dd.RichTextField(_("Body"), blank=True)
    company = dd.ForeignKey(Company)


class Entries(dd.Table):
    model = Entry
    detail_layout = """
    id user date company
    subject
    body
    """
    insert_layout = """
    user date company
    subject
    """
    parameters = mixins.ObservedDateRange(
        entry_type=dd.ForeignKey(
            EntryType,
            blank=True,
            null=True,
            help_text=_("Show only entries of this type.")),
        company=dd.ForeignKey(
            Company,
            blank=True,
            null=True,
            help_text=_("Show only entries of this company.")),
        user=dd.ForeignKey(settings.SITE.user_model,
                           blank=True,
                           null=True,
                           help_text=_("Show only entries by this user.")))
    params_layout = """
    user start_date end_date
    company entry_type
    """

    @classmethod
    def get_request_queryset(cls, ar):
        qs = super().get_request_queryset(ar)
        if (pv := ar.param_values) is None:
            return qs
        if pv.end_date:
            qs = qs.filter(date__lte=pv.end_date)
        if pv.start_date:
            qs = qs.filter(date__gte=pv.start_date)
        if pv.user:
            qs = qs.filter(user=pv.user)
        if pv.entry_type:
            qs = qs.filter(entry_type=pv.entry_type)
        if pv.company:
            qs = qs.filter(company=pv.company)
        return qs

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(Entries, cls).param_defaults(ar, **kw)
        kw.update(user=ar.get_user())
        return kw


class EntriesByCompany(Entries):
    master_key = 'company'


class CompanyDetail(dd.DetailLayout):
    main = """
    name
    street city
    EntriesByCompany
    """


class Companies(dd.Table):
    model = Company
    detail_layout = CompanyDetail()


class CompaniesWithEntryTypes(dd.VentilatingTable, Companies):
    label = _("Companies with Entry Types")
    hide_zero_rows = True
    parameters = mixins.ObservedDateRange()
    params_layout = "start_date end_date"
    editable = False
    auto_fit_column_widths = True

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(CompaniesWithEntryTypes, cls).param_defaults(ar, **kw)
        kw.update(end_date=settings.SITE.today())
        return kw

    @classmethod
    def get_ventilated_columns(self):

        def w(et):
            # return a getter function for a RequestField on the given
            # EntryType.

            def func(fld, obj, ar):
                # mi = ar.master_instance
                # if mi is None: return None
                pv = dict(start_date=ar.param_values.start_date,
                          end_date=ar.param_values.end_date)
                if et is not None:
                    pv.update(entry_type=et)
                pv.update(company=obj, user=ar.get_user())
                return Entries.create_request(param_values=pv)

            return func

        for et in EntryType.objects.all():
            yield dd.RequestField(w(et), verbose_name=str(et))
        yield dd.RequestField(w(None), verbose_name=_("Total"))


@dd.receiver(dd.post_save, sender=EntryType)
def my_setup_columns(sender, **kw):
    CompaniesWithEntryTypes.setup_columns()


# @dd.receiver(dd.post_startup)
# def my_details_setup(sender, **kw):
#     self = sender
#     self.models.contacts.Companies.add_detail_tab(
#         'entries', 'watch2.EntriesByCompany')
