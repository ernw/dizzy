#       test_value.py
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
from unittest import TestCase, main
from dizzy.value import Value


class TestValue(TestCase):
    def test_init(self):
        v = Value(b"\x01\x23", 10)
        self.assertEqual(v.byte, b"\x01\x23")
        self.assertEqual(v.size, 10)
    
    def test_eq(self):
        v1 = Value(b"\x01\x23", 10)
        v2 = Value(b"\x01\x23", 10)
        v3 = Value(b"\x02", 2)
        self.assertEqual(v1, v2)
        self.assertNotEqual(v2, v3)

    def test_add_aligned(self):
        chars1 = b"This is a test "
        chars2 = b"of adding adding aligned"
        chars3 = b" values."
        v1 = Value(chars1, len(chars1) * 8)
        v2 = Value(chars2, len(chars2) * 8)
        v3 = Value(chars3, len(chars3) * 8)
        v4 = v1 + v2 + v3
        self.assertEqual(v4.byte, chars1 + chars2 + chars3)
        self.assertEqual(v4.size // 8, len(chars1) + len(chars2) + len(chars3))

    def test_add_unaligned(self):
        v1 = Value(b"\x01\x23", 10)
        v2 = Value(b"\x02", 2)
        v3 = v1 + v2
        self.assertEqual(v3.byte, b"\x04\x8e")
        self.assertEqual(v3.size, 12)
        v3 = v2 + v1
        self.assertEqual(v3.byte, b"\x09\x23")
        self.assertEqual(v3.size, 12)

        v1 = Value(b'\x00\x00', 10)
        v2 = Value(b'\x00\x1f\xf0\xff', 30)
        v3 = v1 + v2
        self.assertEqual(v3.byte, b'\x00\x00\x1f\xf0\xff')
        self.assertEqual(v3.size, 40)
    
    def test_add_empty(self):
        v1 = Value(b"", 0)
        v2 = Value(b"\x01\x23", 10)
        v3 = v1 + v2
        self.assertEqual(v3.byte, b"\x01\x23")
        self.assertEqual(v3.size, 10)
        v3 = v2 + v1
        self.assertEqual(v3.byte, b"\x01\x23")
        self.assertEqual(v3.size, 10)


if __name__ == '__main__':
    main()
