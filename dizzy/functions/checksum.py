#       checksum.py
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
from hashlib import md5, sha1, sha224, sha256, sha384, sha512
from struct import pack

def checksum(target, start, stop, algorithm, callback=None, when=BOTH):
    def func(dizzy_iterator):
        if algorithm == "md5":
            hash_algorithm = md5()
        elif algorithm == "sha1":
            hash_algorithm = sha1()
        elif algorithm == "sha224":
            hash_algorithm = sha224()
        elif algorithm == "sha256":
            hash_algorithm = sha256()
        elif algorithm == "sha384":
            hash_algorithm = sha384()
        elif algorithm == "sha512":
            hash_algorithm = sha512()
        else:
            if callback is None:
                raise Exception("Hash algorithm not found")
            else:
                hash_algorithm = None

        size = dizzy_iterator[target].size
        size_bytes = (size + 7) // 8

        dizzy_iterator[target] = Value(b'\x00' * size_bytes, size)
        if not hash_algorithm is None:
            hash_algorithm.update(dizzy_iterator[start:stop].byte)
            digest = hash_algorithm.digest()
        else:
            digest = callback(dizzy_iterator[start:stop].byte)
        dizzy_iterator[target] = Value(digest[:size_bytes], size)

    return (func, when)

def checksum_inet(target, start, stop, when=BOTH):
    def func(dizzy_iterator):
        data = dizzy_iterator[start:stop].byte
        checksum = 0
        for i in range(0, len(data),2):
            if i + 1 >= len(data):
                checksum += data[i] & 0xFF
            else:
                w = ((data[i] << 8) & 0xFF00) + (data[i+1] & 0xFF)
                checksum += w
        while (checksum >> 16) > 0:
            checksum = (checksum & 0xFFFF) + (checksum >> 16)
        checksum = ~checksum
        dizzy_iterator[target] = pack("!H", checksum & 0xFFFF)

    return (func, when)
