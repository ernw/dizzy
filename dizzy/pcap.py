#       pcap.py
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
import imp
import threading
from time import sleep

from dizzy.log import print_dizzy, VERBOSE_1, VERBOSE_2

class Pcap(threading.Thread):
    def __init__(self, config, filename):
        threading.Thread.__init__(self)
        try:
            import pcapy
            self.pcap = pcapy
        except:
            print_dizzy("No usable pcap library found. Be sure you have pcapy installed!")
            print_dizzy("Pcap recording disabled!")
            self.pcap = None
            return
        self.interface = config.get("interface", "any")
        print_dizzy("pcap/init: listening on interface '%s'." % self.interface, VERBOSE_1)
        if not self.interface is "any":
            if not self.interface in self.pcap.findalldevs():
                print_dizzy("Device '%s' not found, recording on _all_ interfaces.")
                self.interface = "any"
        self.filter = config.get("filter", "")
        if not self.filter is "":
            print_dizzy("pcap/init: using bpf '%s'." % self.filter, VERBOSE_1)
        self.snaplen = config.getint("snaplen", 8192)
        self.promisc = config.getboolean("promisc", True)
        self.to_ms = config.getint("to_ms", 10)
        self.cooldown = config.getint("cooldown", 0)
        self.filename = filename
        self.is_open = False

    def run(self):
        if self.pcap is None:
            return
        self.run = True
        self.pcap_object = self.pcap.open_live(self.interface, self.snaplen, self.promisc, self.to_ms)
        print_dizzy("pcap/run: pcap object opened.", VERBOSE_2)
        if not self.filter is "":
            self.pcap_object.setfilter(self.filter)
        self.pcap_dumper = self.pcap_object.dump_open(self.filename)
        print_dizzy("pcap/run: pcap dumper opened for file '%s'." % self.filename, VERBOSE_2)
        self.is_open = True
        while self.run:
            hdr, data = self.pcap_object.next()
            if not hdr is None:
                if self.is_open:
                    self.pcap_dumper.dump(hdr, data)

    def stop(self):
        if self.pcap is None:
            return
        if self.cooldown > 0:
            print_dizzy("pcap/stop: cooling down for %d seconds." % self.cooldown, VERBOSE_1)
            sleep(self.cooldown)
        self.run = False
        self.is_open = False
        self.pcap_dumper.close()
        print_dizzy("pcap/stop: pcap dumper closed for file '%s'." % self.filename, VERBOSE_2)
