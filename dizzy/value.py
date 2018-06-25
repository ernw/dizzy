#       value.py
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

from copy import copy

def format_bytes(array, size):
    size = (size + 7) // 8
    length = len(array)
    if length > size:
        array = array[(length - size):]
    elif length < size:
        array = b'\x00' * (size - length) + array
    return array


class Value(object):
    def __init__(self, byte=b'', size=None):
        if isinstance(byte, str):
            from dizzy.config import CONFIG
            byte = byte.encode(CONFIG["GLOBALS"]["CODEC"])
        if isinstance(byte, bytes):
            if size is None:
                self.byte = byte
                self.size = len(self.byte) * 8
            elif isinstance(size, int):
                self.byte = format_bytes(byte, size)
                self.size = size
            else:
                raise TypeError()
        else:
            raise TypeError()
    
    def __add__(self, other):
        result = Value()

        if self.size == 0:
            result.byte = format_bytes(copy(other.byte), other.size)
            result.size = other.size
        elif other.size == 0:
            result.byte = format_bytes(copy(self.byte), self.size)
            result.size = self.size
        else:
            result.byte = bytearray(format_bytes(other.byte, other.size))
            mod = other.size % 8

            if mod == 0:
                result.byte = self.byte + result.byte
            else:
                for x in reversed(self.byte):
                    result.byte[0] |= (x << mod) & 0xff
                    result.byte.insert(0, x >> (8 - mod))

            result.size = self.size + other.size
            result.byte = bytes(format_bytes(result.byte, result.size))

        return result

    def __bytes__(self):
        return self.byte
    
    def __repr__(self):
        return "Value(%s, %d)" % (self.byte, self.size)

    def __len__(self):
        return self.size
    
    def __eq__(self, other):
        if not isinstance(other, Value):
            return False
        return self.byte == other.byte and self.size == other.size
