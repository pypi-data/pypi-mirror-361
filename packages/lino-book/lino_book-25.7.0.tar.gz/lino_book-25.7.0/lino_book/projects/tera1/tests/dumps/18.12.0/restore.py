#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# This is a Python dump created using dump2py.
# DJANGO_SETTINGS_MODULE was 'lino_book.projects.tera1.settings.demo', TIME_ZONE was u'UTC'.

from __future__ import unicode_literals

import logging

logger = logging.getLogger('lino.management.commands.dump2py')

SOURCE_VERSION = '18.12.0'

import os
import six
from decimal import Decimal
from datetime import datetime
from datetime import time, date
from django.conf import settings
from django.utils.timezone import make_aware, utc
from django.core.management import call_command
# from django.contrib.contenttypes.models import ContentType
from lino.utils.dpy import create_mti_child
from lino.utils.dpy import DpyLoader
from lino.core.utils import resolve_model

if settings.USE_TZ:

    def dt(*args):
        return make_aware(datetime(*args), timezone=utc)
else:

    def dt(*args):
        return datetime(*args)


def new_content_type_id(m):
    if m is None: return m
    ct = settings.SITE.models.contenttypes.ContentType.objects.get_for_model(m)
    if ct is None: return None
    return ct.pk


def pmem():
    # Thanks to https://stackoverflow.com/questions/938733/total-memory-used-by-python-process
    process = psutil.Process(os.getpid())
    print(process.memory_info().rss)


def execfile(fn, *args):
    logger.info("Execute file %s ...", fn)
    six.exec_(compile(open(fn, "rb").read(), fn, 'exec'), *args)
    # pmem()  # requires pip install psutil


def bv2kw(fieldname, values):
    """
    Needed if `Site.languages` changed between dumpdata and loaddata
    """
    return settings.SITE.babelkw(fieldname,
                                 en=values[0],
                                 de=values[1],
                                 fr=values[2])


ana_Account = resolve_model("ana.Account")
ana_AnaAccountInvoice = resolve_model("ana.AnaAccountInvoice")
ana_InvoiceItem = resolve_model("ana.InvoiceItem")
bevats_Declaration = resolve_model("bevats.Declaration")
cal_Calendar = resolve_model("cal.Calendar")
cal_DailyPlannerRow = resolve_model("cal.DailyPlannerRow")
cal_Event = resolve_model("cal.Event")
cal_EventPolicy = resolve_model("cal.EventPolicy")
cal_EventType = resolve_model("cal.EventType")
cal_Guest = resolve_model("cal.Guest")
cal_GuestRole = resolve_model("cal.GuestRole")
cal_RecurrentEvent = resolve_model("cal.RecurrentEvent")
cal_RemoteCalendar = resolve_model("cal.RemoteCalendar")
cal_Room = resolve_model("cal.Room")
cal_Subscription = resolve_model("cal.Subscription")
cal_Task = resolve_model("cal.Task")
checkdata_Problem = resolve_model("checkdata.Problem")
clients_ClientContact = resolve_model("clients.ClientContact")
clients_ClientContactType = resolve_model("clients.ClientContactType")
contacts_Company = resolve_model("contacts.Company")
contacts_CompanyType = resolve_model("contacts.CompanyType")
contacts_Partner = resolve_model("contacts.Partner")
contacts_Person = resolve_model("contacts.Person")
contacts_Role = resolve_model("contacts.Role")
contacts_RoleType = resolve_model("contacts.RoleType")
countries_Country = resolve_model("countries.Country")
countries_Place = resolve_model("countries.Place")
courses_Course = resolve_model("courses.Course")
courses_Enrolment = resolve_model("courses.Enrolment")
courses_Line = resolve_model("courses.Line")
courses_PriceRule = resolve_model("courses.PriceRule")
courses_Slot = resolve_model("courses.Slot")
courses_Topic = resolve_model("courses.Topic")
dashboard_Widget = resolve_model("dashboard.Widget")
excerpts_Excerpt = resolve_model("excerpts.Excerpt")
excerpts_ExcerptType = resolve_model("excerpts.ExcerptType")
finan_BankStatement = resolve_model("finan.BankStatement")
finan_BankStatementItem = resolve_model("finan.BankStatementItem")
finan_JournalEntry = resolve_model("finan.JournalEntry")
finan_JournalEntryItem = resolve_model("finan.JournalEntryItem")
finan_PaymentOrder = resolve_model("finan.PaymentOrder")
finan_PaymentOrderItem = resolve_model("finan.PaymentOrderItem")
gfks_HelpText = resolve_model("gfks.HelpText")
healthcare_Plan = resolve_model("healthcare.Plan")
healthcare_Rule = resolve_model("healthcare.Rule")
households_Household = resolve_model("households.Household")
households_Member = resolve_model("households.Member")
households_Type = resolve_model("households.Type")
invoicing_Item = resolve_model("invoicing.Item")
invoicing_Plan = resolve_model("invoicing.Plan")
invoicing_SalesRule = resolve_model("invoicing.SalesRule")
invoicing_Tariff = resolve_model("invoicing.Tariff")
ledger_Account = resolve_model("accounting.Account")
ledger_AccountingPeriod = resolve_model("accounting.AccountingPeriod")
ledger_FiscalYear = resolve_model("accounting.FiscalYear")
ledger_Journal = resolve_model("accounting.Journal")
ledger_LedgerInfo = resolve_model("accounting.LedgerInfo")
ledger_MatchRule = resolve_model("accounting.MatchRule")
ledger_Movement = resolve_model("accounting.Movement")
ledger_PaymentTerm = resolve_model("accounting.PaymentTerm")
ledger_Voucher = resolve_model("accounting.Voucher")
lists_List = resolve_model("lists.List")
lists_ListType = resolve_model("lists.ListType")
lists_Member = resolve_model("lists.Member")
notes_EventType = resolve_model("notes.EventType")
notes_Note = resolve_model("notes.Note")
notes_NoteType = resolve_model("notes.NoteType")
products_Product = resolve_model("products.Product")
products_Category = resolve_model("products.Category")
sales_InvoiceItem = resolve_model("trading.InvoiceItem")
sales_PaperType = resolve_model("trading.PaperType")
sales_VatProductInvoice = resolve_model("trading.VatProductInvoice")
sepa_Account = resolve_model("sepa.Account")
sheets_AccountEntry = resolve_model("sheets.AccountEntry")
sheets_AnaAccountEntry = resolve_model("sheets.AnaAccountEntry")
sheets_Item = resolve_model("sheets.Item")
sheets_ItemEntry = resolve_model("sheets.ItemEntry")
sheets_PartnerEntry = resolve_model("sheets.PartnerEntry")
sheets_Report = resolve_model("sheets.Report")
system_SiteConfig = resolve_model("system.SiteConfig")
teams_Team = resolve_model("teams.Team")
tera_Client = resolve_model("tera.Client")
tera_LifeMode = resolve_model("tera.LifeMode")
tera_Procurer = resolve_model("tera.Procurer")
tinymce_TextFieldTemplate = resolve_model("tinymce.TextFieldTemplate")
topics_Interest = resolve_model("topics.Interest")
topics_Topic = resolve_model("topics.Topic")
users_Authority = resolve_model("users.Authority")
users_User = resolve_model("users.User")
vat_InvoiceItem = resolve_model("vat.InvoiceItem")
vat_VatAccountInvoice = resolve_model("vat.VatAccountInvoice")


def create_ana_account(id, ref, seqno, designation):
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    kw.update(seqno=seqno)
    if designation is not None: kw.update(bv2kw('designation', designation))
    return ana_Account(**kw)


def create_cal_calendar(id, name, description, color):
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(description=description)
    kw.update(color=color)
    return cal_Calendar(**kw)


def create_cal_dailyplannerrow(id, seqno, designation, start_time, end_time):
    kw = dict()
    kw.update(id=id)
    kw.update(seqno=seqno)
    if designation is not None: kw.update(bv2kw('designation', designation))
    kw.update(start_time=start_time)
    kw.update(end_time=end_time)
    return cal_DailyPlannerRow(**kw)


def create_cal_eventtype(id, ref, seqno, name, attach_to_email, email_template,
                         description, is_appointment, all_rooms, locks_user,
                         force_guest_states, start_date, event_label,
                         max_conflicting, max_days, transparent,
                         planner_column):
    #    if planner_column: planner_column = settings.SITE.models.cal.PlannerColumns.get_by_value(planner_column)
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    kw.update(seqno=seqno)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(attach_to_email=attach_to_email)
    kw.update(email_template=email_template)
    kw.update(description=description)
    kw.update(is_appointment=is_appointment)
    kw.update(all_rooms=all_rooms)
    kw.update(locks_user=locks_user)
    kw.update(force_guest_states=force_guest_states)
    kw.update(start_date=start_date)
    if event_label is not None: kw.update(bv2kw('event_label', event_label))
    kw.update(max_conflicting=max_conflicting)
    kw.update(max_days=max_days)
    kw.update(transparent=transparent)
    kw.update(planner_column=planner_column)
    return cal_EventType(**kw)


