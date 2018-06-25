#       module.py
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

from zipimport import zipimporter
import sys

from dizzy.log import print_dizzy, VERBOSE_1, VERBOSE_2, DEBUG

class DizzyModule(object):
    def __init__(self, path, config):
        self.path = path
        self.global_config = config
        self.zipimport = zipimporter(path)
        self.config = self.zipimport.load_module("config")

    def load(self):
        inventory = self.zipimport.load_module(self.name).__all__

        if "deps" in inventory:
            depspath = self.path + "/" + self.name + "/deps"
            sys.path.insert(0, depspath)
            print_dizzy("mod:%s/load: added dependency path '%s'" % (self.name, depspath), VERBOSE_1)

        sys.path.insert(0, self.path)
        if "dizz" in inventory:
            dizz = __import__(self.name + ".dizz").dizz
            self.dizz = []
            for i in dizz.__all__:
                name = self.name + "/dizz/" + i
                obj = dizz.__loader__.get_data(name)
                self.dizz.append(name)
                self.global_config["DIZZ"][name] = obj.decode(self.global_config["GLOBALS"]["CODEC"])

            print_dizzy("mod:%s/load: Loaded %d dizz files." % (self.name, len(self.dizz)), VERBOSE_1)
            print_dizzy("mod:%s/load: %s" % (self.name, self.dizz), DEBUG)

        if "act" in inventory:
            act = __import__(self.name + ".act").act
            self.act = []
            for i in act.__all__:
                name = self.name + "/act/" + i
                obj = act.__loader__.get_data(name)
                self.act.append(name)
                self.global_config["ACT"][name] = obj.decode(self.global_config["GLOBALS"]["CODEC"])

            print_dizzy("mod:%s/load: Loaded %d act files." % (self.name, len(self.act)), VERBOSE_1)
            print_dizzy("mod:%s/load: %s" % (self.name, self.act), DEBUG)

        if "job" in inventory:
            job = __import__(self.name + ".job").job
            self.job = []
            for i in job.__all__:
                name = self.name + "/job/" + i
                obj = job.__loader__.get_data(name)
                self.job.append(name)
                self.global_config["JOB"][name] = obj.decode(self.global_config["GLOBALS"]["CODEC"])

            print_dizzy("mod:%s/load: Loaded %d job files." % (self.name, len(self.job)), VERBOSE_1)
            print_dizzy("mod:%s/load: %s" % (self.name, self.job), DEBUG)

        if "probe" in inventory:
            probe = __import__(self.name + ".probe").probe
            self.probe = []
            for i in probe.__all__:
                name = self.name + ".probe." + i
                obj = getattr(__import__(name).probe, i)
                self.probe.append(name)
                self.global_config["PROBE"][name] = obj

            print_dizzy("mod:%s/load: Loaded %d target probes." % (self.name, len(self.probe)), VERBOSE_1)
            print_dizzy("mod:%s/load: %s" % (self.name, self.probe), DEBUG)

        if "session" in inventory:
            session = __import__(self.name + ".session").session
            self.session = []
            for i in session.__all__:
                name = self.name + ".session." + i
                obj = getattr(__import__(name).session, i)
                self.session.append(name)
                self.global_config["SESSION"][name] = obj

            print_dizzy("mod:%s/load: Loaded %d sessions." % (self.name, len(self.session)), VERBOSE_1)
            print_dizzy("mod:%s/load: %s" % (self.name, self.session), DEBUG)

        sys.path.remove(self.path)

    @property
    def name(self):
        return self.config.name

    @property
    def dependencies(self):
        return self.config.dependencies

    @property
    def version(self):
        return self.config.version