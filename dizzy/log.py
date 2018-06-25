#       log.py
#
#       Copyright 2017 Daniel Mende <mail@c0decafe.de>
#

#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are
#       met:
#
#       * Redistributions of source code must retain the above copyright
#         notice, this list of conditions and the following disclaimer.
#       * Redistributions in binary form must reproduce the above
#         copyright notice, this list of conditions and the following disclaimer
#         in the documentation and/or other materials provided with the
#         distribution.
#       * Neither the name of the  nor the names of its
#         contributors may be used to endorse or promote products derived from
#         this software without specific prior written permission.
#
#       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#       "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#       LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#       A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#       OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#       SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#       LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#       DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#       THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#       OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from datetime import datetime
from traceback import print_tb
from threading import Lock
from sys import exc_info
from pprint import pprint

DEBUG = 5
VERBOSE_2 = 4
VERBOSE_1 = 3
NORMAL = 2
REDUCE = 1
NONE = 0

print_level = NORMAL

print_levels = {"DEBUG": DEBUG,
                "VERBOSE_2": VERBOSE_2,
                "VERBOSE_1": VERBOSE_1,
                "NORMAL": NORMAL,
                "REDUCE": REDUCE,
                "NONE": NONE}

print_colors = { DEBUG:      '\033[91m',
                VERBOSE_2:  '\033[94m',
                VERBOSE_1:  '\033[96m',
                NORMAL:     '\033[97m',
                REDUCE:     '\033[90m',
                NONE:       ''}
ENDC = '\033[0m'

print_lock = Lock()

def set_print_level(level):
    global print_level
    print_level = level

def print_dizzy(value, level=NORMAL):
    if print_level >= level:
        with print_lock:
            print(print_colors[level], end='')
            print(value)
            if isinstance(value, Exception):
                ex_type, ex, tb = exc_info()
                print_tb(tb)
            print(ENDC, end='')

def pprint_dizzy(value, level=NORMAL):
    if print_level >= level:
        with print_lock:
            print(print_colors[level], end='')
            pprint(value, width=1000, compact=True)
            print(ENDC, end='')

class Logger(object):
    def __init__(self, stream, logfile, buffered=False):
        self.stream = stream
        self.logfile = open(logfile, "a")
        self.buffered = buffered

    def write(self, data):
        self.stream.write(data)
        self.logfile.write(datetime.now().isoformat() + ": " + data + "\n")
        if not self.buffered:
            self.flush()

    def flush(self):
        self.stream.flush()
        self.logfile.flush()