def create_cal_eventpolicy(id, start_date, start_time, end_date, end_time,
                           name, every_unit, every, monday, tuesday, wednesday,
                           thursday, friday, saturday, sunday, max_events,
                           event_type_id):
    #    if every_unit: every_unit = settings.SITE.models.cal.Recurrences.get_by_value(every_unit)
    kw = dict()
    kw.update(id=id)
    kw.update(start_date=start_date)
    kw.update(start_time=start_time)
    kw.update(end_date=end_date)
    kw.update(end_time=end_time)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(every_unit=every_unit)
    kw.update(every=every)
    kw.update(monday=monday)
    kw.update(tuesday=tuesday)
    kw.update(wednesday=wednesday)
    kw.update(thursday=thursday)
    kw.update(friday=friday)
    kw.update(saturday=saturday)
    kw.update(sunday=sunday)
    kw.update(max_events=max_events)
    kw.update(event_type_id=event_type_id)
    return cal_EventPolicy(**kw)


def create_cal_guestrole(id, ref, name, is_teacher):
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(is_teacher=is_teacher)
    return cal_GuestRole(**kw)


def create_cal_remotecalendar(id, seqno, type, url_template, username,
                              password, readonly):
    kw = dict()
    kw.update(id=id)
    kw.update(seqno=seqno)
    kw.update(type=type)
    kw.update(url_template=url_template)
    kw.update(username=username)
    kw.update(password=password)
    kw.update(readonly=readonly)
    return cal_RemoteCalendar(**kw)


def create_clients_clientcontacttype(id, name, known_contact_type):
    #    if known_contact_type: known_contact_type = settings.SITE.models.clients.KnownContactTypes.get_by_value(known_contact_type)
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(known_contact_type=known_contact_type)
    return clients_ClientContactType(**kw)


def create_contacts_companytype(id, name, abbr):
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name', name))
    if abbr is not None: kw.update(bv2kw('abbr', abbr))
    return contacts_CompanyType(**kw)


def create_contacts_roletype(id, name):
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name', name))
    return contacts_RoleType(**kw)


def create_countries_country(name, isocode, short_code, iso3):
    kw = dict()
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(isocode=isocode)
    kw.update(short_code=short_code)
    kw.update(iso3=iso3)
    return countries_Country(**kw)


def create_countries_place(id, parent_id, name, country_id, zip_code, type,
                           show_type):
    #    if type: type = settings.SITE.models.countries.PlaceTypes.get_by_value(type)
    kw = dict()
    kw.update(id=id)
    kw.update(parent_id=parent_id)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(country_id=country_id)
    kw.update(zip_code=zip_code)
    kw.update(type=type)
    kw.update(show_type=show_type)
    return countries_Place(**kw)


def create_courses_slot(id, seqno, start_time, end_time, name):
    kw = dict()
    kw.update(id=id)
    kw.update(seqno=seqno)
    kw.update(start_time=start_time)
    kw.update(end_time=end_time)
    kw.update(name=name)
    return courses_Slot(**kw)


def create_courses_topic(id, name):
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name', name))
    return courses_Topic(**kw)


def create_excerpts_excerpttype(id, name, build_method, template,
                                attach_to_email, email_template, certifying,
                                remark, body_template, content_type_id,
                                primary, backward_compat, print_recipient,
                                print_directly, shortcut):
    #    if build_method: build_method = settings.SITE.models.printing.BuildMethods.get_by_value(build_method)
    content_type_id = new_content_type_id(content_type_id)
    #    if shortcut: shortcut = settings.SITE.models.excerpts.Shortcuts.get_by_value(shortcut)
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(build_method=build_method)
    kw.update(template=template)
    kw.update(attach_to_email=attach_to_email)
    kw.update(email_template=email_template)
    kw.update(certifying=certifying)
    kw.update(remark=remark)
    kw.update(body_template=body_template)
    kw.update(content_type_id=content_type_id)
    kw.update(primary=primary)
    kw.update(backward_compat=backward_compat)
    kw.update(print_recipient=print_recipient)
    kw.update(print_directly=print_directly)
    kw.update(shortcut=shortcut)
    return excerpts_ExcerptType(**kw)


def create_gfks_helptext(id, content_type_id, field, help_text):
    content_type_id = new_content_type_id(content_type_id)
    kw = dict()
    kw.update(id=id)
    kw.update(content_type_id=content_type_id)
    kw.update(field=field)
    kw.update(help_text=help_text)
    return gfks_HelpText(**kw)


def create_households_type(id, name):
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name', name))
    return households_Type(**kw)


def create_invoicing_tariff(id, designation, number_of_events, min_asset,
                            max_asset):
    kw = dict()
    kw.update(id=id)
    if designation is not None: kw.update(bv2kw('designation', designation))
    kw.update(number_of_events=number_of_events)
    kw.update(min_asset=min_asset)
    kw.update(max_asset=max_asset)
    return invoicing_Tariff(**kw)


def create_ledger_fiscalyear(id, ref, start_date, end_date, state):
    #    if state: state = settings.SITE.models.accounting.PeriodStates.get_by_value(state)
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    kw.update(start_date=start_date)
    kw.update(end_date=end_date)
    kw.update(state=state)
    return ledger_FiscalYear(**kw)


def create_ledger_accountingperiod(id, ref, start_date, end_date, state,
                                   year_id, remark):
    #    if state: state = settings.SITE.models.accounting.PeriodStates.get_by_value(state)
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    kw.update(start_date=start_date)
    kw.update(end_date=end_date)
    kw.update(state=state)
    kw.update(year_id=year_id)
    kw.update(remark=remark)
    return ledger_AccountingPeriod(**kw)


def create_ledger_paymentterm(id, ref, name, days, months, end_of_month,
                              printed_text):
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(days=days)
    kw.update(months=months)
    kw.update(end_of_month=end_of_month)
    if printed_text is not None: kw.update(bv2kw('printed_text', printed_text))
    return ledger_PaymentTerm(**kw)


def create_lists_listtype(id, designation):
    kw = dict()
    kw.update(id=id)
    if designation is not None: kw.update(bv2kw('designation', designation))
    return lists_ListType(**kw)


def create_lists_list(id, ref, designation, list_type_id, remarks):
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    if designation is not None: kw.update(bv2kw('designation', designation))
    kw.update(list_type_id=list_type_id)
    kw.update(remarks=remarks)
    return lists_List(**kw)


def create_notes_eventtype(id, name, remark, body):
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(remark=remark)
    if body is not None: kw.update(bv2kw('body', body))
    return notes_EventType(**kw)


def create_notes_notetype(id, name, build_method, template, attach_to_email,
                          email_template, important, remark, special_type):
    #    if build_method: build_method = settings.SITE.models.printing.BuildMethods.get_by_value(build_method)
    #    if special_type: special_type = settings.SITE.models.notes.SpecialTypes.get_by_value(special_type)
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(build_method=build_method)
    kw.update(template=template)
    kw.update(attach_to_email=attach_to_email)
    kw.update(email_template=email_template)
    kw.update(important=important)
    kw.update(remark=remark)
    kw.update(special_type=special_type)
    return notes_NoteType(**kw)


def create_products_productcat(id, name, description):
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(description=description)
    return products_Category(**kw)


def create_sales_papertype(id, name, template):
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(template=template)
    return sales_PaperType(**kw)


def create_sheets_item(id, ref, designation, dc, sheet_type, common_item,
                       mirror_ref):
    #    if sheet_type: sheet_type = settings.SITE.models.sheets.SheetTypes.get_by_value(sheet_type)
    #    if common_item: common_item = settings.SITE.models.sheets.CommonItems.get_by_value(common_item)
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    if designation is not None: kw.update(bv2kw('designation', designation))
    kw.update(dc=dc)
    kw.update(sheet_type=sheet_type)
    kw.update(common_item=common_item)
    kw.update(mirror_ref=mirror_ref)
    return sheets_Item(**kw)


