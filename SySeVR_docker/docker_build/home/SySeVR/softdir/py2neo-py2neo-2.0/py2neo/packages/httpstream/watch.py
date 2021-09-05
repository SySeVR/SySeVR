#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011-2014, Nigel Small
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import unicode_literals

import logging
import sys
import threading


__all__ = ["Watcher", "watch"]


def black(s):
    return "\x1b[30m{}\x1b[0m".format(s)


def red(s):
    return "\x1b[31m{}\x1b[0m".format(s)


def green(s):
    return "\x1b[32m{}\x1b[0m".format(s)


def yellow(s):
    return "\x1b[33m{}\x1b[0m".format(s)


def blue(s):
    return "\x1b[34m{}\x1b[0m".format(s)


def magenta(s):
    return "\x1b[35m{}\x1b[0m".format(s)


def cyan(s):
    return "\x1b[36m{}\x1b[0m".format(s)


def white(s):
    return "\x1b[36m{}\x1b[0m".format(s)


def bright_black(s):
    return "\x1b[30;1m{}\x1b[0m".format(s)


def bright_red(s):
    return "\x1b[31;1m{}\x1b[0m".format(s)


def bright_green(s):
    return "\x1b[32;1m{}\x1b[0m".format(s)


def bright_yellow(s):
    return "\x1b[33;1m{}\x1b[0m".format(s)


def bright_blue(s):
    return "\x1b[34;1m{}\x1b[0m".format(s)


def bright_magenta(s):
    return "\x1b[35;1m{}\x1b[0m".format(s)


def bright_cyan(s):
    return "\x1b[36;1m{}\x1b[0m".format(s)


def bright_white(s):
    return "\x1b[37;1m{}\x1b[0m".format(s)


class ColourFormatter(logging.Formatter):

    def format(self, record):
        s = super(ColourFormatter, self).format(record)
        if record.levelno == logging.CRITICAL:
            return bright_red(s)
        elif record.levelno == logging.ERROR:
            return bright_yellow(s)
        elif record.levelno == logging.WARNING:
            return yellow(s)
        elif record.levelno == logging.INFO:
            return cyan(s)
        elif record.levelno == logging.DEBUG:
            return blue(s)
        else:
            return s


class Watcher(threading.local):

    handlers = {}

    def __init__(self, logger_name):
        super(Watcher, self).__init__()
        self.logger_name = logger_name
        self.logger = logging.getLogger(self.logger_name)
        self.formatter = ColourFormatter()

    def watch(self, level=None, out=sys.stdout):
        try:
            self.logger.removeHandler(self.handlers[self.logger_name])
        except KeyError:
            pass
        handler = logging.StreamHandler(out)
        handler.setFormatter(self.formatter)
        self.handlers[self.logger_name] = handler
        self.logger.addHandler(handler)
        if level is None:
            level = logging.DEBUG if __debug__ else logging.INFO
        self.logger.setLevel(level)


def watch(logger_name, level=logging.INFO, out=sys.stdout):
    watcher = Watcher(logger_name)
    watcher.watch(level, out)
