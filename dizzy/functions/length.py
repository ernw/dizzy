#       length.py
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
from dizzy.value import Value
from dizzy.tools import pack_with_length
from dizzy.objects import START, END
from dizzy.log import print_dizzy, DEBUG
from . import BOTH

def length(target, start=START, stop=END, endian="!", when=BOTH):
    def func(dizzy_iterator):
        if target not in dizzy_iterator.current_mutated_objects:
            size = dizzy_iterator[target].size
            value = Value(pack_with_length(dizzy_iterator[start:stop].size, size, endian), size)
            print_dizzy("length/%s: seting to %s." % (target, value), DEBUG)
            dizzy_iterator[target] = value
        else:
            print_dizzy("length/%s: is not updated." % (target,), DEBUG)

    return (func, when)

def length_bytes(target, start=START, stop=END, endian="!", when=BOTH):
    def func(dizzy_iterator):
        if target not in dizzy_iterator.current_mutated_objects:
            size = dizzy_iterator[target].size
            value = Value(pack_with_length((dizzy_iterator[start:stop].size + 7) // 8, size, endian), size)
            print_dizzy("length_bytes/%s: seting to %s." % (target, value), DEBUG)
            dizzy_iterator[target] = value
        else:
            print_dizzy("length_bytes/%s: is not updated." % (target,), DEBUG)

    return (func, when)

def length_string_bytes(target, start=START, stop=END, encoding=CONFIG["GLOBALS"]["CODEC"], when=BOTH):
    def func(dizzy_iterator):
        if target not in dizzy_iterator.current_mutated_objects:
            size = str((dizzy_iterator[start:stop].size + 7) // 8)
            value = Value(bytes(size, encoding), len(size) * 8)
            print_dizzy("length_string_bytes/%s: seting to %s." % (target, value), DEBUG)
            dizzy_iterator[target] = value
        else:
            print_dizzy("length_string_bytes/%s: is not updated." % (target,), DEBUG)

    return (func, when)

def length_lambda(target, start=START, stop=END, lam=lambda x: x, endian="!", when=BOTH):
    def func(dizzy_iterator):
        if target not in dizzy_iterator.current_mutated_objects:
            size = dizzy_iterator[target].size
            value = Value(pack_with_length(lam(dizzy_iterator[start:stop].size), size, endian), size)
            print_dizzy("length_lambda/%s: seting to %s." % (target, value), DEBUG)
            dizzy_iterator[target] = value
        else:
            print_dizzy("length_lambda/%s: is not updated." % (target,), DEBUG)

    return (func, when)

def length_lambda2(target, start=START, stop=END, lam=lambda x: x, lam2=lambda x: x, endian="!", when=BOTH):
    def func(dizzy_iterator):
        if target not in dizzy_iterator.current_mutated_objects:
            size = lam(dizzy_iterator[target].size)
            value = Value(pack_with_length(lam2(dizzy_iterator[start:stop].size), size, endian), size)
            print_dizzy("length_lambda2/%s: seting to %s." % (target, value), DEBUG)
            dizzy_iterator[target] = value
        else:
            print_dizzy("length_lambda2/%s: is not updated." % (target,), DEBUG)


    return (func, when)