def create_ledger_account(id, ref, seqno, name, sheet_item_id, common_account,
                          needs_partner, clearable, default_amount,
                          sales_allowed, purchases_allowed, wages_allowed,
                          taxes_allowed, clearings_allowed, bank_po_allowed,
                          vat_column, ana_account_id, needs_ana):
    #    if common_account: common_account = settings.SITE.models.accounting.CommonAccounts.get_by_value(common_account)
    if default_amount is not None: default_amount = Decimal(default_amount)
    #    if vat_column: vat_column = settings.SITE.models.vat.VatColumns.get_by_value(vat_column)
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    kw.update(seqno=seqno)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(sheet_item_id=sheet_item_id)
    kw.update(common_account=common_account)
    kw.update(needs_partner=needs_partner)
    kw.update(clearable=clearable)
    kw.update(default_amount=default_amount)
    kw.update(sales_allowed=sales_allowed)
    kw.update(purchases_allowed=purchases_allowed)
    kw.update(wages_allowed=wages_allowed)
    kw.update(taxes_allowed=taxes_allowed)
    kw.update(clearings_allowed=clearings_allowed)
    kw.update(bank_po_allowed=bank_po_allowed)
    kw.update(vat_column=vat_column)
    kw.update(ana_account_id=ana_account_id)
    kw.update(needs_ana=needs_ana)
    return ledger_Account(**kw)


def create_contacts_partner(id, email, language, url, phone, gsm, fax,
                            country_id, city_id, zip_code, region_id, addr1,
                            street_prefix, street, street_no, street_box,
                            addr2, prefix, name, remarks,
                            client_contact_type_id, payment_term_id,
                            vat_regime, vat_id, pf_residence, pf_composition,
                            pf_income, purchase_account_id):
    #    if vat_regime: vat_regime = settings.SITE.models.vat.VatRegimes.get_by_value(vat_regime)
    #    if pf_residence: pf_residence = settings.SITE.models.courses.Residences.get_by_value(pf_residence)
    #    if pf_composition: pf_composition = settings.SITE.models.courses.HouseholdCompositions.get_by_value(pf_composition)
    #    if pf_income: pf_income = settings.SITE.models.courses.IncomeCategories.get_by_value(pf_income)
    kw = dict()
    kw.update(id=id)
    kw.update(email=email)
    kw.update(language=language)
    kw.update(url=url)
    kw.update(phone=phone)
    kw.update(gsm=gsm)
    kw.update(fax=fax)
    kw.update(country_id=country_id)
    kw.update(city_id=city_id)
    kw.update(zip_code=zip_code)
    kw.update(region_id=region_id)
    kw.update(addr1=addr1)
    kw.update(street_prefix=street_prefix)
    kw.update(street=street)
    kw.update(street_no=street_no)
    kw.update(street_box=street_box)
    kw.update(addr2=addr2)
    kw.update(prefix=prefix)
    kw.update(name=name)
    kw.update(remarks=remarks)
    kw.update(client_contact_type_id=client_contact_type_id)
    kw.update(payment_term_id=payment_term_id)
    kw.update(vat_regime=vat_regime)
    kw.update(vat_id=vat_id)
    kw.update(pf_residence=pf_residence)
    kw.update(pf_composition=pf_composition)
    kw.update(pf_income=pf_income)
    kw.update(purchase_account_id=purchase_account_id)
    return contacts_Partner(**kw)


def create_contacts_company(partner_ptr_id, type_id):
    kw = dict()
    kw.update(type_id=type_id)
    return create_mti_child(contacts_Partner, partner_ptr_id, contacts_Company,
                            **kw)


def create_contacts_person(partner_ptr_id, title, first_name, middle_name,
                           last_name, gender, birth_date):
    #    if gender: gender = settings.SITE.models.system.Genders.get_by_value(gender)
    kw = dict()
    kw.update(title=title)
    kw.update(first_name=first_name)
    kw.update(middle_name=middle_name)
    kw.update(last_name=last_name)
    kw.update(gender=gender)
    kw.update(birth_date=birth_date)
    return create_mti_child(contacts_Partner, partner_ptr_id, contacts_Person,
                            **kw)


def create_cal_room(id, name, company_id, contact_person_id, contact_role_id,
                    description):
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(company_id=company_id)
    kw.update(contact_person_id=contact_person_id)
    kw.update(contact_role_id=contact_role_id)
    kw.update(description=description)
    return cal_Room(**kw)


def create_clients_clientcontact(id, company_id, contact_person_id,
                                 contact_role_id, type_id, client_id, remark):
    kw = dict()
    kw.update(id=id)
    kw.update(company_id=company_id)
    kw.update(contact_person_id=contact_person_id)
    kw.update(contact_role_id=contact_role_id)
    kw.update(type_id=type_id)
    kw.update(client_id=client_id)
    kw.update(remark=remark)
    return clients_ClientContact(**kw)


def create_contacts_role(id, type_id, person_id, company_id):
    kw = dict()
    kw.update(id=id)
    kw.update(type_id=type_id)
    kw.update(person_id=person_id)
    kw.update(company_id=company_id)
    return contacts_Role(**kw)


def create_healthcare_plan(id, ref, designation, provider_id):
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    if designation is not None: kw.update(bv2kw('designation', designation))
    kw.update(provider_id=provider_id)
    return healthcare_Plan(**kw)


def create_households_household(partner_ptr_id, type_id, client_state):
    #    if client_state: client_state = settings.SITE.models.clients.ClientStates.get_by_value(client_state)
    kw = dict()
    kw.update(type_id=type_id)
    kw.update(client_state=client_state)
    return create_mti_child(contacts_Partner, partner_ptr_id,
                            households_Household, **kw)


def create_households_member(id, start_date, end_date, title, first_name,
                             middle_name, last_name, gender, birth_date, role,
                             person_id, household_id, dependency, primary):
    #    if gender: gender = settings.SITE.models.system.Genders.get_by_value(gender)
    #    if role: role = settings.SITE.models.households.MemberRoles.get_by_value(role)
    #    if dependency: dependency = settings.SITE.models.households.MemberDependencies.get_by_value(dependency)
    kw = dict()
    kw.update(id=id)
    kw.update(start_date=start_date)
    kw.update(end_date=end_date)
    kw.update(title=title)
    kw.update(first_name=first_name)
    kw.update(middle_name=middle_name)
    kw.update(last_name=last_name)
    kw.update(gender=gender)
    kw.update(birth_date=birth_date)
    kw.update(role=role)
    kw.update(person_id=person_id)
    kw.update(household_id=household_id)
    kw.update(dependency=dependency)
    kw.update(primary=primary)
    return households_Member(**kw)


def create_invoicing_salesrule(partner_id, invoice_recipient_id,
                               paper_type_id):
    kw = dict()
    kw.update(partner_id=partner_id)
    kw.update(invoice_recipient_id=invoice_recipient_id)
    kw.update(paper_type_id=paper_type_id)
    return invoicing_SalesRule(**kw)


def create_lists_member(id, seqno, list_id, partner_id, remark):
    kw = dict()
    kw.update(id=id)
    kw.update(seqno=seqno)
    kw.update(list_id=list_id)
    kw.update(partner_id=partner_id)
    kw.update(remark=remark)
    return lists_Member(**kw)


def create_products_product(id, name, description, category_id, delivery_unit,
                            product_type, vat_class, tariff_id,
                            sales_account_id, sales_price):
    #    if delivery_unit: delivery_unit = settings.SITE.models.products.DeliveryUnits.get_by_value(delivery_unit)
    #    if product_type: product_type = settings.SITE.models.products.ProductTypes.get_by_value(product_type)
    #    if vat_class: vat_class = settings.SITE.models.vat.VatClasses.get_by_value(vat_class)
    if sales_price is not None: sales_price = Decimal(sales_price)
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name', name))
    if description is not None: kw.update(bv2kw('description', description))
    kw.update(category_id=category_id)
    kw.update(delivery_unit=delivery_unit)
    kw.update(product_type=product_type)
    kw.update(vat_class=vat_class)
    kw.update(tariff_id=tariff_id)
    kw.update(sales_account_id=sales_account_id)
    kw.update(sales_price=sales_price)
    return products_Product(**kw)


def create_courses_line(id, ref, name, excerpt_title, company_id,
                        contact_person_id, contact_role_id, course_area,
                        topic_id, description, every_unit, every,
                        event_type_id, fee_id, guest_role_id, options_cat_id,
                        fees_cat_id, body_template, invoicing_policy):
    #    if course_area: course_area = settings.SITE.models.courses.ActivityLayouts.get_by_value(course_area)
    #    if every_unit: every_unit = settings.SITE.models.cal.Recurrences.get_by_value(every_unit)
    #    if invoicing_policy: invoicing_policy = settings.SITE.models.courses.InvoicingPolicies.get_by_value(invoicing_policy)
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    if name is not None: kw.update(bv2kw('name', name))
    if excerpt_title is not None:
        kw.update(bv2kw('excerpt_title', excerpt_title))
    kw.update(company_id=company_id)
    kw.update(contact_person_id=contact_person_id)
    kw.update(contact_role_id=contact_role_id)
    kw.update(course_area=course_area)
    kw.update(topic_id=topic_id)
    if description is not None: kw.update(bv2kw('description', description))
    kw.update(every_unit=every_unit)
    kw.update(every=every)
    kw.update(event_type_id=event_type_id)
    kw.update(fee_id=fee_id)
    kw.update(guest_role_id=guest_role_id)
    kw.update(options_cat_id=options_cat_id)
    kw.update(fees_cat_id=fees_cat_id)
    kw.update(body_template=body_template)
    kw.update(invoicing_policy=invoicing_policy)
    return courses_Line(**kw)


