#       field.py
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
from dizzy.config import CONFIG
from dizzy.tools import pack_with_length
from dizzy.value import Value
from dizzy import DizzyParseException
from sys import maxsize

class Field:
    def __init__(self, name, default=b'', size=None, fuzz='none', endian="!", encoding=CONFIG["GLOBALS"]["CODEC"], extra_encoding=None, extra_encoding_data=None):
        if isinstance(name, str) and name:
            self.name = name
        else:
            raise DizzyParseException("Name must be str and not empty.")
        self.encoding = encoding
        self.extra_encoding = extra_encoding
        self.extra_encoding_data = extra_encoding_data

        if isinstance(default, str):
            self.default = bytes(default, self.encoding)
        elif isinstance(default, bytes):
            self.default = default
        elif isinstance(default, int):
            # TODO: check size type
            self.default = pack_with_length(default, size, endian)
        else:
            raise DizzyParseException('Default must be str, bytes or int: %s' % name)

        if isinstance(size, int):
            self.size = slice(size, size + 1, 1)
        elif size is None:
            self.size = len(self.default) * 8
            self.size = slice(self.size, self.size + 1, 1)
        elif isinstance(size, slice):
            self.size = size
        else:
            raise DizzyParseException("Unknown fuzzing mode: %s" % name)

        if self.size.start < 0:
            raise DizzyParseException('Length less than 0 are not allowed: %s' % name)
        elif self.size.stop <= self.size.start:
            raise DizzyParseException('Length less than 0 are not allowed: %s' % name)
        elif self.size.step is None:
            self.size = slice(self.size.start, self.size.stop, 1)
        elif self.size.step <= 0:
            raise DizzyParseException('Step must not be 0: %s' % name)

        self.fuzz = fuzz

        if self.fuzz == "full":
            if self.size.start > maxsize or self.size.stop > maxsize:
                raise DizzyParseException("Cannot make dizzy with length '%d' full fuzzable, "
                                          "this would take ages: %s" % (size, name))
            else:
                self.iter = self.iter_full
                self.len = 1
                for r in range(self.size.start, self.size.stop, self.size.step):
                    self.len += 2 ** r
        elif self.fuzz == 'std':
            self.iter = self.iter_std
            self.len = 1
            for r in range(self.size.start, self.size.stop, self.size.step):
                if r > 2:
                    self.len += 5
                    if r > 4:
                        self.len += 5
                        if r > 7:
                            self.len += 4
                            if r > 8:
                                self.len += 4
        elif self.fuzz is 'none':
            self.iter = self.iter_none
            self.len = 1
        else:
            raise DizzyParseException("Unknown fuzzing mode: %s" % name)

        self.default = Value(self.default, self.size.start)
        self.endian = endian

    def __iter__(self):
        return self.iter()
    
    def __repr__(self):
        return "Field(name=%s, default=%s, size=%s, fuzz=%s, endian=%s, encoding=%s)" % (self.name, self.default, self.size, self.fuzz, self.endian, self.encoding)

    def length(self):
        return self.len

    def iter_full(self):
        yield self.default
        for r in range(self.size.start, self.size.stop, self.size.step):
            i = 0
            byte_length = (r + 7) // 8
            max_value = 2 ** r
            while i < max_value:
                yield Value(i.to_bytes(byte_length, 'big'), r)
                i += 1

    def iter_std(self):
        yield self.default
        for r in range(self.size.start, self.size.stop, self.size.step):
            if r > 2:
                byte_length = (r + 7) // 8
                for i in range(0, 5):
                    yield Value(i.to_bytes(byte_length, 'big'), r)
                if r > 4:
                    buf = (2 ** r) - 1
                    for i in range(0, 5):
                        yield Value((buf - (4 - i)).to_bytes(byte_length, 'big'), r)
                    if r > 7:
                        buf = 2 ** (r - 1)
                        for i in range(0, 4):
                            yield Value((buf - (4 - i)).to_bytes(byte_length, 'big'), r)
                        if r > 8:
                            buf = 2 ** ((byte_length - 1) * 8)
                            for i in range(1, 5):
                                yield Value((i * buf).to_bytes(byte_length, 'big'), r)

    def iter_none(self):
        yield self.default
