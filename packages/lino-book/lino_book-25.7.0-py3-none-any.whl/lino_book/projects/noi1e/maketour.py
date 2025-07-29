# -*- coding: UTF-8 -*-
# Copyright 2015-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# Usage:
# $ go noi1e
# $ python manage.py run tours/make.py
# import time
from pathlib import Path
# from os.path import dirname
# import traceback
from django.conf import settings
from django.utils import translation
from lino.api import gettext as _  # not lazy
from lino.api import dd, rt

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from lino.api.selenium import Tour, runserver


def tour(app, user):
    driver = app.driver

    app.screenshot('login1', "Before signing in")

    # note that "Sign in" button is in English even when user.language is
    # something else because they haven't yet authenticated:
    app.find_clickable("Sign in").click()

    elem = driver.find_element(By.NAME, 'username')
    elem.send_keys(user.username)
    elem = driver.find_element(By.NAME, 'password')
    elem.send_keys(dd.plugins.users.demo_password)

    app.screenshot('login2', "The login window")

    elem.send_keys(Keys.RETURN)

    app.screenshot('welcome', "The main screen")

    app.find_clickable(_("Contacts")).click()

    app.screenshot('menu_contacts', "The Contacts menu")

    app.find_clickable(_("Organizations")).click()
    # elem = driver.find_element(By.LINK_TEXT, _("Organizations"))
    # elem.click()

    app.screenshot('contacts.Companies.grid', "The list of organizations")

    # this worked on 20210206 but after a firefox upgrade it caused
    # selenium.common.exceptions.ElementClickInterceptedException: Message: Element <button id="ext-gen103" class=" x-btn-text x-tbar-database_gear" type="button"> is not clickable at point (172,69) because another element <div id="ext-gen195" class="ext-el-mask"> obscures it
    # and other problems.

    wait = WebDriverWait(driver, 10)
    elem = wait.until(
        EC.element_to_be_clickable((By.CLASS_NAME, "x-tbar-database_gear")))

    # app.stabilize()
    # elem = driver.find_element(By.CLASS_NAME, "x-tbar-database_gear")
    elem.click()
    app.screenshot('contacts.Companies.grid.params', "Filter parameters")

    # time.sleep(2)

    # find the first row and doubleclick it:
    app.stabilize()
    found = False
    for elem in driver.find_elements(By.CLASS_NAME, 'x-grid3-row'):
        if app.is_stale(elem):
            print("stale:", elem)
        else:
            found = True
            app.doubleclick(elem)
            app.screenshot('contacts.Companies.detail',
                           "Detail window of an organization")
            app.find_clickable(_("Contact")).click()
            app.screenshot('contacts.Companies.detail2',
                           "Detail window of an organization (tab 2)")
            app.find_clickable(_("Sites")).click()
            app.screenshot('contacts.Companies.detail3',
                           "Detail window of an organization (tab 3)")
            break

    if not found:
        print("Mysterious: Did not find any row to doubleclick")

    # we can open the datail window programmatically using a permalink
    if False:  # TODO: stabilize fails when there is no dashboard
        obj = rt.models.contacts.Person.objects.first()
        ar = rt.login(user=user)
        ba = obj.get_detail_action(ar)
        url = ar.get_detail_url(ba.actor, obj.pk)
        driver.get(app.server_url + url)
        app.stabilize()
        app.screenshot('contacts.Person.detail', "Detail window of a person")

    # Log out before leaving so that the next user can enter

    app.find_clickable(str(user)).click()
    app.stabilize()
    app.find_clickable(_("Sign out")).click()


def main(a):
    """The function to call when the server is running."""
    for username in ("robin", "rolf"):
        user = rt.models.users.User.objects.get(username=username)
        a.set_language(user.language)
        with translation.override(user.language):
            tour(a, user)


if __name__ == '__main__':
    pth = Path(__file__).resolve().parents[3] / "docs/apps/noi/tour"
    print("Writing screenshots to {}...".format(pth))
    pth.mkdir(exist_ok=True)
    # pth.mkdir(exist_ok=True)
    Tour(main,
         output_path=pth,
         title="A tour of the Noi/ExtJS demo project",
         ref="noi1e.tour").make()
