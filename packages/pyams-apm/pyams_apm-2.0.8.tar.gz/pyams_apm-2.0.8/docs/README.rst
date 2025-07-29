=================
PyAMS_apm package
=================

.. contents::


What is PyAMS?
==============

PyAMS (Pyramid Application Management Suite) is a small suite of packages written for applications
and content management with the Pyramid framework.

**PyAMS** is actually mainly used to manage web sites through content management applications (CMS,
see PyAMS_content package), but many features are generic and can be used inside any kind of web
application.

All PyAMS documentation is available on `ReadTheDocs <https://pyams.readthedocs.io>`_; official
source code is available on `Gitlab <https://gitlab.com/pyams>`_ and pushed to `Github
<https://github.com/py-ams>`_.


What is Elastic-APM?
====================

APM (Application Performances Monitoring - https://elastic.co/products/apm) is an extension for
Elasticsearch which provides application monitoring features: APM agents, deployed on an
application, allows to create Kibana dashboards displaying many applications performances elements,
like the CPU load, the duration of HTTP requests and many other informations.


What is PyAMS_apm?
==================

PyAMS_APM is an extension to Pyramid which allows to send APM data to an APM server to record
application activity. It's not dedicated to PyAMS applications, and can be used to monitor any
Pyramid application.

Compared to default Elastic-APM package implementation, PyAMS_APM also add monitoring of additional
libraries, like LDAP3 or Chameleon.
