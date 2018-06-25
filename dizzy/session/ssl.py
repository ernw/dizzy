#       ssl.py
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
from socket import inet_aton, AF_INET, inet_pton, AF_INET6, SOCK_STREAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR, \
    SO_SNDBUF, timeout, socket
from traceback import print_exc
from ssl import SSLSocket, SSLError
from select import select
from dizzy.config import CONFIG
from dizzy.log import print_dizzy, DEBUG

class DizzySession(object):
    def __init__(self, section_proxy):
        self.dest = section_proxy.get('target_host')
        self.dport = section_proxy.getint('target_port')
        self.src = section_proxy.get('source_host', '')
        self.sport = section_proxy.getint('source_port')
        self.client_cert = section_proxy.get('certfile')
        self.client_key = section_proxy.get('keyfile')
        self.timeout = section_proxy.getfloat('timeout', 1)
        self.recv_buffer = section_proxy.getfloat('recv_buffer', 4096)
        self.auto_reopen = section_proxy.getboolean('auto_reopen', True)
        self.server_side = section_proxy.getboolean('server', False)
        self.read_first = self.server_side
        self.read_first = section_proxy.getboolean('read_first', self.read_first)
        self.connect_retry = section_proxy.getint('retry', 3)
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
            self.s = socket(self.af, SOCK_STREAM)
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
            self.s = SSLSocket(self.s, self.client_key, self.client_cert, ssl_version=3)
            if self.server_side:
                self.s.listen(1)
                (self.cs, (rip, rport)) = self.s.accept()
                if self.dport:
                    while self.dport != rport or self.src != rip:
                        if self.dport != rport:
                            print_dizzy("session/ssl: remote port %i not destination port %i" % (rport, self.dport), DEBUG)
                        if self.src != rip:
                            print_dizzy("session/ssl: remote ip %s not destination ip %i" % (rip, self.dst), DEBUG)
                        (self.cs, (sip, rport)) = self.s.accept()
                self.cs.settimeout(self.timeout)
            else:
                connected = False
                attempt = 1
                try:
                    self.s.connect((self.dest, self.dport))
                    connected = True
                except (timeout, SSLError):
                    print_dizzy("session/ssl: Connection attempt %d timed out." % attempt)
                    while not connected and attempt <= self.connect_retry:
                        try:
                            (r, w, x) = select([], [self.s], [], self.timeout)
                            if self.s in w:
                                connected = True
                        except:
                            pass
                        attempt += 1
                    if not connected:
                        raise SessionException("too much connection attempts")
        except Exception as e:
            raise SessionException("cant open session: %s" % str(e))
        else:
            self.is_open = True

    def close(self):
        self.s.close()
        self.s = None
        if self.cs:
            self.cs.close()
            self.cs = None
        self.is_open = False

    def send(self, data):
        try:
            if not self.maxsize is None and len(data) > self.maxsize:
                data = data[:self.maxsize - 1]
                print_dizzy("Truncated data to %d byte." % self.maxsize, DEBUG)
            if self.server_side:
                if not self.cs:
                    raise SessionException("no client connection, cant send")
                self.cs.send(data)
            else:
                self.s.send(data)
        except Exception as e:
            if self.auto_reopen:
                print_dizzy("session got closed '%s', autoreopening..." % e, DEBUG)
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
