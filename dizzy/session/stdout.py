#       stdout.py
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
from . import SessionException
from sys import stdout, stdin
from traceback import print_exc
from dizzy.log import print_dizzy, DEBUG
from dizzy.config import CONFIG

class DizzySession(object):
    def __init__(self, section_proxy):
        self.auto_reopen = section_proxy.getboolean('auto_reopen', True)
        self.read_first = section_proxy.getboolean('read_first', False)
        self.send_lf = section_proxy.getboolean('send_lf', True)
        self.is_open = False

    def open(self):
        try:
            self.f = stdout.buffer
        except Exception as e:
            raise SessionException("cant open session: %s" % e)
        else:
            self.is_open = True

    def close(self):
        self.is_open = False

    def send(self, data):
        try:
            self.f.write(data)
            if self.send_lf:
                self.f.write(b"\n")
            self.f.flush()
        except Exception as e:
            if self.auto_reopen:
                print_dizzy("session/stdout: session got closed '%s', autoreopening..." % e, DEBUG)
                self.close()
                self.open()
            else:
                self.close()
                raise SessionException("error on sending '%s', connection closed." % e)

    def recv(self):
        line = bytes(stdin.readline(), CONFIG["GLOBALS"]["CODEC"])
        if line == b".\n":
            return None
        else:
            return line