def create_courses_pricerule(id, seqno, fee_id, tariff, event_type_id,
                             pf_residence, pf_composition, pf_income):
    #    if tariff: tariff = settings.SITE.models.courses.PartnerTariffs.get_by_value(tariff)
    #    if pf_residence: pf_residence = settings.SITE.models.courses.Residences.get_by_value(pf_residence)
    #    if pf_composition: pf_composition = settings.SITE.models.courses.HouseholdCompositions.get_by_value(pf_composition)
    #    if pf_income: pf_income = settings.SITE.models.courses.IncomeCategories.get_by_value(pf_income)
    kw = dict()
    kw.update(id=id)
    kw.update(seqno=seqno)
    kw.update(fee_id=fee_id)
    kw.update(tariff=tariff)
    kw.update(event_type_id=event_type_id)
    kw.update(pf_residence=pf_residence)
    kw.update(pf_composition=pf_composition)
    kw.update(pf_income=pf_income)
    return courses_PriceRule(**kw)


def create_healthcare_rule(id, plan_id, client_fee_id, provider_fee_id):
    kw = dict()
    kw.update(id=id)
    kw.update(plan_id=plan_id)
    kw.update(client_fee_id=client_fee_id)
    kw.update(provider_fee_id=provider_fee_id)
    return healthcare_Rule(**kw)


def create_sepa_account(id, partner_id, iban, bic, remark, primary):
    kw = dict()
    kw.update(id=id)
    kw.update(partner_id=partner_id)
    kw.update(iban=iban)
    kw.update(bic=bic)
    kw.update(remark=remark)
    kw.update(primary=primary)
    return sepa_Account(**kw)


def create_ledger_journal(id, ref, seqno, name, build_method, template,
                          trade_type, voucher_type, journal_group,
                          auto_check_clearings, auto_fill_suggestions,
                          force_sequence, account_id, partner_id, printed_name,
                          dc, yearly_numbering, must_declare, sepa_account_id):
    #    if build_method: build_method = settings.SITE.models.printing.BuildMethods.get_by_value(build_method)
    #    if trade_type: trade_type = settings.SITE.models.accounting.TradeTypes.get_by_value(trade_type)
    #    if voucher_type: voucher_type = settings.SITE.models.accounting.VoucherTypes.get_by_value(voucher_type)
    #    if journal_group: journal_group = settings.SITE.models.accounting.JournalGroups.get_by_value(journal_group)
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    kw.update(seqno=seqno)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(build_method=build_method)
    kw.update(template=template)
    kw.update(trade_type=trade_type)
    kw.update(voucher_type=voucher_type)
    kw.update(journal_group=journal_group)
    kw.update(auto_check_clearings=auto_check_clearings)
    kw.update(auto_fill_suggestions=auto_fill_suggestions)
    kw.update(force_sequence=force_sequence)
    kw.update(account_id=account_id)
    kw.update(partner_id=partner_id)
    if printed_name is not None: kw.update(bv2kw('printed_name', printed_name))
    kw.update(dc=dc)
    kw.update(yearly_numbering=yearly_numbering)
    kw.update(must_declare=must_declare)
    kw.update(sepa_account_id=sepa_account_id)
    return ledger_Journal(**kw)


def create_ledger_matchrule(id, account_id, journal_id):
    kw = dict()
    kw.update(id=id)
    kw.update(account_id=account_id)
    kw.update(journal_id=journal_id)
    return ledger_MatchRule(**kw)


def create_system_siteconfig(id, default_build_method, simulate_today,
                             site_company_id, default_event_type_id,
                             site_calendar_id, max_auto_events,
                             hide_events_before, next_partner_id,
                             system_note_type_id):
    #    if default_build_method: default_build_method = settings.SITE.models.printing.BuildMethods.get_by_value(default_build_method)
    kw = dict()
    kw.update(id=id)
    kw.update(default_build_method=default_build_method)
    kw.update(simulate_today=simulate_today)
    kw.update(site_company_id=site_company_id)
    kw.update(default_event_type_id=default_event_type_id)
    kw.update(site_calendar_id=site_calendar_id)
    kw.update(max_auto_events=max_auto_events)
    kw.update(hide_events_before=hide_events_before)
    kw.update(next_partner_id=next_partner_id)
    kw.update(system_note_type_id=system_note_type_id)
    return system_SiteConfig(**kw)


def create_teams_team(id, ref, name):
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    if name is not None: kw.update(bv2kw('name', name))
    return teams_Team(**kw)


def create_tera_lifemode(id, designation):
    kw = dict()
    kw.update(id=id)
    if designation is not None: kw.update(bv2kw('designation', designation))
    return tera_LifeMode(**kw)


def create_tera_procurer(id, designation):
    kw = dict()
    kw.update(id=id)
    if designation is not None: kw.update(bv2kw('designation', designation))
    return tera_Procurer(**kw)


def create_topics_topic(id, ref, name, description):
    kw = dict()
    kw.update(id=id)
    kw.update(ref=ref)
    if name is not None: kw.update(bv2kw('name', name))
    if description is not None: kw.update(bv2kw('description', description))
    return topics_Topic(**kw)


def create_users_user(id, email, language, modified, created, start_date,
                      end_date, access_class, event_type_id, password,
                      last_login, username, user_type, initials, first_name,
                      last_name, remarks, time_zone, cash_daybook_id, team_id,
                      partner_id):
    #    if access_class: access_class = settings.SITE.models.cal.AccessClasses.get_by_value(access_class)
    #    if user_type: user_type = settings.SITE.models.users.UserTypes.get_by_value(user_type)
    #    if time_zone: time_zone = settings.SITE.models.about.TimeZones.get_by_value(time_zone)
    kw = dict()
    kw.update(id=id)
    kw.update(email=email)
    kw.update(language=language)
    kw.update(modified=modified)
    kw.update(created=created)
    kw.update(start_date=start_date)
    kw.update(end_date=end_date)
    kw.update(access_class=access_class)
    kw.update(event_type_id=event_type_id)
    kw.update(password=password)
    kw.update(last_login=last_login)
    kw.update(username=username)
    kw.update(user_type=user_type)
    kw.update(initials=initials)
    kw.update(first_name=first_name)
    kw.update(last_name=last_name)
    kw.update(remarks=remarks)
    kw.update(time_zone=time_zone)
    kw.update(cash_daybook_id=cash_daybook_id)
    kw.update(team_id=team_id)
    kw.update(partner_id=partner_id)
    return users_User(**kw)


def create_cal_recurrentevent(id, start_date, start_time, end_date, end_time,
                              name, user_id, every_unit, every, monday,
                              tuesday, wednesday, thursday, friday, saturday,
                              sunday, max_events, event_type_id, description):
    #    if every_unit: every_unit = settings.SITE.models.cal.Recurrences.get_by_value(every_unit)
    kw = dict()
    kw.update(id=id)
    kw.update(start_date=start_date)
    kw.update(start_time=start_time)
    kw.update(end_date=end_date)
    kw.update(end_time=end_time)
    if name is not None: kw.update(bv2kw('name', name))
    kw.update(user_id=user_id)
    kw.update(every_unit=every_unit)
    kw.update(every=every)
    kw.update(monday=monday)
    kw.update(tuesday=tuesday)
    kw.update(wednesday=wednesday)
    kw.update(thursday=thursday)
    kw.update(friday=friday)
    kw.update(saturday=saturday)
    kw.update(sunday=sunday)
    kw.update(max_events=max_events)
    kw.update(event_type_id=event_type_id)
    kw.update(description=description)
    return cal_RecurrentEvent(**kw)


def create_cal_subscription(id, user_id, calendar_id, is_hidden):
    kw = dict()
    kw.update(id=id)
    kw.update(user_id=user_id)
    kw.update(calendar_id=calendar_id)
    kw.update(is_hidden=is_hidden)
    return cal_Subscription(**kw)


def create_checkdata_problem(id, owner_type_id, owner_id, user_id, checker,
                             message):
    owner_type_id = new_content_type_id(owner_type_id)
    #    if checker: checker = settings.SITE.models.checkdata.Checkers.get_by_value(checker)
    kw = dict()
    kw.update(id=id)
    kw.update(owner_type_id=owner_type_id)
    kw.update(owner_id=owner_id)
    kw.update(user_id=user_id)
    kw.update(checker=checker)
    kw.update(message=message)
    return checkdata_Problem(**kw)


