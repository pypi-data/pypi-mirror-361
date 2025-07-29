.. doctest docs/specs/voga/pupils.rst
.. _voga.specs.pupils:

==================================
Managing participants in Lino Voga
==================================

>>> from lino_book.projects.voga2.startup import *


Displaying all pupils who are either Member or Non-Member (using
gridfilter):


>>> from urllib.parse import quote
>>> url = '/api/courses/Pupils?'
>>> url += 'limit=10&start=0&fmt=json&'
>>> # url += "rp=ext-comp-1213&"
>>> # url += "pv=&pv=&pv=&pv=&pv=&pv=&pv=&"
>>> url += "filter=" + quote('[{"type":"string","value":"mem","field":"pupil_type"}]')
>>> test_client.force_login(rt.login('robin').user)
>>> res = test_client.get(url, REMOTE_USER='robin')
>>> print(res.status_code)
200

The response to this AJAX request is in JSON:

>>> d = json.loads(res.content.decode())
>>> d['count']
24



Filtering pupils
=================

Select pupils who participate in a given course:

>>> obj = rt.models.courses.Course.objects.get(pk=1)
>>> obj
Course #1 ('001 Greece 2014')
>>> pv = dict(course=obj)
>>> rt.show('courses.Pupils', param_values=pv)
========================== ================================= ================== ========= ===== ===== ======== ==============
 Name                       Address                           Participant type   Section   LFV   CKK   Raviva   Mitglied bis
-------------------------- --------------------------------- ------------------ --------- ----- ----- -------- --------------
 Annette Arens (MEL)        Alter Malmedyer Weg, 4700 Eupen   Helper                       Yes   No    No       31/12/2015
 Bernd Brecht (MEC)         Aachen, Germany                   Member                       No    Yes   No       31/12/2015
 Luc Faymonville (ME)       Brabantstraße, 4700 Eupen         Helper                       No    No    No       31/12/2016
 Guido Radermacher (MCLS)   4730 Raeren                       Helper             Hauset    Yes   Yes   No
========================== ================================= ================== ========= ===== ===== ======== ==============
<BLANKLINE>

Note that above table contains the same pupils but not the same
columns as :class:`EnrolmentsByCourse
<lino_voga.lib.courses.desktop.EnrolmentsByCourse>`:

>>> rt.show('courses.EnrolmentsByCourse', obj)
==================== ========================== ============ ============ ============= ======== ========== ============= ============== ===============
 Date of request      Participant                Start date   End date     Places used   Remark   Fee        Free events   Amount         Workflow
-------------------- -------------------------- ------------ ------------ ------------- -------- ---------- ------------- -------------- ---------------
 25/07/2014           Annette Arens (MEL)                                  1                      Journeys                 295,00         **Confirmed**
 25/07/2014           Bernd Brecht (MEC)                                   1                      Journeys                 295,00         **Confirmed**
 09/08/2014           Luc Faymonville (ME)                    18/09/2014   2                      Journeys                 590,00         **Confirmed**
 29/08/2014           Guido Radermacher (MCLS)   29/08/2014                1                      Journeys                 295,00         **Confirmed**
 **Total (4 rows)**                                                        **5**                             **0**         **1 475,00**
==================== ========================== ============ ============ ============= ======== ========== ============= ============== ===============
<BLANKLINE>


..
  >>> dbhash.check_virgin()
