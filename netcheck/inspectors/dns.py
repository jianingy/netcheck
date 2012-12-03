#!/usr/bin/env python
# -*- coding: utf-8 -*-

# filename   : dns.py
# created at : 2012-12-03 11:48:55
# author     : Jianing Yang <jianingy.yang AT gmail DOT com>

__author__ = 'Jianing Yang <jianingy.yang AT gmail DOT com>'

from twisted.python.failure import Failure
from twisted.names import client
from twisted.names import dns
from twisted.python import log

RECORD_MAP = dict(A=dns.A, AAAA=dns.AAAA, PTR=dns.PTR,
                  CNAME=dns.CNAME, MX=dns.MX, TXT=dns.TXT)


def done_dns_check(value, audit, server):

    if isinstance(value, Failure):
        audit.fail("%s is unresolvable by server %s"
                   % (audit.detail['monitor_name'], server))
    else:
        result = list()
        for answer in value.answers:
            if answer.type != RECORD_MAP[audit.detail['monitor_type'].upper()]:
                continue
            result.append(answer.payload.dottedQuad())

        result = set(result)
        test = set(audit.detail['monitor_answer'])

        if test.issubset(result):
            audit.success()
        else:
            difference = test.difference(result)
            audit.fail("missing answer(s): %s from server %s"
                       % (",".join(list(difference)), server))


def do_dns_check(audit):

    # sanity check
    if 'monitor_servers' not in audit.detail:
        log.err('missing monitor_servers')
        return

    if not isinstance(audit.detail['monitor_servers'], list):
        log.err('monitor_servers should be a list')
        return

    if 'monitor_answer' not in audit.detail:
        log.err('missing monitor_answer')
        return

    if not isinstance(audit.detail['monitor_answer'], list):
        log.err('monitor_answer should be a list')
        return

    if 'monitor_type' not in audit.detail:
        log.err('missing monitor_type')
        return

    servers = None
    if 'monitor_servers' in audit.detail:
        servers = []
        for server in audit.detail['monitor_servers']:
            if server.find(':') > -1:
                host, port = server.split(':')
                servers.append((host, int(port)))
            else:
                servers.append((server, 53))

    for server in servers:
        timeout = int(audit.detail['monitor_interval'])
        resolver = client.Resolver(servers=[server])

        q = dns.Query(name=audit.detail['monitor_name'],
                      type=RECORD_MAP[audit.detail['monitor_type'].upper()])

        d = resolver.queryUDP([q], timeout=[timeout])
        d.addBoth(done_dns_check, audit, "%s:%s" % server)
