#!/usr/bin/env python3

#       tools.py
#       
#       Copyright 2013 Daniel Mende <mail@c0decafe.de>
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
from . import DizzyRuntimeException
from dizzy.log import print_dizzy, DEBUG
from struct import unpack, pack

endian_format = {"<": "little",
                 ">": "big",
                 "!": "big"}


def unique(seq, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


def read_with_length(data, length, endian='!'):
    try:
        out = None
        if length <= 8:
            (out,) = unpack("%sB" % endian, data[0])
        elif length <= 16:
            (out,) = unpack("%sH" % endian, data[0:1])
        elif length <= 32:
            (out,) = unpack("%sI" % endian, data[0:3])
        elif length <= 64:
            (out,) = unpack("%sQ" % endian, data[0:7])
        else:
            raise DizzyRuntimeException("cant read with len >64")
    except Exception as e:
        print_dizzy("Can't unpack %s: %s" % (data, str(e)), DEBUG)
        raise e


def pack_with_length(value, size, endian='!'):
    return (value & ((1 << size) - 1)).to_bytes((size + 7) // 8, endian_format[endian])


def chr_to_bin(c):
    out = ""
    for i in range(0, 8):
        if i == 4:
            out += " "
        out += "%d" % (((ord(c) << i) & 0x80) >> 7)
    return out


def str_to_bin(s):
    out = ""
    c = 1
    for i in s:
        out += chr_to_bin(i)
        if c % 8 == 0:
            out += "\n"
        else:
            out += "  "
        c += 1
    return out[:-2]


def shift_left(inp, by, out=None):
    by = by % 8
    if inp == b"":
        return out
    l = len(inp)
    if isinstance(out, bytes) and len(out) == 1:
        out = bytes([out[0] | inp[0] >> 8 - by])
    else:
        out = b""
    for i in range(0, l):
        if i == l - 1:
            out += bytes([(inp[i] << by) & 0xff])
        else:
            out += bytes([((inp[i] << by) & 0xff) | (inp[i + 1] >> 8 - by)])
    return out


def shift_right(inp, by, out=None):
    by = by % 8
    l = len(inp)
    if isinstance(out, bytes) and len(out) == 1:
        if inp == b"":
            return out
        out = bytes([out[0] | ((inp[-1] << 8 - by) & 0xff)])
    else:
        out = b""
    for i in range(1, l + 1):
        if i == l:
            out = bytes([inp[-i] >> by]) + out
        else:
            out = bytes([inp[-i] >> by | ((inp[-i - 1] << 8 - by) & 0xff)]) + out
    return out


def csum_inet(data, csum=0):
    for i in range(0, len(data), 2):
        if i + 1 >= len(data):
            csum += data[i] & 0xFF
        else:
            w = ((data[i] << 8) & 0xFF00) + (data[i + 1] & 0xFF)
            csum += w
    while (csum >> 16) > 0:
        csum = (csum & 0xFFFF) + (csum >> 16)
    csum = ~csum
    return pack("!H", csum & 0xFFFF)

# ~ def align_mod(inp, blen, mod, out=b"\x00"):
# ~ out[0] |= (inp[0] << 8 - mod) & 0xff
# ~ for j in range(1, blen]):
# ~ tmp = out[-1] | (inp[j] >> mod)
# ~ out = out[:-1] + bytes([tmp])
# ~ tmp2 = (inp[j] << 8 - mod) & 0xff
# ~ out += bytes([tmp2])
# ~ return out
