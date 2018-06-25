#       http.py
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
from . import ProbeParseException, ProbeException
from dizzy.log import print_dizzy, VERBOSE_1, DEBUG

from http.client import HTTPConnection

class DizzyProbe(object):
    def __init__(self, section_proxy):
        self.dest = section_proxy.get('target_host')
        self.dport = section_proxy.getint('target_port', 80)
        self.src = section_proxy.get('source_host', '')
        if self.src == '':
            self.src = None
        self.method = section_proxy.get('method', 'GET')
        self.url = section_proxy.get('url')
        self.body = section_proxy.get('body', '')
        if self.body == '':
            self.body = None
        self.headers = {}
        headers = section_proxy.get('headers', '')
        if not headers == '':
            for l in headers.split("\n"):
                r = l.split(":")
                self.headers[r[0]] = ":".join(r[1:])
        self.timeout = section_proxy.getfloat('timeout', 1)
        self.retry = section_proxy.getint('retry', 3)
        self.is_open = False
        self.res = None

    def open(self):
        try:
            self.connection = HTTPConnection(self.dest, self.dport, timeout=self.timeout, source_address=self.src)
        except Exception as e:
            raise SessionException("probe/http: cant open session: %s" % e)
        else:
            self.is_open = True

    def close(self):
        if not self.is_open:
            return
        self.connection.close()
        self.res = None
        self.is_open = False

    def probe(self):
        if not self.is_open:
            print_dizzy("probe/http: not opened.", DEBUG)
            return False
        for attempt in range(1, self.retry + 1):
            print_dizzy("probe/http: probe attempt: %d" % attempt, VERBOSE_1)
            try:
                self.connection.request(self.method, self.url, body=self.body, headers=self.headers)
                self.res = self.connection.getresponse()
                self.connection.close()
            except Exception as e:
                print_dizzy("probe/http: probe error: '%s'" % type(e))
                print_dizzy(e, DEBUG)
            else:
                return True
        return False