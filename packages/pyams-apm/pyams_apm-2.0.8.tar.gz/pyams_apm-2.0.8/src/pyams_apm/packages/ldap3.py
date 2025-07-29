#
# Copyright (c) 2008-2017 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_apm.packages.ldap3 module

This module adds APM instrumentation to LDAP3 package
"""

from elasticapm.instrumentation.packages.base import AbstractInstrumentedModule
from elasticapm.traces import capture_span


__docformat__ = 'restructuredtext'


LDAP_DB_SPAN = 'db.ldap'


class LDAP3OpenInstrumentation(AbstractInstrumentedModule):
    """LDAP3 connection opening instrumentation"""

    name = "ldap.open"

    instrument_list = [
        ("ldap3.strategy.base", "BaseStrategy.open"),
        ("ldap3.strategy.reusable", "ReusableStrategy.open")
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        # pylint: disable=too-many-arguments
        """Wrapped method call"""
        with capture_span('LDAP.OPEN', LDAP_DB_SPAN, leaf=True):
            return wrapped(*args, **kwargs)


class LDAP3BindInstrumentation(AbstractInstrumentedModule):
    """LDAP3 bind instrumentation"""

    name = "ldap.bind"

    instrument_list = [("ldap3", "Connection.bind")]

    def call(self, module, method, wrapped, instance, args, kwargs):
        # pylint: disable=too-many-arguments
        """Wrapped method call"""
        with capture_span('LDAP.BIND', LDAP_DB_SPAN, leaf=True):
            return wrapped(*args, **kwargs)


class LDAP3SearchInstrumentation(AbstractInstrumentedModule):
    """LDAP3 search instrumentation"""

    name = "ldap.search"

    instrument_list = [("ldap3", "Connection.search")]

    def call(self, module, method, wrapped, instance, args, kwargs):
        # pylint: disable=too-many-arguments
        """Wrapped method call"""
        with capture_span('LDAP.SEARCH', LDAP_DB_SPAN, {
            'db': {
                'type': 'ldap',
                'statement': kwargs.get('search_filter') or args[1]
            }
        }, leaf=True):
            return wrapped(*args, **kwargs)


class LDAP3GetResponseInstrumentation(AbstractInstrumentedModule):
    """LDAP3 response getter instrumentation"""

    name = "ldap.get_response"

    instrument_list = [
        ("ldap3.strategy.base", "BaseStrategy.get_response"),
        ("ldap3.strategy.reusable", "ReusableStrategy.get_response")
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        # pylint: disable=too-many-arguments
        """Wrapped method call"""
        with capture_span('LDAP.GET_RESPONSE', LDAP_DB_SPAN, leaf=True):
            return wrapped(*args, **kwargs)
