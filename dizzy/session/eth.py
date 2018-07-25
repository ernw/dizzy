#       eth.py
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
from socket import AF_INET, IPPROTO_IP, gethostname, PF_PACKET, SOCK_RAW, socket, gethostbyname
from ctypes import Structure, c_char, c_short, create_string_buffer
from dizzy.config import CONFIG
from dizzy.log import print_dizzy, DEBUG
from dizzy.tools import check_root

class Ifreq(Structure):
    _fields_ = [("ifr_ifrn", c_char * 16), ("ifr_flags", c_short)]

class DizzySession(object):
    IFF_PROMISC = 0x100
    SIOCGIFFLAGS = 0x8913
    SIOCSIFFLAGS = 0x8914
    ETH_P_ALL = 0x0003

    def __init__(self, section_proxy):
        check_root("use the ETH session")

        self.interface = section_proxy.get('target_interface')
        self.timeout = section_proxy.getfloat('timeout', 1)
        self.recv_buffer = section_proxy.getfloat('recv_buffer', 4096)
        self.auto_reopen = section_proxy.getboolean('auto_reopen', True)
        self.server_side = section_proxy.getboolean('server', False)
        self.read_first = self.server_side
        self.read_first = section_proxy.getboolean('read_first', self.read_first)
        self.is_open = False

    def open(self):
        try:
            if CONFIG["GLOBALS"]["PLATFORM"] == "Windows":
                from socket import SIO_RCVALL, RCVALL_ON
                self.s = socket(AF_INET, SOCK_RAW, IPPROTO_IP)
                host = gethostbyname(gethostname())
                self.s.bind((host, 0))
                # enable promisc
                self.s.ioctl(SIO_RCVALL, RCVALL_ON)
            else:
                self.s = socket(PF_PACKET, SOCK_RAW, self.ETH_P_ALL)
                # set interface
                self.s.bind((self.interface, self.ETH_P_ALL))
                # enable promisc
                import fcntl
                self.ifr = Ifreq()
                ifname = create_string_buffer(self.interface.encode(CONFIG["GLOBALS"]["CODEC"]))
                self.ifr.ifr_ifrn = ifname.value
                fcntl.ioctl(self.s.fileno(), self.SIOCGIFFLAGS, self.ifr)  # G for Get
                self.ifr.ifr_flags |= self.IFF_PROMISC
                fcntl.ioctl(self.s.fileno(), self.SIOCSIFFLAGS, self.ifr)  # S for Set
            self.maxsize = 1500
        except Exception as e:
            raise SessionException("session/eth: cant open session: %s" % e)
        else:
            self.is_open = True

    def close(self):
        if CONFIG["GLOBALS"]["PLATFORM"] == "Windows":
            self.s.ioctl(SIO_RCVALL, RCVALL_OFF)
        else:
            self.ifr.ifr_flags &= ~self.IFF_PROMISC
            import fcntl
            fcntl.ioctl(self.s.fileno(), self.SIOCSIFFLAGS, self.ifr)
        self.is_open = False

    def send(self, data):
        try:
            if not self.maxsize is None and len(data) > self.maxsize:
                data = data[:self.maxsize - 1]
                print_dizzy("session/eth: Truncated data to %d byte." % self.maxsize, DEBUG)
            self.s.send(data)
        except Exception as e:
            if self.auto_reopen:
                print_dizzy("session/eth: session got closed '%s', autoreopening..." % e, DEBUG)
                print_dizzy(e, DEBUG)
                self.close()
                self.open()
            else:
                self.close()
                raise SessionException("error on sending '%s', connection closed." % e)

    def recv(self):
        return self.s.recv(2048)
