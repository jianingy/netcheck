#!/usr/bin/env python
# -*- coding: utf-8 -*-

# filename   : tcp.py
# created at : 2012-11-29 08:59:23
# author     : Jianing Yang <jianingy.yang AT gmail DOT com>

__author__ = 'Jianing Yang <jianingy.yang AT gmail DOT com>'

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor


class TCPInspectionProtocol(Protocol):

    def __init__(self, audit):
        self.audit = audit

    def connectionMade(self):
        self.audit.success()
        self.transport.loseConnection()


class TCPInspectionClientFactory(ClientFactory):

    def __init__(self, audit, *args, **kw):
        self.audit = audit

    def buildProtocol(self, addr):
        return TCPInspectionProtocol(self.audit)

    def clientConnectionFailed(self, connector, reason):
        self.audit.fail("%s:%s is unreachable" %
                        (self.audit.inspect_item['monitor_host'],
                         self.audit.inspect_item['monitor_port']))


def do_tcp_check(audit):

    # sanity check
    if 'monitor_host' not in audit.inspect_item:
        return

    if 'monitor_port' not in audit.inspect_item:
        return

    reactor.connectTCP(audit.inspect_item['monitor_host'],
                       audit.inspect_item['monitor_port'],
                       TCPInspectionClientFactory(audit))
