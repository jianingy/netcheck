#!/usr/bin/env python
# -*- coding: utf-8 -*-

# filename   : __init__.py<2>
# created at : 2012-11-29 15:54:50
# author     : Jianing Yang <jianingy.yang AT gmail DOT com>

__author__ = 'Jianing Yang <jianingy.yang AT gmail DOT com>'

from twisted.python.failure import Failure
from twisted.python import log

from config import GlobalConfig


def sendmail(to_addr, title, reason):
    from twisted.mail.smtp import sendmail as do_sendmail
    from email.mime.text import MIMEText

    host = GlobalConfig.mail['host']
    #port = GlobalConfig.mail['port']
    from_addr = GlobalConfig.mail['from']

    msg = MIMEText(reason)
    msg['Subject'] = title
    msg['From'] = from_addr
    msg['To'] = to_addr

    log.msg("sending mail to %s" % to_addr)
    d = do_sendmail(host, from_addr, to_addr, msg.as_string())
    d.addBoth(done_sendmail)


def done_sendmail(value):
    if isinstance(value, Failure):
        log.err("failed to send mail: %s" % value)
    else:
        log.msg("mail sent: %s" % str(value))


class Informant(object):

    __instance__ = None
    __rule__ = dict()

    def __new__(cls, *args, **kw):
        if not cls.__instance__:
            cls.__instance__ = super(Informant, cls).__new__(
                cls, *args, **kw)
        return cls.__instance__

    @staticmethod
    def create_instance(rules):
        instance = Informant()
        for name, value in rules.items():
            value.sort(cmp=lambda x, y:
                       y['failure_count'] - x['failure_count'])
            instance.__rule__[name] = value

    @staticmethod
    def select_rule(name, failure_count):

        if name not in Informant.__rule__:
            log.err('rule %s does not exist' % name)
            return

        selected = None
        for rule in Informant.__rule__[name]:
            if 'failure_count' not in rule:
                log.err('missing failure_count in rule %s' % name)
                continue

            selected = rule

            if int(rule['failure_count']) < failure_count:
                return selected

        return None

    @staticmethod
    def inform(name, failure_count, title, reason):

        rule = Informant.select_rule(name, failure_count)
        if not rule: return

        if 'mail' in rule:
                sendmail(rule['mail'], title, reason)
