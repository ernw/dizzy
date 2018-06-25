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
#       THEORY OF LIABILITY, frWHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#       OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from . import SessionException, SessionParseException
from socket import inet_aton, inet_pton, AF_INET, AF_INET6, socket, SOCK_STREAM, SOL_SOCKET, SO_BROADCAST, \
    SO_REUSEADDR, SO_SNDBUF, timeout, IPPROTO_TCP
from select import select
from traceback import print_exc
from dizzy.log import print_dizzy, DEBUG

class DizzySession(object):
    def __init__(self, section_proxy):
        self.dest = section_proxy.get('target_host')
        self.dport = section_proxy.getint('target_port')
        self.src = section_proxy.get('source_host', '')
        self.sport = section_proxy.getint('source_port')
        self.interface = section_proxy.get('interface', '')
        self.timeout = section_proxy.getfloat('timeout', 1)
        self.recv_buffer = section_proxy.getfloat('recv_buffer', 4096)
        self.auto_reopen = section_proxy.getboolean('auto_reopen', True)
        self.server_side = section_proxy.getboolean('server', False)
        self.read_first = self.server_side
        self.read_first = section_proxy.getboolean('read_first', self.read_first)
        self.connect_retry = section_proxy.getint('retry', 3)
        self.is_open = False
        self.client_socket = None
        self.maxsize = 65534

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

    def open(self):
        try:
            self.socket = socket(self.af, SOCK_STREAM)
            if self.dest == "255.255.255.255":
                self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.socket.settimeout(self.timeout)
            sendbuf = self.socket.getsockopt(SOL_SOCKET, SO_SNDBUF)
            if sendbuf < self.maxsize:
                self.maxsize = sendbuf
            if not self.sport is None and not self.src is None:
                if self.af == AF_INET:
                    self.socket.bind((self.src, self.sport))
                elif self.af == AF_INET6:
                    try:
                        #this should be the way for v6 addr, for some reason failed on me ):
                        #self.socket.bind((self.src, self.sport, 0, 0))
                        self.socket.bind((self.src, self.sport))
                    except:
                        if not self.interface is '':
                            (_, _, _, _, addri) = getaddrinfo("%s%%%s" % (self.src, self.interface), self.sport, family=AF_INET6, proto=IPPROTO_TCP)[0]
                            self.socket.bind(addri)
                        else:
                            raise SessionException("cant bind to ipv6 LL without interface!")
            if self.server_side:
                self.socket.listen(1)
                (self.client_socket, (rip, rport)) = self.socket.accept()
                if self.dport:
                    while self.dport != rport or self.src != rip:
                        if self.dport != rport:
                            print_dizzy("session/tcp: remote port %i not destination port %i" % (rport, self.dport), DEBUG)
                        if self.src != rip:
                            print_dizzy("session/tcp: remote ip %s not destination ip %i" % (rip, self.dst))
                        (self.client_socket, (sip, rport)) = self.socket.accept()
                self.client_socket.settimeout(self.timeout)
            else:
                connected = False
                attempt = 1
                try:
                    self.socket.connect((self.dest, self.dport))
                    connected = True
                except timeout:
                    print_dizzy("session/tcp: Connection attempt %d timed out." % (attempt))
                    while not connected and attempt <= self.connect_retry:
                        try:
                            (r, w, x) = select([], [self.socket], [], self.timeout)
                            if self.socket in w:
                                connected = True
                        except:
                            pass
                        attempt += 1
                    if not connected:
                        raise SessionException("too much connection attempts")
        except Exception as e:
            raise SessionException("cant open session: %s" % e)
        else:
            self.is_open = True

    def close(self):
        if not self.is_open:
            return
        if not self.socket is None:
            self.socket.close()
            self.socket = None
        if not self.client_socket is None:
            self.client_socket.close()
            self.client_socket = None
        self.is_open = False

    def send(self, data):
        try:
            if not self.maxsize is None and len(data) > self.maxsize:
                data = data[:self.maxsize - 1]
                print_dizzy("session/tcp: Truncated data to %d byte." % self.maxsize, DEBUG)

            if self.server_side:
                if not self.client_socket:
                    raise SessionException("no client connection, cant send")
                self.client_socket.send(data)
            else:
                self.socket.send(data)
        except Exception as e:
            if self.auto_reopen:
                print_dizzy("session/tcp: session got closed '%s', auto reopening..." % e, DEBUG)
                print_dizzy(e, DEBUG)
                self.close()
                self.open()
            else:
                self.close()
                raise SessionException("error on sending '%s', connection closed." % e)

    def recv(self):
        if self.server_side:
            return self.client_socket.recv(self.recv_buffer)
        else:
            return self.socket.recv(self.recv_buffer)
