#       icmp.py
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
from dizzy.tools import csum_inet
from os import getpid, geteuid
from socket import socket, inet_aton, inet_pton, getprotobyname, AF_INET, AF_INET6, SOCK_RAW, error
from struct import pack, unpack
from sys import exit

class DizzyProbe(object):
    ICMP_ECHO_REPLY = 0
    ICMP_ECHO = 8
    ICMP6_ECHO = 128
    ICMP6_ECHO_REPLY = 129
    
    def __init__(self, section_proxy):
        self.target_host = section_proxy.get('target_host')
        self.timeout = section_proxy.getfloat('timeout', 1)
        self.pkg_size = section_proxy.getint('pkg_size', 64)
        self.retry = section_proxy.getint('retry', 2)
        self.socket = None
        self.is_open = False

        try:
            inet_aton(self.target_host)
            self.af = AF_INET
            self.proto = getprotobyname("icmp")
            echo = self.ICMP_ECHO
        except Exception as e:
            try:
                inet_pton(AF_INET6, self.target_host)
                self.af = AF_INET6
                self.proto = getprotobyname("ipv6-icmp")
                echo = self.ICMP6_ECHO
            except Exception as f:
                raise ProbeParseException("probe/icmp: unknown address family: %s: %s, %s" %
                                               (self.target_host, e, f))
        self.pid = getpid() & 0xFFFF
        if geteuid() != 0:
            print_dizzy("probe/icmp: you must be root to use the ICMP probe.")
            exit(1)
        
        self.header = pack("!BBHHH", echo, 0, 0, self.pid, 0)

        pad = list()
        for i in range(0x41, 0x41 + self.pkg_size):
            pad += [(i & 0xff)]
        self.data = bytearray(pad)

        checksum = csum_inet(self.header + self.data)
        self.header = self.header[0:2] + checksum + self.header[4:]

    def open(self):
        try:
            self.socket = socket(self.af, SOCK_RAW, self.proto)
        except error as e:
            if not self.socket is None:
                self.socket.close()
            print_dizzy("probe/icmp: open error: '%s'" % e)
            print_dizzy(e, DEBUG)
        self.is_open = True
   
    def probe(self):
        if not self.is_open:
            print_dizzy("probe/tcp: not opened.", DEBUG)
            return False
        for attempt in range(1, self.retry + 1):
            print_dizzy("probe/icmp: probe attempt: %d" % attempt, VERBOSE_1)

            try:
                if self.af == AF_INET6:
                    self.socket.sendto(self.header + self.data, (self.target_host, 0, 0, 0))
                else:
                    self.socket.sendto(self.header + self.data, (self.target_host, 0))

                if self.af == AF_INET6:
                    (data, (address, _, _, _)) = self.socket.recvfrom(2048)
                    if address == self.target_host:
                        pid, = unpack("!H", data[4:6])
                        if data[0] == self.ICMP6_ECHO_REPLY and pid == self.pid:
                            return True
                else:
                    (data, (address, _)) = self.socket.recvfrom(2048)
                    if address == self.target_host:
                        hl = (data[0] & 0x0f) * 4
                        pid, = unpack("!H", data[hl + 4:hl + 6])
                        if data[hl] == self.ICMP_ECHO_REPLY and pid == self.pid:
                            return True
            except error as e:
                print_dizzy("probe/icmp: reopening: '%s'" % e)
                print_dizzy(e, DEBUG)
                self.close()
                self.open()

        return False

    def close(self):
        if not self.is_open:
            return
        if self.socket is not None:
            self.socket.close()
            self.socket = None
        self.is_open = False
