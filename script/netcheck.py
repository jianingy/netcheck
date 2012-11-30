#!/usr/bin/env python
# -*- coding: utf-8 -*-

# filename   : netcheck.py
# created at : 2012-11-29 09:07:12
# author     : Jianing Yang <jianingy.yang AT gmail DOT com>

__author__ = 'Jianing Yang <jianingy.yang AT gmail DOT com>'

from yaml import load as yaml_load
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.python import log, usage
from logging import DEBUG

from netinspect import do_tcp_check, do_http_check
from notifier import Notifier


class Audit(object):

    num_failure_trace = 10
    notifier = Notifier()

    def __init__(self, item):
        self.inspect_item = item
        self.inspector = self.__init_inspector()
        self.failure_count = [0]

    def success(self):
        self.reset_failure()
        #log.msg("SUCCESS: %s" % self.inspect_item)

    def fail(self, reason=""):
        self.increase_failure()
        count = self.count_failure()
        if count > 0 and 'notifier' in self.inspect_item:
            Notifier.notify(self.inspect_item['notifier'], count, reason)
        log.msg("FAIL: %s (%s)" % (self.inspect_item, self.failure_count))

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

        if 'monitor_interval' not in self.inspect_item:
            log.err('missing monitor_interval: %s' % self.inspect_item)
            return False

        log.msg("Starting inspector on %s" % self.inspect_item, level=DEBUG)
        interval = int(self.inspect_item['monitor_interval'])
        self.inspector.start(interval)

    def __init_inspector(self):

        if self.inspect_item['type'] == 'http':
            return LoopingCall(do_http_check, audit=self)
        elif self.inspect_item['type'] == 'tcp':
            return LoopingCall(do_tcp_check, self)
        else:
            log.err('invalid inspection type: %s' % self.inspect_item)
            return False


class Options(usage.Options):

    optParameters = [
        ["inspect", "i", "conf/netcheck.yaml", "Inspection configuration"],
        ["notify", "n", "conf/notify.yaml", "Notification configuration"],
        #["max-process", "m", "1", "Number of processes"],
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

    inspect_items = yaml_load(file(options['inspect']).read())
    Notifier.create_instance(yaml_load(file(options['notify']).read()))
    rule = Notifier()
    print rule.__rule__

    """
    import math
    num_process = int(options['max-process'])
    chunk_size = int(math.ceil(float(len(inspect_items)) / float(num_process)))
    for items in chunk(inspect_items, chunk_size):
        pass
    """
    log.startLogging(sys.stdout)
    map(lambda x: Audit(x).start(), inspect_items)
    reactor.run()
