#!/usr/bin/env python
# -*- coding: utf-8 -*-

# filename   : netcheck.py
# created at : 2012-11-29 09:07:12
# author     : Jianing Yang <jianingy.yang AT gmail DOT com>

__author__ = 'Jianing Yang <jianingy.yang AT gmail DOT com>'

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.python import log, usage
from logging import DEBUG

from netcheck import GlobalConfig, Informant
from netcheck.inspectors import do_tcp_check, do_http_check
import re


class Audit(object):

    num_failure_trace = 10
    informant = Informant()
    repl_re = re.compile('%(\w+)%')

    def __init__(self, detail):
        self.detail = detail
        self.inspector = self.__init_inspector()
        self.failure_count = [0]
        self.vars = dict(detail)

    def replace_variable(self, s):

        def _replace(x):
            if x.group(1) in self.vars:
                return str(self.vars[x.group(1)])
            else:
                return x.group(0)

        return self.repl_re.sub(_replace, s)

    def success(self):
        self.reset_failure()

    def fail(self, reason=""):
        self.increase_failure()
        count = self.count_failure()

        self.vars['count'] = count

        if 'title' in self.detail:
            title = self.detail['title']
        else:
            title = reason

        title = self.replace_variable(title)

        if count > 0 and 'informant' in self.detail:

            Informant.inform(self.detail['informant'], count, title, reason)

        log.msg("FAIL: %s (%s)" % (title, reason))

    def count_failure(self):
        return self.failure_count[-1]

    def increase_failure(self):
        self.failure_count.append(self.count_failure() + 1)
        self.failure_count = self.failure_count[-self.num_failure_trace:]

    def reset_failure(self):
        self.failure_count.append(0)
        self.failure_count = self.failure_count[-self.num_failure_trace:]

    def start(self):
        # sanity check

        if 'monitor_interval' not in self.detail:
            log.err('missing monitor_interval: %s' % self.detail)
            return False

        log.msg("Starting inspector on %s" % self.detail, level=DEBUG)
        interval = int(self.detail['monitor_interval'])
        self.inspector.start(interval)

    def __init_inspector(self):

        if self.detail['type'] == 'http':
            return LoopingCall(do_http_check, audit=self)
        elif self.detail['type'] == 'tcp':
            return LoopingCall(do_tcp_check, self)
        else:
            log.err('invalid inspection type: %s' % self.detail)
            return False


class Options(usage.Options):

    optParameters = [
        ["config", "c", "conf/netcheck.yaml", "Configuration"],
    ]


def chunk(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

if __name__ == '__main__':
    import sys

    options = Options()

    try:
        options.parseOptions(sys.argv[1:])
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)

    config = GlobalConfig.create_instance(options['config'])
    Informant.create_instance(GlobalConfig.informant)

    log.startLogging(sys.stdout)
    map(lambda x: Audit(x).start(), GlobalConfig.inspector)

    reactor.run()
