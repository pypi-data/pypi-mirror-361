#
# Copyright (c) 2008-2018 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_apm.tween module

This module provides a custom tween which is used to integrate the Pyramid application
with APM, sending requests frames to the APM server.
"""

import sys
try:
    from importlib.metadata import PackageNotFoundError, distribution
except ImportError:
    from importlib_metadata import PackageNotFoundError, distribution
    
import elasticapm
from elasticapm.utils import get_url_dict
from pyramid.settings import asbool
from pyramid.util import reraise

__docformat__ = 'restructuredtext'


def list_from_setting(config, setting):
    """Split configuration setting"""
    value = config.get(setting)
    if not value:
        return None
    return value.split()


def get_data_from_request(request):
    """Extract main APM data from request properties"""
    data = {
        "headers": dict(**request.headers),
        "method": request.method,
        "socket": {
            "remote_address": request.remote_addr,
            "encrypted": request.scheme == 'https'
        },
        "cookies": dict(**request.cookies),
        "url": get_url_dict(request.url)
    }
    # remove Cookie header since the same data is in request["cookies"] as well
    data["headers"].pop("Cookie", None)
    return data


def get_data_from_response(response):
    """Extract APM data from response properties"""
    data = {"status_code": response.status_int}
    if response.headers:
        data["headers"] = {
            key: ";".join(response.headers.getall(key))
            for key in response.headers.keys()
        }
    return data


class elastic_apm_tween_factory:  # pylint: disable=invalid-name
    """Elasticsearch APM tween factory"""

    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry
        config = registry.settings
        service_version = config.get("elasticapm.service_version")
        if service_version:
            try:
                service_version = distribution(service_version).version
            except PackageNotFoundError:
                pass
        self.client = elasticapm.Client(
            server_url=config.get("elasticapm.server_url"),
            server_cert=config.get('elasticapm.server_cert'),
            verify_server_cert=asbool(config.get('elasticapm.verify_server_cert')),
            server_ca_cert_file=config.get('elasticapm.server_ca_cert_file'),
            server_timeout=config.get("elasticapm.server_timeout"),
            name=config.get("elasticapm.name"),
            framework_name="Pyramid",
            framework_version=distribution("pyramid").version,
            service_name=config.get("elasticapm.service_name"),
            service_version=service_version,
            secret_token=config.get("elasticapm.secret_token"),
            api_key=config.get('elasticapm.api_key'),
            environment=config.get("elasticapm.environment"),
            include_paths=list_from_setting(config, "elasticapm.include_paths"),
            exclude_paths=list_from_setting(config, "elasticapm.exclude_paths"),
            debug=asbool(config.get('elasticapm.debug'))
        )

    def __call__(self, request):
        self.client.begin_transaction('request')
        try:
            response = self.handler(request)
            transaction_result = response.status[0] + "xx"
            elasticapm.set_context(lambda: get_data_from_response(response), "response")
            return response
        except Exception:  # pylint: disable=broad-except
            transaction_result = '5xx'
            self.client.capture_exception(
                context={
                    "request": get_data_from_request(request)
                },
                handled=False,  # indicate that this exception bubbled all the way up to the user
            )
            reraise(*sys.exc_info())
        finally:
            try:
                view_name = request.view_name
                if not view_name:
                    view_name = request.traversed[-1] if request.traversed else '/'
            except AttributeError:
                view_name = ''
            transaction_name = request.matched_route.pattern if request.matched_route else view_name
            # prepend request method
            transaction_name = " ".join((request.method, transaction_name)) \
                if transaction_name else ""
            elasticapm.set_context(lambda: get_data_from_request(request), "request")
            self.client.end_transaction(transaction_name, transaction_result)