def create_courses_course(id, modified, ref, start_date, start_time, end_date,
                          end_time, healthcare_plan_id, user_id, every_unit,
                          every, monday, tuesday, wednesday, thursday, friday,
                          saturday, sunday, max_events, room_id, max_date,
                          line_id, teacher_id, slot_id, description, remark,
                          state, max_places, name, enrolments_until, tariff_id,
                          payment_term_id, procurer_id, mandatory,
                          ending_reason, partner_tariff, translator_type,
                          therapy_domain, team_id, partner_id, paper_type_id):
    #    if every_unit: every_unit = settings.SITE.models.cal.Recurrences.get_by_value(every_unit)
    #    if state: state = settings.SITE.models.courses.CourseStates.get_by_value(state)
    #    if ending_reason: ending_reason = settings.SITE.models.courses.EndingReasons.get_by_value(ending_reason)
    #    if partner_tariff: partner_tariff = settings.SITE.models.courses.PartnerTariffs.get_by_value(partner_tariff)
    #    if translator_type: translator_type = settings.SITE.models.courses.TranslatorTypes.get_by_value(translator_type)
    #    if therapy_domain: therapy_domain = settings.SITE.models.courses.TherapyDomains.get_by_value(therapy_domain)
    kw = dict()
    kw.update(id=id)
    kw.update(modified=modified)
    kw.update(ref=ref)
    kw.update(start_date=start_date)
    kw.update(start_time=start_time)
    kw.update(end_date=end_date)
    kw.update(end_time=end_time)
    kw.update(healthcare_plan_id=healthcare_plan_id)
    kw.update(user_id=user_id)
    kw.update(every_unit=every_unit)
    kw.update(every=every)
    kw.update(monday=monday)
    kw.update(tuesday=tuesday)
    kw.update(wednesday=wednesday)
    kw.update(thursday=thursday)
    kw.update(friday=friday)
    kw.update(saturday=saturday)
    kw.update(sunday=sunday)
    kw.update(max_events=max_events)
    kw.update(room_id=room_id)
    kw.update(max_date=max_date)
    kw.update(line_id=line_id)
    kw.update(teacher_id=teacher_id)
    kw.update(slot_id=slot_id)
    if description is not None: kw.update(bv2kw('description', description))
    kw.update(remark=remark)
    kw.update(state=state)
    kw.update(max_places=max_places)
    kw.update(name=name)
    kw.update(enrolments_until=enrolments_until)
    kw.update(tariff_id=tariff_id)
    kw.update(payment_term_id=payment_term_id)
    kw.update(procurer_id=procurer_id)
    kw.update(mandatory=mandatory)
    kw.update(ending_reason=ending_reason)
    kw.update(partner_tariff=partner_tariff)
    kw.update(translator_type=translator_type)
    kw.update(therapy_domain=therapy_domain)
    kw.update(team_id=team_id)
    kw.update(partner_id=partner_id)
    kw.update(paper_type_id=paper_type_id)
    return courses_Course(**kw)


def create_cal_event(id, modified, created, project_id, start_date, start_time,
                     end_date, end_time, build_time, build_method,
                     owner_type_id, owner_id, user_id, assigned_to_id, summary,
                     description, access_class, sequence, auto_type, priority,
                     event_type_id, transparent, room_id, state, amount):
    #    if build_method: build_method = settings.SITE.models.printing.BuildMethods.get_by_value(build_method)
    owner_type_id = new_content_type_id(owner_type_id)
    #    if access_class: access_class = settings.SITE.models.cal.AccessClasses.get_by_value(access_class)
    #    if priority: priority = settings.SITE.models.xl.Priorities.get_by_value(priority)
    #    if state: state = settings.SITE.models.cal.EntryStates.get_by_value(state)
    if amount is not None: amount = Decimal(amount)
    kw = dict()
    kw.update(id=id)
    kw.update(modified=modified)
    kw.update(created=created)
    kw.update(project_id=project_id)
    kw.update(start_date=start_date)
    kw.update(start_time=start_time)
    kw.update(end_date=end_date)
    kw.update(end_time=end_time)
    kw.update(build_time=build_time)
    kw.update(build_method=build_method)
    kw.update(owner_type_id=owner_type_id)
    kw.update(owner_id=owner_id)
    kw.update(user_id=user_id)
    kw.update(assigned_to_id=assigned_to_id)
    kw.update(summary=summary)
    kw.update(description=description)
    kw.update(access_class=access_class)
    kw.update(sequence=sequence)
    kw.update(auto_type=auto_type)
    kw.update(priority=priority)
    kw.update(event_type_id=event_type_id)
    kw.update(transparent=transparent)
    kw.update(room_id=room_id)
    kw.update(state=state)
    kw.update(amount=amount)
    return cal_Event(**kw)


def create_cal_guest(id, event_id, partner_id, role_id, state, remark, amount):
    #    if state: state = settings.SITE.models.cal.GuestStates.get_by_value(state)
    if amount is not None: amount = Decimal(amount)
    kw = dict()
    kw.update(id=id)
    kw.update(event_id=event_id)
    kw.update(partner_id=partner_id)
    kw.update(role_id=role_id)
    kw.update(state=state)
    kw.update(remark=remark)
    kw.update(amount=amount)
    return cal_Guest(**kw)


def create_cal_task(id, modified, created, project_id, start_date, start_time,
                    owner_type_id, owner_id, user_id, summary, description,
                    access_class, sequence, auto_type, priority, due_date,
                    due_time, percent, state):
    owner_type_id = new_content_type_id(owner_type_id)
    #    if access_class: access_class = settings.SITE.models.cal.AccessClasses.get_by_value(access_class)
    #    if priority: priority = settings.SITE.models.xl.Priorities.get_by_value(priority)
    #    if state: state = settings.SITE.models.cal.TaskStates.get_by_value(state)
    kw = dict()
    kw.update(id=id)
    kw.update(modified=modified)
    kw.update(created=created)
    kw.update(project_id=project_id)
    kw.update(start_date=start_date)
    kw.update(start_time=start_time)
    kw.update(owner_type_id=owner_type_id)
    kw.update(owner_id=owner_id)
    kw.update(user_id=user_id)
    kw.update(summary=summary)
    kw.update(description=description)
    kw.update(access_class=access_class)
    kw.update(sequence=sequence)
    kw.update(auto_type=auto_type)
    kw.update(priority=priority)
    kw.update(due_date=due_date)
    kw.update(due_time=due_time)
    kw.update(percent=percent)
    kw.update(state=state)
    return cal_Task(**kw)


def create_dashboard_widget(id, seqno, user_id, item_name, visible):
    kw = dict()
    kw.update(id=id)
    kw.update(seqno=seqno)
    kw.update(user_id=user_id)
    kw.update(item_name=item_name)
    kw.update(visible=visible)
    return dashboard_Widget(**kw)


def create_excerpts_excerpt(id, project_id, build_time, build_method,
                            owner_type_id, owner_id, user_id, company_id,
                            contact_person_id, contact_role_id,
                            excerpt_type_id, language):
    #    if build_method: build_method = settings.SITE.models.printing.BuildMethods.get_by_value(build_method)
    owner_type_id = new_content_type_id(owner_type_id)
    kw = dict()
    kw.update(id=id)
    kw.update(project_id=project_id)
    kw.update(build_time=build_time)
    kw.update(build_method=build_method)
    kw.update(owner_type_id=owner_type_id)
    kw.update(owner_id=owner_id)
    kw.update(user_id=user_id)
    kw.update(company_id=company_id)
    kw.update(contact_person_id=contact_person_id)
    kw.update(contact_role_id=contact_role_id)
    kw.update(excerpt_type_id=excerpt_type_id)
    kw.update(language=language)
    return excerpts_Excerpt(**kw)


def create_courses_enrolment(id, start_date, end_date, printed_by_id, user_id,
                             course_area, course_id, pupil_id, request_date,
                             state, places, option_id, remark,
                             confirmation_details, tariff_id, guest_role_id):
    #    if course_area: course_area = settings.SITE.models.courses.ActivityLayouts.get_by_value(course_area)
    #    if state: state = settings.SITE.models.courses.EnrolmentStates.get_by_value(state)
    kw = dict()
    kw.update(id=id)
    kw.update(start_date=start_date)
    kw.update(end_date=end_date)
    kw.update(printed_by_id=printed_by_id)
    kw.update(user_id=user_id)
    kw.update(course_area=course_area)
    kw.update(course_id=course_id)
    kw.update(pupil_id=pupil_id)
    kw.update(request_date=request_date)
    kw.update(state=state)
    kw.update(places=places)
    kw.update(option_id=option_id)
    kw.update(remark=remark)
    kw.update(confirmation_details=confirmation_details)
    kw.update(tariff_id=tariff_id)
    kw.update(guest_role_id=guest_role_id)
    return courses_Enrolment(**kw)


