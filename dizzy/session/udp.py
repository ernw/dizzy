#       udp.py
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
from . import SessionException, SessionParseException
from socket import inet_aton, AF_INET, inet_pton, AF_INET6, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR, \
    SO_SNDBUF, socket, getaddrinfo, IPPROTO_UDP
from traceback import print_exc
from dizzy.log import print_dizzy, DEBUG

class DizzySession(object):
    def __init__(self, section_proxy):
        self.dest = section_proxy.get('target_host')
        self.dport = section_proxy.getint('target_port')
        self.src = section_proxy.get('source_host', '')
        self.sport = section_proxy.getint('source_port')
        self.timeout = section_proxy.getfloat('timeout', 1)
        self.recv_buffer = section_proxy.getfloat('recv_buffer', 4096)
        self.auto_reopen = section_proxy.getboolean('auto_reopen', True)
        self.server_side = section_proxy.getboolean('server', False)
        self.read_first = self.server_side
        self.read_first = section_proxy.getboolean('read_first', self.read_first)
        self.connect_retry = section_proxy.getint('retry', 3)
        self.interface = section_proxy.get('interface', "")
        self.is_open = False

        try:
            inet_aton(self.dest)
            self.af = AF_INET
        except Exception as e:
            try:
                inet_pton(AF_INET6, self.dest)
                self.af = AF_INET6
            except Exception as f:
                raise SessionParseException("unknown address family: %s: %s, %s" % (self.dest, e, f))
        if self.src != '':
            try:
                inet_aton(self.src)
            except Exception as e:
                try:
                    inet_pton(AF_INET6, self.src)
                except Exception as f:
                    raise SessionParseException("unknown address family: %s: %s, %s" % (self.src, e, f))
                else:
                    if not self.af == AF_INET6:
                        raise SessionParseException("address family missmatch: %s - %s" % (self.dest, self.src))
            else:
                if not self.af == AF_INET:
                    raise SessionParseException("address family missmatch: %s - %s" % (self.dest, self.src))

        self.cs = None
        self.maxsize = 65534

    def open(self):
        try:
            self.s = socket(self.af, SOCK_DGRAM)
            if self.dest == "255.255.255.255":
                self.s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            self.s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.s.settimeout(self.timeout)
            sendbuf = self.s.getsockopt(SOL_SOCKET, SO_SNDBUF)
            if sendbuf < self.maxsize:
                self.maxsize = sendbuf
            if not self.sport is None:
                if self.af == AF_INET:
                    self.s.bind((self.src, self.sport))
                elif self.af == AF_INET6:
                    try:
                        self.s.bind((self.src, self.port, 0, 0))
                    except:
                        if not self.interface is '':
                            (_, _, _, _, addri) = getaddrinfo("%s%%%s" % (self.src, self.interface), self.sport, family=AF_INET6, proto=IPPROTO_UDP)[0]
                            self.s.bind(addri)
                        else:
                            raise SessionException("cant bind to ipv6 LL without interface!")
        except Exception as e:
            raise SessionException("cant open session: %s" % e)
        else:
            self.is_open = True

    def close(self):
        if not self.is_open:
            return
        if not self.s is None:
            self.s.close()
            self.s = None
        if not self.cs is None:
            self.cs.close()
            self.cs = None
        self.is_open = False

    def send(self, data):
        try:
            self.s.sendto(data, (self.dest, self.dport))
        except Exception as e:
            if self.auto_reopen:
                print_dizzy("session/udp: session got closed '%s', autoreopening..." % e, DEBUG)
                self.close()
                self.open()
            else:
                self.close()
                raise SessionException("error on sending '%s', connection closed." % e)

    def recv(self):
        if self.server_side:
            return self.cs.recv(self.recv_buffer)
        else:
            return self.s.recv(self.recv_buffer)
