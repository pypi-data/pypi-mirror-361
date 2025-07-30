#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_apm.include module

This module is used for Pyramid integration
"""

import elasticapm
from elasticapm.instrumentation import register
from pyramid.events import subscriber
from pyramid.interfaces import IApplicationCreated


__docformat__ = 'restructuredtext'


@subscriber(IApplicationCreated)
def handle_apm_application(event):  # pylint: disable=unused-argument
    """Register custom instrumentations on application startup"""
    register.register('pyams_apm.packages.ldap3.LDAP3OpenInstrumentation')
    register.register('pyams_apm.packages.ldap3.LDAP3BindInstrumentation')
    register.register('pyams_apm.packages.ldap3.LDAP3SearchInstrumentation')
    register.register('pyams_apm.packages.ldap3.LDAP3GetResponseInstrumentation')
    register.register('pyams_apm.packages.chameleon.ChameleonCookingInstrumentation')
    register.register('pyams_apm.packages.chameleon.ChameleonRenderingInstrumentation')
    elasticapm.instrument()


def include_package(config):
    """Pyramid package include"""

    # add APM tween
    config.add_tween('pyams_apm.tween.elastic_apm_tween_factory')

    # scan package
    config.scan()
