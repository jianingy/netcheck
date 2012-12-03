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
                        (self.audit.detail['monitor_host'],
                         self.audit.detail['monitor_port']))


def do_tcp_check(audit):

    # sanity check
    if 'monitor_host' not in audit.detail:
        return

    if 'monitor_port' not in audit.detail:
        return

    reactor.connectTCP(audit.detail['monitor_host'],
                       audit.detail['monitor_port'],
                       TCPInspectionClientFactory(audit))
