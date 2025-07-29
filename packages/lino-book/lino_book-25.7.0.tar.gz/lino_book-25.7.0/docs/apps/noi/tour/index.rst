.. _noi1e.tour:

====================================
A tour of the Noi/ExtJS demo project
====================================






A series of screenshots taken from the
:mod:`lino_book.projects.noi1e` demo project.

.. include:: /../docs/shared/include/defs.rst




-----------------
Before signing in
-----------------







.. image:: login1_en.png
    :alt: Before signing in
    :width: 90.0%







----------------
The login window
----------------







.. image:: login2_en.png
    :alt: The login window
    :width: 90.0%







---------------
The main screen
---------------







.. image:: welcome_en.png
    :alt: The main screen
    :width: 90.0%







-----------------
The Contacts menu
-----------------







.. image:: menu_contacts_en.png
    :alt: The Contacts menu
    :width: 90.0%







-------------------------
The list of organizations
-------------------------







.. image:: contacts.Companies.grid_en.png
    :alt: The list of organizations
    :width: 90.0%







-----------------
Filter parameters
-----------------







.. image:: contacts.Companies.grid.params_en.png
    :alt: Filter parameters
    :width: 90.0%







--------------------------------
Detail window of an organization
--------------------------------







.. image:: contacts.Companies.detail_en.png
    :alt: Detail window of an organization
    :width: 90.0%







----------------------------------------
Detail window of an organization (tab 2)
----------------------------------------







.. image:: contacts.Companies.detail2_en.png
    :alt: Detail window of an organization (tab 2)
    :width: 90.0%







.. _noi1e.tour.oops:

------------
Not finished
------------



Oops, we had a problem when generating this document::

    Traceback (most recent call last):
      File "/home/blurry/lino/env/repositories/lino/lino/api/selenium.py", line 146, in find_clickable
        return self.driver.find_element(By.XPATH, '//button[text()="{}"]'.format(text))
      File "/home/blurry/lino/env/lib/python3.10/site-packages/selenium/webdriver/remote/webdriver.py", line 739, in find_element
        return self.execute(Command.FIND_ELEMENT, {"using": by, "value": value})["value"]
      File "/home/blurry/lino/env/lib/python3.10/site-packages/selenium/webdriver/remote/webdriver.py", line 345, in execute
        self.error_handler.check_response(response)
      File "/home/blurry/lino/env/lib/python3.10/site-packages/selenium/webdriver/remote/errorhandler.py", line 229, in check_response
        raise exception_class(message, screen, stacktrace)
    selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: {"method":"xpath","selector":"//button[text()="Sites"]"}
      (Session info: chrome=115.0.5790.170); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception
    Stacktrace:
    #0 0x557d6571abc3 <unknown>
    #1 0x557d6545a367 <unknown>
    #2 0x557d65497ef3 <unknown>
    #3 0x557d65497fe1 <unknown>
    #4 0x557d654d29b4 <unknown>
    #5 0x557d654b853d <unknown>
    #6 0x557d654d05ac <unknown>
    #7 0x557d654b82e3 <unknown>
    #8 0x557d6548c722 <unknown>
    #9 0x557d6548d4ce <unknown>
    #10 0x557d656df92d <unknown>
    #11 0x557d656e4183 <unknown>
    #12 0x557d656ed578 <unknown>
    #13 0x557d656e4bba <unknown>
    #14 0x557d656b624e <unknown>
    #15 0x557d65705698 <unknown>
    #16 0x557d6570583f <unknown>
    #17 0x557d65714148 <unknown>
    #18 0x7fb8a73afb43 <unknown>


    During handling of the above exception, another exception occurred:

    Traceback (most recent call last):
      File "/home/blurry/lino/env/repositories/lino/lino/api/selenium.py", line 260, in run_from_server
        self.main_func(self)
      File "maketour.py", line 112, in main
        tour(a, user)
      File "maketour.py", line 81, in tour
        app.find_clickable(_("Sites")).click()
      File "/home/blurry/lino/env/repositories/lino/lino/api/selenium.py", line 148, in find_clickable
        return self.driver.find_element(By.LINK_TEXT, text)
      File "/home/blurry/lino/env/lib/python3.10/site-packages/selenium/webdriver/remote/webdriver.py", line 739, in find_element
        return self.execute(Command.FIND_ELEMENT, {"using": by, "value": value})["value"]
      File "/home/blurry/lino/env/lib/python3.10/site-packages/selenium/webdriver/remote/webdriver.py", line 345, in execute
        self.error_handler.check_response(response)
      File "/home/blurry/lino/env/lib/python3.10/site-packages/selenium/webdriver/remote/errorhandler.py", line 229, in check_response
        raise exception_class(message, screen, stacktrace)
    selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: {"method":"link text","selector":"Sites"}
      (Session info: chrome=115.0.5790.170); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception
    Stacktrace:
    #0 0x557d6571abc3 <unknown>
    #1 0x557d6545a367 <unknown>
    #2 0x557d65497ef3 <unknown>
    #3 0x557d65497fe1 <unknown>
    #4 0x557d654d29b4 <unknown>
    #5 0x557d654b853d <unknown>
    #6 0x557d654d05ac <unknown>
    #7 0x557d654b82e3 <unknown>
    #8 0x557d6548c722 <unknown>
    #9 0x557d6548d4ce <unknown>
    #10 0x557d656df92d <unknown>
    #11 0x557d656e4183 <unknown>
    #12 0x557d656ed578 <unknown>
    #13 0x557d656e4bba <unknown>
    #14 0x557d656b624e <unknown>
    #15 0x557d65705698 <unknown>
    #16 0x557d6570583f <unknown>
    #17 0x557d65714148 <unknown>
    #18 0x7fb8a73afb43 <unknown>
