#!/usr/bin/env python
# -*- coding: utf-8 -*-

# filename   : http.py
# created at : 2012-11-29 09:11:46
# author     : Jianing Yang <jianingy.yang AT gmail DOT com>

__author__ = 'Jianing Yang <jianingy.yang AT gmail DOT com>'

from twisted.web.client import getPage as http_request
from twisted.python.failure import Failure


def done_http_check(value, audit):

    if isinstance(value, Failure):
        audit.fail("%s is unreachable" % audit.detail['monitor_url'])
    else:
        audit.success()


def do_http_check(audit):
    if 'monitor_url' not in audit.detail:
        return
    d = http_request(audit.detail['monitor_url'])
    d.addBoth(done_http_check, audit)
