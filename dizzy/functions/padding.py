#       padding.py
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
from dizzy.value import Value
from . import BOTH
from os import urandom


def padding(target, start, stop, modulo, pattern=b"\x00", when=BOTH):
    def func(dizzy_iterator):
        if target not in dizzy_iterator.current_mutated_objects:
            mod = (dizzy_iterator[start:stop].size % modulo)
            if mod > 0:
                size_in_bits = modulo - mod
                dizzy_iterator[target] = Value(pattern * ((size_in_bits + 7) // 8), size_in_bits)
            else:
                dizzy_iterator[target] = ""
    return (func, when)


# Source: https://en.wikipedia.org/wiki/Padding_(cryptography)


def padding_zero(target, start, stop, modulo, when=BOTH):
    return padding(target, start, stop, modulo, pattern=b"\x00", when=when)


def padding_pkcs7(target, start, stop, modulo, when=BOTH):
    def func(dizzy_iterator):
        if target not in dizzy_iterator.current_mutated_objects:
            size_in_bits = modulo - (dizzy_iterator[start:stop].size % modulo)
            size_in_bytes = ((size_in_bits + 7) // 8)
            dizzy_iterator[target] = Value(size_in_bytes.to_bytes(1, 'big') * size_in_bytes, size_in_bits)

    return (func, when)


def padding_ansi_x923(target, start, stop, modulo, when=BOTH):
    def func(dizzy_iterator):
        if target not in dizzy_iterator.current_mutated_objects:
            size_in_bits = modulo - (dizzy_iterator[start:stop].size % modulo)
            size_in_bytes = ((size_in_bits + 7) // 8)
            dizzy_iterator[target] = Value((size_in_bytes - 1) * b"\x00" + size_in_bytes.to_bytes(1, 'big'),
                                           size_in_bits)

    return (func, when)


def padding_iso_10126(target, start, stop, modulo, when=BOTH):
    def func(dizzy_iterator):
        if target not in dizzy_iterator.current_mutated_objects:
            size_in_bits = modulo - (dizzy_iterator[start:stop].size % modulo)
            size_in_bytes = ((size_in_bits + 7) // 8)
            dizzy_iterator[target] = Value(urandom(size_in_bytes - 1) + size_in_bytes.to_bytes(1, 'big'), size_in_bits)

    return (func, when)


def padding_iso_iec_7816_4(target, start, stop, modulo, when=BOTH):
    def func(dizzy_iterator):
        if target not in dizzy_iterator.current_mutated_objects:
            size_in_bits = modulo - (dizzy_iterator[start:stop].size % modulo)
            size_in_bytes = ((size_in_bits + 7) // 8)
            dizzy_iterator[target] = Value(b"\80" + (size_in_bytes - 1) * b"\x00", size_in_bits)

    return (func, when)