def create_invoicing_plan(id, user_id, today, journal_id, max_date, partner_id,
                          course_id):
    kw = dict()
    kw.update(id=id)
    kw.update(user_id=user_id)
    kw.update(today=today)
    kw.update(journal_id=journal_id)
    kw.update(max_date=max_date)
    kw.update(partner_id=partner_id)
    kw.update(course_id=course_id)
    return invoicing_Plan(**kw)


def create_ledger_ledgerinfo(user_id, entry_date):
    kw = dict()
    kw.update(user_id=user_id)
    kw.update(entry_date=entry_date)
    return ledger_LedgerInfo(**kw)


def create_ledger_voucher(id, user_id, journal_id, entry_date, voucher_date,
                          accounting_period_id, number, narration, state):
    #    if state: state = settings.SITE.models.accounting.VoucherStates.get_by_value(state)
    kw = dict()
    kw.update(id=id)
    kw.update(user_id=user_id)
    kw.update(journal_id=journal_id)
    kw.update(entry_date=entry_date)
    kw.update(voucher_date=voucher_date)
    kw.update(accounting_period_id=accounting_period_id)
    kw.update(number=number)
    kw.update(narration=narration)
    kw.update(state=state)
    return ledger_Voucher(**kw)


def create_ana_anaaccountinvoice(voucher_ptr_id, partner_id, payment_term_id,
                                 match, your_ref, due_date, total_incl,
                                 total_base, total_vat, vat_regime,
                                 items_edited):
    if total_incl is not None: total_incl = Decimal(total_incl)
    if total_base is not None: total_base = Decimal(total_base)
    if total_vat is not None: total_vat = Decimal(total_vat)
    #    if vat_regime: vat_regime = settings.SITE.models.vat.VatRegimes.get_by_value(vat_regime)
    kw = dict()
    kw.update(partner_id=partner_id)
    kw.update(payment_term_id=payment_term_id)
    kw.update(match=match)
    kw.update(your_ref=your_ref)
    kw.update(due_date=due_date)
    kw.update(total_incl=total_incl)
    kw.update(total_base=total_base)
    kw.update(total_vat=total_vat)
    kw.update(vat_regime=vat_regime)
    kw.update(items_edited=items_edited)
    return create_mti_child(ledger_Voucher, voucher_ptr_id,
                            ana_AnaAccountInvoice, **kw)


def create_ana_invoiceitem(id, seqno, account_id, total_incl, total_base,
                           total_vat, vat_class, voucher_id, ana_account_id,
                           title):
    if total_incl is not None: total_incl = Decimal(total_incl)
    if total_base is not None: total_base = Decimal(total_base)
    if total_vat is not None: total_vat = Decimal(total_vat)
    #    if vat_class: vat_class = settings.SITE.models.vat.VatClasses.get_by_value(vat_class)
    kw = dict()
    kw.update(id=id)
    kw.update(seqno=seqno)
    kw.update(account_id=account_id)
    kw.update(total_incl=total_incl)
    kw.update(total_base=total_base)
    kw.update(total_vat=total_vat)
    kw.update(vat_class=vat_class)
    kw.update(voucher_id=voucher_id)
    kw.update(ana_account_id=ana_account_id)
    kw.update(title=title)
    return ana_InvoiceItem(**kw)


def create_bevats_declaration(voucher_ptr_id, printed_by_id, partner_id,
                              payment_term_id, start_period_id, end_period_id,
                              your_ref, due_date, F71, F72, F73, F75, F76, F77,
                              F78, F80, F81, F82, F83):
    if F71 is not None: F71 = Decimal(F71)
    if F72 is not None: F72 = Decimal(F72)
    if F73 is not None: F73 = Decimal(F73)
    if F75 is not None: F75 = Decimal(F75)
    if F76 is not None: F76 = Decimal(F76)
    if F77 is not None: F77 = Decimal(F77)
    if F78 is not None: F78 = Decimal(F78)
    if F80 is not None: F80 = Decimal(F80)
    if F81 is not None: F81 = Decimal(F81)
    if F82 is not None: F82 = Decimal(F82)
    if F83 is not None: F83 = Decimal(F83)
    kw = dict()
    kw.update(printed_by_id=printed_by_id)
    kw.update(partner_id=partner_id)
    kw.update(payment_term_id=payment_term_id)
    kw.update(start_period_id=start_period_id)
    kw.update(end_period_id=end_period_id)
    kw.update(your_ref=your_ref)
    kw.update(due_date=due_date)
    kw.update(F71=F71)
    kw.update(F72=F72)
    kw.update(F73=F73)
    kw.update(F75=F75)
    kw.update(F76=F76)
    kw.update(F77=F77)
    kw.update(F78=F78)
    kw.update(F80=F80)
    kw.update(F81=F81)
    kw.update(F82=F82)
    kw.update(F83=F83)
    return create_mti_child(ledger_Voucher, voucher_ptr_id, bevats_Declaration,
                            **kw)


def create_finan_bankstatement(voucher_ptr_id, printed_by_id, item_account_id,
                               item_remark, last_item_date, balance1,
                               balance2):
    if balance1 is not None: balance1 = Decimal(balance1)
    if balance2 is not None: balance2 = Decimal(balance2)
    kw = dict()
    kw.update(printed_by_id=printed_by_id)
    kw.update(item_account_id=item_account_id)
    kw.update(item_remark=item_remark)
    kw.update(last_item_date=last_item_date)
    kw.update(balance1=balance1)
    kw.update(balance2=balance2)
    return create_mti_child(ledger_Voucher, voucher_ptr_id,
                            finan_BankStatement, **kw)


def create_finan_bankstatementitem(id, seqno, match, amount, dc, remark,
                                   account_id, partner_id, date, voucher_id):
    if amount is not None: amount = Decimal(amount)
    kw = dict()
    kw.update(id=id)
    kw.update(seqno=seqno)
    kw.update(match=match)
    kw.update(amount=amount)
    kw.update(dc=dc)
    kw.update(remark=remark)
    kw.update(account_id=account_id)
    kw.update(partner_id=partner_id)
    kw.update(date=date)
    kw.update(voucher_id=voucher_id)
    return finan_BankStatementItem(**kw)


def create_finan_journalentry(voucher_ptr_id, printed_by_id, item_account_id,
                              item_remark, last_item_date):
    kw = dict()
    kw.update(printed_by_id=printed_by_id)
    kw.update(item_account_id=item_account_id)
    kw.update(item_remark=item_remark)
    kw.update(last_item_date=last_item_date)
    return create_mti_child(ledger_Voucher, voucher_ptr_id, finan_JournalEntry,
                            **kw)


def create_finan_journalentryitem(id, seqno, match, amount, dc, remark,
                                  account_id, partner_id, date, voucher_id):
    if amount is not None: amount = Decimal(amount)
    kw = dict()
    kw.update(id=id)
    kw.update(seqno=seqno)
    kw.update(match=match)
    kw.update(amount=amount)
    kw.update(dc=dc)
    kw.update(remark=remark)
    kw.update(account_id=account_id)
    kw.update(partner_id=partner_id)
    kw.update(date=date)
    kw.update(voucher_id=voucher_id)
    return finan_JournalEntryItem(**kw)


def create_finan_paymentorder(voucher_ptr_id, printed_by_id, item_account_id,
                              item_remark, total, execution_date):
    if total is not None: total = Decimal(total)
    kw = dict()
    kw.update(printed_by_id=printed_by_id)
    kw.update(item_account_id=item_account_id)
    kw.update(item_remark=item_remark)
    kw.update(total=total)
    kw.update(execution_date=execution_date)
    return create_mti_child(ledger_Voucher, voucher_ptr_id, finan_PaymentOrder,
                            **kw)


def create_finan_paymentorderitem(id, seqno, match, bank_account_id, amount,
                                  dc, remark, account_id, partner_id,
                                  voucher_id):
    if amount is not None: amount = Decimal(amount)
    kw = dict()
    kw.update(id=id)
    kw.update(seqno=seqno)
    kw.update(match=match)
    kw.update(bank_account_id=bank_account_id)
    kw.update(amount=amount)
    kw.update(dc=dc)
    kw.update(remark=remark)
    kw.update(account_id=account_id)
    kw.update(partner_id=partner_id)
    kw.update(voucher_id=voucher_id)
    return finan_PaymentOrderItem(**kw)


