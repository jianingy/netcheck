#!/usr/bin/env python
# -*- coding: utf-8 -*-

# filename   : config.py
# created at : 2012-12-03 11:07:40
# author     : Jianing Yang <jianingy.yang AT gmail DOT com>

__author__ = 'Jianing Yang <jianingy.yang AT gmail DOT com>'

from twisted.python import log


class GlobalConfig(object):
    import re

    __instance__ = None

    uri_re       = re.compile(r'''
                                  (?P<type>\w+)://
                                  (?:(?P<user>\w+):(?P<password>[^@]+)@)?
                                  (?P<host>[^/]+)/
                                  (?P<path>.+)
                              ''', re.VERBOSE)

    def __new__(cls, *args, **kw):
        if not cls.__instance__:
            cls.__instance__ = super(GlobalConfig, cls).__new__(
                cls, *args, **kw)
        return cls.__instance__

    @staticmethod
    def load_config(uri):
        match = GlobalConfig.uri_re.match(uri)
        if not match:
            log.err('invalid uri: %s' % uri)
            sys.exit(0)

        if match.group('type') == 'file':
            from yaml import load as yaml_load
            fn = "%s/%s" % (match.group('host'), match.group('path'))
            return yaml_load(file(fn).read())
        else:
            log.err('unknown type: %s' % match.group('type'))
            sys.exit(0)

    @staticmethod
    def create_instance(yaml):
        from yaml import load as yaml_load
        instance = GlobalConfig()
        base = yaml_load(file(yaml).read())
        GlobalConfig.base = base
        GlobalConfig.mail = base['mail']
        GlobalConfig.inspector = instance.load_config(base['inspector'])
        GlobalConfig.informant = instance.load_config(base['informant'])
