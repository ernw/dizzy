#       test_field.py
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
from dizzy.tests import first
from dizzy.objects.field import Field
from dizzy.value import Value


class TestField(TestCase):
    def test_init(self):
        f = Field("test", b"\x01\x23", slice(10, 12), "std")
        self.assertEqual(f.name, "test")
        self.assertEqual(f.size, slice(10, 12, 1))
        self.assertEqual(f.default, Value(b"\x01\x23", 10))
        self.assertEqual(f.fuzz, "std")

    def test_add_aligned(self):
        chars1 = b"This is a test "
        chars2 = b"of adding adding aligned"
        chars3 = b" values."

        f1 = Field("test1", chars1)
        f2 = Field("test2", chars2)
        f3 = Field("test3", chars3)

        v1 = first(f1) + first(f2) + first(f3)

        self.assertTrue(isinstance(v1, Value))
        self.assertEqual(v1.byte, chars1 + chars2 + chars3)
        self.assertEqual(v1.size // 8, len(chars1) + len(chars2) + len(chars3))

    def test_add_unaligned(self):
        pass
    
    def test_iter(self):
        expected = [Value(b'\x01#', 10), Value(b'\x00\x00', 10), Value(b'\x00\x01', 10), Value(b'\x00\x02', 10),
                    Value(b'\x00\x03', 10), Value(b'\x00\x04', 10), Value(b'\x03\xfb', 10), Value(b'\x03\xfc', 10),
                    Value(b'\x03\xfd', 10), Value(b'\x03\xfe', 10), Value(b'\x03\xff', 10), Value(b'\x01\xfc', 10),
                    Value(b'\x01\xfd', 10), Value(b'\x01\xfe', 10), Value(b'\x01\xff', 10), Value(b'\x01\x00', 10),
                    Value(b'\x02\x00', 10), Value(b'\x03\x00', 10), Value(b'\x04\x00', 10)]
        f = Field("test", b"\x01\x23", 10, "std")
        self.assertEqual([i for i in f], expected)
    
    def test_size(self):
        f = Field("test", b"\x01\x23", 10, "std")
        self.assertEqual(f.length(), 19)
        self.assertEqual(len(list(f)), f.length())
        
        
if __name__ == '__main__':
    main()