def create_ledger_movement(id, voucher_id, partner_id, seqno, account_id,
                           amount, dc, match, cleared, value_date, vat_regime,
                           vat_class, ana_account_id):
    if amount is not None: amount = Decimal(amount)
    #    if vat_regime: vat_regime = settings.SITE.models.vat.VatRegimes.get_by_value(vat_regime)
    #    if vat_class: vat_class = settings.SITE.models.vat.VatClasses.get_by_value(vat_class)
    kw = dict()
    kw.update(id=id)
    kw.update(voucher_id=voucher_id)
    kw.update(partner_id=partner_id)
    kw.update(seqno=seqno)
    kw.update(account_id=account_id)
    kw.update(amount=amount)
    kw.update(dc=dc)
    kw.update(match=match)
    kw.update(cleared=cleared)
    kw.update(value_date=value_date)
    kw.update(vat_regime=vat_regime)
    kw.update(vat_class=vat_class)
    kw.update(ana_account_id=ana_account_id)
    return ledger_Movement(**kw)


def create_notes_note(id, project_id, build_time, build_method, owner_type_id,
                      owner_id, user_id, company_id, contact_person_id,
                      contact_role_id, date, time, type_id, event_type_id,
                      subject, body, language):
    #    if build_method: build_method = settings.SITE.models.printing.BuildMethods.get_by_value(build_method)
    owner_type_id = new_content_type_id(owner_type_id)
    kw = dict()
    kw.update(id=id)
    kw.update(project_id=project_id)
    kw.update(build_time=build_time)
    kw.update(build_method=build_method)
    kw.update(owner_type_id=owner_type_id)
    kw.update(owner_id=owner_id)
    kw.update(user_id=user_id)
    kw.update(company_id=company_id)
    kw.update(contact_person_id=contact_person_id)
    kw.update(contact_role_id=contact_role_id)
    kw.update(date=date)
    kw.update(time=time)
    kw.update(type_id=type_id)
    kw.update(event_type_id=event_type_id)
    kw.update(subject=subject)
    kw.update(body=body)
    kw.update(language=language)
    return notes_Note(**kw)


def create_sales_vatproductinvoice(voucher_ptr_id, printed_by_id, partner_id,
                                   payment_term_id, match, your_ref, due_date,
                                   total_incl, total_base, total_vat,
                                   vat_regime, items_edited, language, subject,
                                   intro, paper_type_id):
    if total_incl is not None: total_incl = Decimal(total_incl)
    if total_base is not None: total_base = Decimal(total_base)
    if total_vat is not None: total_vat = Decimal(total_vat)
    #    if vat_regime: vat_regime = settings.SITE.models.vat.VatRegimes.get_by_value(vat_regime)
    kw = dict()
    kw.update(printed_by_id=printed_by_id)
    kw.update(partner_id=partner_id)
    kw.update(payment_term_id=payment_term_id)
    kw.update(match=match)
    kw.update(your_ref=your_ref)
    kw.update(due_date=due_date)
    kw.update(total_incl=total_incl)
    kw.update(total_base=total_base)
    kw.update(total_vat=total_vat)
    kw.update(vat_regime=vat_regime)
    kw.update(items_edited=items_edited)
    kw.update(language=language)
    kw.update(subject=subject)
    kw.update(intro=intro)
    kw.update(paper_type_id=paper_type_id)
    return create_mti_child(ledger_Voucher, voucher_ptr_id,
                            sales_VatProductInvoice, **kw)


def create_invoicing_item(id, plan_id, partner_id, generator_type_id,
                          generator_id, amount, preview, selected, invoice_id):
    generator_type_id = new_content_type_id(generator_type_id)
    if amount is not None: amount = Decimal(amount)
    kw = dict()
    kw.update(id=id)
    kw.update(plan_id=plan_id)
    kw.update(partner_id=partner_id)
    kw.update(generator_type_id=generator_type_id)
    kw.update(generator_id=generator_id)
    kw.update(amount=amount)
    kw.update(preview=preview)
    kw.update(selected=selected)
    kw.update(invoice_id=invoice_id)
    return invoicing_Item(**kw)


def create_sales_invoiceitem(id, seqno, total_incl, total_base, total_vat,
                             vat_class, unit_price, qty, product_id,
                             description, discount, voucher_id, title,
                             invoiceable_type_id, invoiceable_id):
    if total_incl is not None: total_incl = Decimal(total_incl)
    if total_base is not None: total_base = Decimal(total_base)
    if total_vat is not None: total_vat = Decimal(total_vat)
    #    if vat_class: vat_class = settings.SITE.models.vat.VatClasses.get_by_value(vat_class)
    if unit_price is not None: unit_price = Decimal(unit_price)
    if discount is not None: discount = Decimal(discount)
    invoiceable_type_id = new_content_type_id(invoiceable_type_id)
    kw = dict()
    kw.update(id=id)
    kw.update(seqno=seqno)
    kw.update(total_incl=total_incl)
    kw.update(total_base=total_base)
    kw.update(total_vat=total_vat)
    kw.update(vat_class=vat_class)
    kw.update(unit_price=unit_price)
    kw.update(qty=qty)
    kw.update(product_id=product_id)
    kw.update(description=description)
    kw.update(discount=discount)
    kw.update(voucher_id=voucher_id)
    kw.update(title=title)
    kw.update(invoiceable_type_id=invoiceable_type_id)
    kw.update(invoiceable_id=invoiceable_id)
    return sales_InvoiceItem(**kw)


def create_sheets_report(id, printed_by_id, user_id, today, start_period_id,
                         end_period_id):
    kw = dict()
    kw.update(id=id)
    kw.update(printed_by_id=printed_by_id)
    kw.update(user_id=user_id)
    kw.update(today=today)
    kw.update(start_period_id=start_period_id)
    kw.update(end_period_id=end_period_id)
    return sheets_Report(**kw)


def create_sheets_accountentry(id, report_id, old_d, old_c, during_d, during_c,
                               account_id):
    if old_d is not None: old_d = Decimal(old_d)
    if old_c is not None: old_c = Decimal(old_c)
    if during_d is not None: during_d = Decimal(during_d)
    if during_c is not None: during_c = Decimal(during_c)
    kw = dict()
    kw.update(id=id)
    kw.update(report_id=report_id)
    kw.update(old_d=old_d)
    kw.update(old_c=old_c)
    kw.update(during_d=during_d)
    kw.update(during_c=during_c)
    kw.update(account_id=account_id)
    return sheets_AccountEntry(**kw)


def create_sheets_anaaccountentry(id, report_id, old_d, old_c, during_d,
                                  during_c, ana_account_id):
    if old_d is not None: old_d = Decimal(old_d)
    if old_c is not None: old_c = Decimal(old_c)
    if during_d is not None: during_d = Decimal(during_d)
    if during_c is not None: during_c = Decimal(during_c)
    kw = dict()
    kw.update(id=id)
    kw.update(report_id=report_id)
    kw.update(old_d=old_d)
    kw.update(old_c=old_c)
    kw.update(during_d=during_d)
    kw.update(during_c=during_c)
    kw.update(ana_account_id=ana_account_id)
    return sheets_AnaAccountEntry(**kw)


def create_sheets_itementry(id, report_id, old_d, old_c, during_d, during_c,
                            item_id):
    if old_d is not None: old_d = Decimal(old_d)
    if old_c is not None: old_c = Decimal(old_c)
    if during_d is not None: during_d = Decimal(during_d)
    if during_c is not None: during_c = Decimal(during_c)
    kw = dict()
    kw.update(id=id)
    kw.update(report_id=report_id)
    kw.update(old_d=old_d)
    kw.update(old_c=old_c)
    kw.update(during_d=during_d)
    kw.update(during_c=during_c)
    kw.update(item_id=item_id)
    return sheets_ItemEntry(**kw)


def create_sheets_partnerentry(id, report_id, old_d, old_c, during_d, during_c,
                               partner_id, trade_type):
    if old_d is not None: old_d = Decimal(old_d)
    if old_c is not None: old_c = Decimal(old_c)
    if during_d is not None: during_d = Decimal(during_d)
    if during_c is not None: during_c = Decimal(during_c)
    #    if trade_type: trade_type = settings.SITE.models.accounting.TradeTypes.get_by_value(trade_type)
    kw = dict()
    kw.update(id=id)
    kw.update(report_id=report_id)
    kw.update(old_d=old_d)
    kw.update(old_c=old_c)
    kw.update(during_d=during_d)
    kw.update(during_c=during_c)
    kw.update(partner_id=partner_id)
    kw.update(trade_type=trade_type)
    return sheets_PartnerEntry(**kw)


