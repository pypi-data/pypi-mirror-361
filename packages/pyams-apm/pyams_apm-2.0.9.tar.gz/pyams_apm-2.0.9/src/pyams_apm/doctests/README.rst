=================
PyAMS_apm package
=================

Introduction
------------

This package is composed of a set of utility functions, usable into any Pyramid application.

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)
    >>> config.registry.settings['elasticapm.service_version'] = 'pyams_apm'

    >>> from pyams_apm.include import include_package as include_apm
    >>> include_apm(config)

    >>> from pyramid.events import ApplicationCreated
    >>> from pyams_apm.include import handle_apm_application

    >>> event = ApplicationCreated(None)
    >>> handle_apm_application(event)

    >>> from pyramid.response import Response
    >>> def handler(request):
    ...     response = Response()
    ...     response.status_code = 200
    ...     return response

    >>> from pyams_apm.tween import elastic_apm_tween_factory
    >>> factory = elastic_apm_tween_factory(handler, config.registry)

Let's start a first request:

    >>> request = DummyRequest('http://localhost',
    ...                        scheme='http',
    ...                        matched_route=None,
    ...                        remote_addr='localhost')
    >>> response = factory(request)

We can try another request:

    >>> request = DummyRequest('http://localhost',
    ...                        scheme='http',
    ...                        matched_route=None,
    ...                        view_name='index.html',
    ...                        remote_addr='localhost')
    >>> response = factory(request)

Exceptions should be trapped and re-raised:

    >>> from pyramid.exceptions import HTTPNotFound
    >>> def error_handler(request):
    ...     raise HTTPNotFound()
    >>> factory = elastic_apm_tween_factory(error_handler, config.registry)
    >>> request = DummyRequest('http://localhost',
    ...                        scheme='http',
    ...                        matched_route=None,
    ...                        remote_addr='localhost')
    >>> response = factory(request)
    Traceback (most recent call last):
    ...
    pyramid.httpexceptions.HTTPNotFound: The resource could not be found.


Tests cleanup:

    >>> tearDown()
