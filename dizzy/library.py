#       library.py
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

#import math

#from dizzy.config import CONFIG
from dizzy import tools
from dizzy.value import Value

class DizzyLibrary(object):
    def __init__(self):
        self.lib = {}

    def load_file(self, filename, listname=None):
        if listname is None:
            listname = filename
        if listname in self.lib:
            return self.lib[listname]
        self.lib[listname] = []
        with open(filename, 'r+b') as f:
            for l in f:
                if l.rstrip(b'\n') in self.lib[listname]:
                    pass
                v = Value(l.rstrip(b'\n'))
                self.lib[listname].append(v)
        return self.lib[listname]








class dizz_library(object):
    def __init__(self):
        self.lib = {}
        self.load_strings(CONFIG["GLOBALS"]["DEFAULT_STR_LIB"])

    def get_next(self, obj):
        libidx = obj["length"]
        if libidx is None:
            if not obj["encoding"] is None:
                cur = obj["cur"].decode(obj["encoding"])
            else:
                cur = obj["cur"].decode(CONFIG["GLOBALS"]["CODEC"])
        else:
            cur = obj["cur"]
        if obj["_type"] == "list":
            libidx = obj["listname"]
        if not libidx in self.lib:
            self.gen_entries(libidx)
        if cur not in self.lib[libidx]:
            if libidx == None:
                return self.lib[libidx][0]
            return None
        return self.lib[libidx][self.lib[libidx].index(cur) + 1]

    def _get_next(self, index, cur):
        if not index in self.lib:
            self.gen_entries(index)
        if cur is None:
            return self.lib[index][0]
        return self.lib[index][self.lib[index].index(cur) + 1]

    def gen_entries(self, length):
        bytelen = length // 8
        if length % 8 > 0:
            bytelen += 1
        if length >= 4:
            entr = []
            entr += [tools.pack_with_length(0, length)]
            entr += [tools.pack_with_length(1, length)]
            entr += [tools.pack_with_length(2, length)]
            entr += [tools.pack_with_length(3, length)]
            entr += [tools.pack_with_length(4, length)]
            if length > 8:
                entr += [tools.pack_with_length(1, length, endian="<")]
                entr += [tools.pack_with_length(2, length, endian="<")]
                entr += [tools.pack_with_length(3, length, endian="<")]
                entr += [tools.pack_with_length(4, length, endian="<")]
            max = int(math.pow(2, length)) - 1
            if length > 8:
                entr += [tools.pack_with_length(max - 4, length, endian="<")]
                entr += [tools.pack_with_length(max - 3, length, endian="<")]
                entr += [tools.pack_with_length(max - 2, length, endian="<")]
                entr += [tools.pack_with_length(max - 1, length, endian="<")]
                entr += [tools.pack_with_length((max / 2), length, endian="<")]
                entr += [tools.pack_with_length((max / 2) + 1, length, endian="<")]
                entr += [tools.pack_with_length(((max / 2) + 1) / 2, length, endian="<")]
            entr += [tools.pack_with_length(max - 4, length)]
            entr += [tools.pack_with_length(max - 3, length)]
            entr += [tools.pack_with_length(max - 2, length)]
            entr += [tools.pack_with_length(max - 1, length)]
            entr += [tools.pack_with_length(max, length)]
            entr += [tools.pack_with_length((max / 2), length)]
            entr += [tools.pack_with_length((max / 2) + 1, length)]
            entr += [tools.pack_with_length(((max / 2) + 1) / 2, length)]
            entr += [None]
        elif length == 3:
            entr = [b"\x00", b"\x01", b"\x02", b"\x03", b"\x04", b"\x05", b"\x06", b"\x07", None]
        elif length == 2:
            entr = [b"\x00", b"\x01", b"\x02", b"\x03", None]
        elif length == 1:
            entr = [b"\x00", b"\x01", None]
        self.lib[length] = tools.unique(entr)

    def load_strings(self, filename, listname=None):
        if listname in self.lib:
            return
        self.lib[listname] = [ b"", None ]
        with open(filename, 'r+b') as f:
            for l in f:
                if l.rstrip(b'\n') in self.lib[listname]:
                    pass
                b = l.rstrip(b'\n')
                self.lib[listname].insert(-1, b)