def create_tera_client(person_ptr_id, modified, created, user_id, client_state,
                       private, professional_state, obsoletes_id,
                       nationality_id, life_mode_id, civil_state):
    #    if client_state: client_state = settings.SITE.models.clients.ClientStates.get_by_value(client_state)
    #    if professional_state: professional_state = settings.SITE.models.tera.ProfessionalStates.get_by_value(professional_state)
    #    if civil_state: civil_state = settings.SITE.models.contacts.CivilStates.get_by_value(civil_state)
    kw = dict()
    kw.update(modified=modified)
    kw.update(created=created)
    kw.update(user_id=user_id)
    kw.update(client_state=client_state)
    kw.update(private=private)
    kw.update(professional_state=professional_state)
    kw.update(obsoletes_id=obsoletes_id)
    kw.update(nationality_id=nationality_id)
    kw.update(life_mode_id=life_mode_id)
    kw.update(civil_state=civil_state)
    return create_mti_child(contacts_Person, person_ptr_id, tera_Client, **kw)


def create_tinymce_textfieldtemplate(id, user_id, name, description, text):
    kw = dict()
    kw.update(id=id)
    kw.update(user_id=user_id)
    kw.update(name=name)
    kw.update(description=description)
    kw.update(text=text)
    return tinymce_TextFieldTemplate(**kw)


def create_topics_interest(id, owner_type_id, owner_id, topic_id, remark,
                           partner_id):
    owner_type_id = new_content_type_id(owner_type_id)
    kw = dict()
    kw.update(id=id)
    kw.update(owner_type_id=owner_type_id)
    kw.update(owner_id=owner_id)
    kw.update(topic_id=topic_id)
    kw.update(remark=remark)
    kw.update(partner_id=partner_id)
    return topics_Interest(**kw)


def create_users_authority(id, user_id, authorized_id):
    kw = dict()
    kw.update(id=id)
    kw.update(user_id=user_id)
    kw.update(authorized_id=authorized_id)
    return users_Authority(**kw)


def create_vat_vataccountinvoice(voucher_ptr_id, partner_id, payment_term_id,
                                 match, your_ref, due_date, total_incl,
                                 total_base, total_vat, vat_regime,
                                 items_edited):
    if total_incl is not None: total_incl = Decimal(total_incl)
    if total_base is not None: total_base = Decimal(total_base)
    if total_vat is not None: total_vat = Decimal(total_vat)
    #    if vat_regime: vat_regime = settings.SITE.models.vat.VatRegimes.get_by_value(vat_regime)
    kw = dict()
    kw.update(partner_id=partner_id)
    kw.update(payment_term_id=payment_term_id)
    kw.update(match=match)
    kw.update(your_ref=your_ref)
    kw.update(due_date=due_date)
    kw.update(total_incl=total_incl)
    kw.update(total_base=total_base)
    kw.update(total_vat=total_vat)
    kw.update(vat_regime=vat_regime)
    kw.update(items_edited=items_edited)
    return create_mti_child(ledger_Voucher, voucher_ptr_id,
                            vat_VatAccountInvoice, **kw)


def create_vat_invoiceitem(id, seqno, account_id, total_incl, total_base,
                           total_vat, vat_class, voucher_id, title):
    if total_incl is not None: total_incl = Decimal(total_incl)
    if total_base is not None: total_base = Decimal(total_base)
    if total_vat is not None: total_vat = Decimal(total_vat)
    #    if vat_class: vat_class = settings.SITE.models.vat.VatClasses.get_by_value(vat_class)
    kw = dict()
    kw.update(id=id)
    kw.update(seqno=seqno)
    kw.update(account_id=account_id)
    kw.update(total_incl=total_incl)
    kw.update(total_base=total_base)
    kw.update(total_vat=total_vat)
    kw.update(vat_class=vat_class)
    kw.update(voucher_id=voucher_id)
    kw.update(title=title)
    return vat_InvoiceItem(**kw)


def main(args):
    loader = DpyLoader(globals(), quick=args.quick)
    from django.core.management import call_command
    call_command('initdb', interactive=args.interactive)
    os.chdir(os.path.dirname(__file__))
    loader.initialize()
    args = (globals(), locals())

    execfile("ana_account.py", *args)
    execfile("cal_calendar.py", *args)
    execfile("cal_dailyplannerrow.py", *args)
    execfile("cal_eventtype.py", *args)
    execfile("cal_eventpolicy.py", *args)
    execfile("cal_guestrole.py", *args)
    execfile("cal_remotecalendar.py", *args)
    execfile("clients_clientcontacttype.py", *args)
    execfile("contacts_companytype.py", *args)
    execfile("contacts_roletype.py", *args)
    execfile("countries_country.py", *args)
    execfile("countries_place.py", *args)
    execfile("courses_slot.py", *args)
    execfile("courses_topic.py", *args)
    execfile("excerpts_excerpttype.py", *args)
    execfile("gfks_helptext.py", *args)
    execfile("households_type.py", *args)
    execfile("invoicing_tariff.py", *args)
    execfile("ledger_fiscalyear.py", *args)
    execfile("ledger_accountingperiod.py", *args)
    execfile("ledger_paymentterm.py", *args)
    execfile("lists_listtype.py", *args)
    execfile("lists_list.py", *args)
    execfile("notes_eventtype.py", *args)
    execfile("notes_notetype.py", *args)
    execfile("products_productcat.py", *args)
    execfile("sales_papertype.py", *args)
    execfile("sheets_item.py", *args)
    execfile("ledger_account.py", *args)
    execfile("contacts_partner.py", *args)
    execfile("contacts_company.py", *args)
    execfile("contacts_person.py", *args)
    execfile("cal_room.py", *args)
    execfile("clients_clientcontact.py", *args)
    execfile("contacts_role.py", *args)
    execfile("healthcare_plan.py", *args)
    execfile("households_household.py", *args)
    execfile("households_member.py", *args)
    execfile("invoicing_salesrule.py", *args)
    execfile("lists_member.py", *args)
    execfile("products_product.py", *args)
    execfile("courses_line.py", *args)
    execfile("courses_pricerule.py", *args)
    execfile("healthcare_rule.py", *args)
    execfile("sepa_account.py", *args)
    execfile("ledger_journal.py", *args)
    execfile("ledger_matchrule.py", *args)
    execfile("system_siteconfig.py", *args)
    execfile("teams_team.py", *args)
    execfile("tera_lifemode.py", *args)
    execfile("tera_procurer.py", *args)
    execfile("topics_topic.py", *args)
    execfile("users_user.py", *args)
    execfile("cal_recurrentevent.py", *args)
    execfile("cal_subscription.py", *args)
    execfile("checkdata_problem.py", *args)
    execfile("courses_course.py", *args)
    execfile("cal_event.py", *args)
    execfile("cal_guest.py", *args)
    execfile("cal_task.py", *args)
    execfile("dashboard_widget.py", *args)
    execfile("excerpts_excerpt.py", *args)
    execfile("courses_enrolment.py", *args)
    execfile("invoicing_plan.py", *args)
    execfile("ledger_ledgerinfo.py", *args)
    execfile("ledger_voucher.py", *args)
    execfile("ana_anaaccountinvoice.py", *args)
    execfile("ana_invoiceitem.py", *args)
    execfile("bevats_declaration.py", *args)
    execfile("finan_bankstatement.py", *args)
    execfile("finan_bankstatementitem.py", *args)
    execfile("finan_journalentry.py", *args)
    execfile("finan_journalentryitem.py", *args)
    execfile("finan_paymentorder.py", *args)
    execfile("finan_paymentorderitem.py", *args)
    execfile("ledger_movement.py", *args)
    execfile("notes_note.py", *args)
    execfile("sales_vatproductinvoice.py", *args)
    execfile("invoicing_item.py", *args)
    execfile("sales_invoiceitem.py", *args)
    execfile("sheets_report.py", *args)
    execfile("sheets_accountentry.py", *args)
    execfile("sheets_anaaccountentry.py", *args)
    execfile("sheets_itementry.py", *args)
    execfile("sheets_partnerentry.py", *args)
    execfile("tera_client.py", *args)
    execfile("tinymce_textfieldtemplate.py", *args)
    execfile("topics_interest.py", *args)
    execfile("users_authority.py", *args)
    execfile("vat_vataccountinvoice.py", *args)
    execfile("vat_invoiceitem.py", *args)
    loader.finalize()
    logger.info("Loaded %d objects", loader.count_objects)
    call_command('resetsequences')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Restore the data.')
    parser.add_argument(
        '--noinput',
        dest='interactive',
        action='store_false',
        default=True,
        help="Don't ask for confirmation before flushing the database.")
    parser.add_argument('--quick',
                        dest='quick',
                        action='store_true',
                        default=False,
                        help='Do not call full_clean() on restored instances.')

    args = parser.parse_args()
    main(args)
