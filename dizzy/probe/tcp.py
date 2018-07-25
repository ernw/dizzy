#       tcp.py
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
from dizzy.tools import check_root
from socket import inet_aton, inet_pton, AF_INET, AF_INET6, socket, SOCK_STREAM, SOL_SOCKET, SO_BROADCAST, \
    SO_REUSEADDR, SHUT_RDWR
from binascii import unhexlify


class DizzyProbe(object):
    def __init__(self, section_proxy):
        self.target_host = section_proxy.get('target_host')
        self.target_port = section_proxy.getint('target_port')
        self.source_host = section_proxy.get('source_host', None)
        self.source_port = section_proxy.getint('source_port', None)
        if not self.source_host is None and self.source_port <= 1024:
            check_root("use a source port <= 1024")
        self.timeout = section_proxy.getfloat('timeout', 1)
        self.retry = section_proxy.getint('retry', 2)
        self.is_open = False
        self.socket = None

        try:
            inet_aton(self.target_host)
            self.af = AF_INET
        except Exception as e:
            try:
                inet_pton(AF_INET6, self.target_host)
                self.af = AF_INET6
            except Exception as f:
                raise ProbeParseException("probe/tcp: unknown address family: %s: %s, %s" %
                                               (self.target_host, e, f))
        if not self.source_host is None:
            try:
                inet_aton(self.source_host)
            except Exception as e:
                try:
                    inet_pton(AF_INET6, self.source_host)
                except Exception as f:
                    raise ProbeParseException("probe/tcp: unknown address family: %s: %s, %s" %
                                                   (self.source_host, e, f))
                else:
                    if not self.af == AF_INET6:
                        raise ProbeParseException("probe/tcp: address family mismatch: %s - %s" %
                                                       (self.target_host, self.source_host))
            else:
                if not self.af == AF_INET:
                    raise ProbeParseException("probe/tcp: address family mismatch: %s - %s" %
                                                   (self.target_host, self.source_host))

    def open(self):
        self.is_open = True

    def probe(self):
        try:
            self.socket = socket(self.af, SOCK_STREAM)
            if self.target_host == "255.255.255.255":
                self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.socket.settimeout(self.timeout)
            if not self.source_host is None and not self.source_port is None:
                self.socket.bind((self.source_host, self.source_port))
        except Exception as e:
            if not self.socket is None:
                self.socket.close()
            print_dizzy("probe/tcp: open error: %s" % e)
            print_dizzy(e, DEBUG)

        for attempt in range(1, self.retry + 1):
            print_dizzy("probe/tcp: probe attempt: %d" % attempt, VERBOSE_1)
            try:
                self.socket.connect((self.target_host, self.target_port))
            except (ConnectionAbortedError, ConnectionRefusedError) as e:
                pass
            except Exception as e:
                print_dizzy("probe/tcp: probe error: '%s'" % type(e))
                print_dizzy(e, DEBUG)
            else:
                self.socket.close()
                return True
        return False

    def close(self):
        if not self.is_open:
            return
        self.is_open = False
