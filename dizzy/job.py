#       job.py
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
import atexit
from configparser import ConfigParser
from os import path
import socket
from statistics import mean
import sys
import tarfile
from tempfile import TemporaryDirectory
from threading import Thread, RLock
from time import time, sleep, strftime
from traceback import print_exc
from . import JobParseException
from dizzy.config import CONFIG
from dizzy.dizz import load_dizz
from dizzy.interaction import load_interaction
from dizzy.log import print_level, set_print_level, NORMAL, print_dizzy, DEBUG, VERBOSE_2, Logger
from dizzy.pcap import Pcap

def enumerate_interactions(interactions, i=0):
    for obj in interactions:
        yield i, obj
        if obj is None:
            i += 1

def create_archive(outfile, tempdir):
    with tarfile.open(outfile, 'w:xz') as out:
        out.add(tempdir.name)
    tempdir.cleanup()

class Job(Thread):
    TIME_LIST_MAX_LEN = 100

    def __init__(self, config_file, start_at=0, options={}, daemon=True):
        Thread.__init__(self, daemon=daemon)
        self.config_file = config_file
        self.config = ConfigParser(allow_no_value=True, interpolation=None)
        if path.exists(config_file):
            self.config.read(config_file)
        elif config_file in CONFIG["JOB"]:
                self.config.read_string(CONFIG["JOB"][config_file])
        else:
            raise JobParseException("Job '%s' not found." % config_file)
        self.config.read_dict(options)
        
        self.outfile = self.config['job'].get('outfile', './outfile_%s.tar.xz' % strftime("%Y-%m-%d_%H-%M-%S"))
        self.tempdir = TemporaryDirectory(prefix="dizzy-")
        atexit.register(create_archive, self.outfile, self.tempdir)
        sys.stdout = Logger(sys.stdout, path.join(self.tempdir.name, "stdout.log"))
        print_dizzy("job/run: cmd was: '%s'." % " ".join(sys.argv))

        if 'job' not in self.config:
            raise JobParseException("No 'job' section found in conf.")
        if 'file' not in self.config['job']:
            raise JobParseException("No 'file' found in conf.")
        if 'mode' not in self.config['job']:
            raise JobParseException("No 'mode' found in conf.")
        self.mode = self.config['job']['mode']
        self.file = self.config['job']['file']

        self.delay = self.config['job'].getfloat('delay', 1)
        self.verbose = self.config['job'].getint('verbose', NORMAL)
        set_print_level(self.verbose)

        if 'output' not in self.config:
            raise JobParseException("No 'output' section found in conf.")
        if 'type' not in self.config['output']:
            raise JobParseException("No 'type' found in conf.")
        self.out_type = self.config['output']['type']
        self.session_reopen = self.config['output'].getboolean('session_reopen', False)
        
        if 'values' in self.config:
            self.config_values = dict(self.config['values'])
        else:
            self.config_values = {}

        self.config_values['_output'] = dict(self.config['output'])

        if self.file.endswith('.act'):
            self.act = load_interaction(self.file, self.mode, start_at, \
                config_values=self.config_values)
            self.dizz = None
            self.mutations = self.act.iterations()
        elif self.file.endswith('.dizz'):
            self.dizz = load_dizz(self.file, self.file, 0, self.mode, start_at, \
                                  config_values=self.config_values)
            self.act = None
            self.mutations = self.dizz.length()
        else:
            raise JobParseException("Wrong input file in conf.")

        self.state_lock = RLock()

        self.probe = None
        self.probe_type = None
        if 'probe' in self.config:
            self.probe_type = self.config['probe'].get('type', None)

        if not self.probe_type is None:
            if self.probe_type in CONFIG["PROBE"]:
                self.probe = CONFIG["PROBE"][self.probe_type].DizzyProbe(self.config["probe"])
            else:
                print_dizzy("job/init: target probe '%s' not found." % self.probe_type)
                exit(1)
        if self.out_type in CONFIG["SESSION"]:
            self.session = CONFIG["SESSION"][self.out_type].DizzySession(self.config['output'])
            CONFIG["GLOBALS"]["SESSION"] = self.session
        else:
            print_dizzy("job/init: session '%s' not found." % self.out_type)
            exit(1)

        self.print_index = start_at + 1
        self.start_time = 0
        self.index = 0
        self.time_list = []
        self.session_reset = False
        self.pcap = None

    def __repr__(self):
        return "Job/%s %s" % (self.out_type, self.config_file)

    def print_status(self):
        self.state_lock.acquire()
        self.time_list.append(time() - self.start_time)
        time_mean = mean(self.time_list)
        if len(self.time_list) > self.TIME_LIST_MAX_LEN:
            self.time_list = [time_mean] * 50
        
        secs = (self.mutations - self.index) * time_mean
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        self.start_time = time()

        status = "%05.2f%% %i/%i iterations done.\n" % ((self.index / self.mutations) * 100, self.index, self.mutations)
        if d == 0:
            status += "eta %02d:%02d:%02d" % (h, m, s)
        else:
            status += "eta %d days %02d:%02d:%02d" % (d, h, m, s)

        if self.print_index == self.index or print_level == DEBUG:
            print_dizzy(status)
            self.print_index *= 2
        self.state_lock.release()
    
    def do_probe(self):
        res = True
        if not self.probe is None:
            if 'pcap' in self.config:
                self.pcap = Pcap(self.config['pcap'], path.join(self.tempdir.name, "trace-%s-probe.pcap" % self.index))
                self.pcap.start()
                while not self.pcap.is_open:
                    sleep(0.1)
            res = self.probe.probe()
            if not self.pcap is None:
                self.pcap.stop()
                self.pcap.join()
            if not res:
                print_dizzy("job/run: probe failed")
        return res

    def run(self):
        self.start_time = time()
        self.session.open()

        if self.probe:
            self.probe.open()
            if not self.probe.probe():
                print_dizzy("job/run: initial probe failed")
                return

        if self.act is None:
            for self.index, value in enumerate(self.dizz, self.print_index):
                if 'pcap' in self.config:
                    self.pcap = Pcap(self.config['pcap'], path.join(self.tempdir.name, "trace-%s.pcap" % self.index))
                    self.pcap.start()
                    while not self.pcap.is_open:
                        sleep(0.1)
                try:
                    self.session.send(value.byte)
                except Exception as e:
                    print_dizzy(e)
                    print_exc()
                self.read(self.session, 1)
                if not self.pcap is None:
                    self.pcap.stop()
                    self.pcap.join()
                if not self.do_probe():
                    break
                self.print_status()
        else:
            if 'pcap' in self.config:
                self.pcap = Pcap(self.config['pcap'], path.join(self.tempdir.name, "trace-%s.pcap" % self.index))            
                self.pcap.start()
                while not self.pcap.is_open:
                    sleep(0.1)

            if self.session.read_first:
                self.act.response, session_reset = self.read(self.session, 1)

            for self.index, value in enumerate_interactions(self.act, self.print_index):
                print_dizzy("job/run: index: %d, value: %s" % (self.index, value), DEBUG)
                if self.session_reset:
                    print_dizzy("job/run: Session reset triggered", DEBUG)
                    if not value is None:
                        continue

                if value is None:
                    if self.session_reopen or self.session_reset:
                        print_dizzy("job/run: Reseting session", DEBUG)
                        self.session.close()
                        if not self.pcap is None:
                            self.pcap.stop()
                            self.pcap.join()
                        sleep(self.delay)
                        if 'pcap' in self.config:
                            self.pcap = Pcap(self.config['pcap'], path.join(self.tempdir.name, "trace-%s.pcap" % self.index))            
                            self.pcap.start()
                            while not self.pcap.is_open:
                                sleep(0.1)
                        self.session.open()
                        self.session_reset = False
                    if not self.do_probe():
                        break
                    self.print_status()
                    continue

                try:
                    self.session.send(value.byte)
                except Exception as e:
                    print_dizzy(e)
                    self.session_reset = True
                    continue
                self.act.response, session_reset = self.read(self.session, value.dizz_iterator.dizz.readback)
        
        print_dizzy("job/run: end")

        if not self.pcap is None:
            self.pcap.stop()
            self.pcap.join()

        if self.probe:
            self.probe.close()

    def read(self, session, read_back=None):
        d = b""
        reconnect = False
        try:
            reading = True
            while reading:
                r = session.recv()
                if not r:
                    reading = False
                    print_dizzy("job/read: read end on NONE", DEBUG)
                else:
                    d += r
                    #print_dizzy(d, DEBUG)
                if not read_back is None:
                    if len(d) >= read_back:
                        reading = False
        except socket.timeout:
            print_dizzy("job/read: read end on timeout", VERBOSE_2)
        except socket.error as e:
            print_dizzy("job/read: read end on sock error '%s', reopening..." % str(e), VERBOSE_2)
            reconnect = True
        except Exception as e:
            print_dizzy("job/read: cant read input: %s" % str(e), VERBOSE_2)
            return "", True
        if not read_back is None and read_back > 0 and len(d) < read_back:
            print_dizzy("job/read: len(read): %i < rlen: %i, reconnect..." % (len(d), read_back), DEBUG)
            reconnect = True
        print_dizzy("job/read: data: %s reconnect: %s" % (d, reconnect), DEBUG)
        return d, reconnect
