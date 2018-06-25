#       test_dizz.py
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
from dizzy.dizz import Dizz, load_dizz
from dizzy.value import Value
from dizzy.objects import START, END
from dizzy.objects.field import Field
from dizzy.functions.length import length
from dizzy.functions import BOTH

class TestDizzy(TestCase):
    def test_init(self):
        objects = list()
        objects.append(Field("test0", b"\x01\xff", 10, "std"))
        objects.append(Field("test1", b"\xab", 8, "std"))
        objects.append(Field("test2", b"\x00\xff", 12, "std"))

        d = Dizz("test", objects, fuzz="none")
        self.assertEqual(first(d), Value(b'\x1f\xfa\xb0\xff', 30))

    def test_iter(self):
        expected = [Value(b'\x00""w3\x00!', 49), Value(b'\x00\x00\x00w3\x00!', 49), Value(b'\x00\x00\x02w3\x00!', 49),
                    Value(b'\x00\x00\x04w3\x00!', 49), Value(b'\x00\x00\x06w3\x00!', 49),
                    Value(b'\x00\x00\x08w3\x00!', 49), Value(b'\x01\xff\xf6w3\x00!', 49),
                    Value(b'\x01\xff\xf8w3\x00!', 49), Value(b'\x01\xff\xfaw3\x00!', 49),
                    Value(b'\x01\xff\xfcw3\x00!', 49), Value(b'\x01\xff\xfew3\x00!', 49),
                    Value(b'\x00\xff\xf8w3\x00!', 49), Value(b'\x00\xff\xfaw3\x00!', 49),
                    Value(b'\x00\xff\xfcw3\x00!', 49), Value(b'\x00\xff\xfew3\x00!', 49),
                    Value(b'\x00\x02\x00w3\x00!', 49), Value(b'\x00\x04\x00w3\x00!', 49),
                    Value(b'\x00\x06\x00w3\x00!', 49), Value(b'\x00\x08\x00w3\x00!', 49), Value(b'\x00""33\x00!', 49),
                    Value(b'\x00""33\x00!', 49), Value(b'\x00""73\x00!', 49), Value(b'\x00""73\x00!', 49),
                    Value(b'\x00"";3\x00!', 49), Value(b'\x00"#\xf73\x00!', 49), Value(b'\x00"#\xfb3\x00!', 49),
                    Value(b'\x00"#\xfb3\x00!', 49), Value(b'\x00"#\xff3\x00!', 49), Value(b'\x00"#\xff3\x00!', 49),
                    Value(b'\x00""\xfb3\x00!', 49), Value(b'\x00""\xfb3\x00!', 49), Value(b'\x00""\xff3\x00!', 49),
                    Value(b'\x00""\xff3\x00!', 49), Value(b'\x00""D\x00\x00!', 49), Value(b'\x00""D\x01\x00!', 49),
                    Value(b'\x00""D\x02\x00!', 49), Value(b'\x00""D\x03\x00!', 49), Value(b'\x00""D\x04\x00!', 49),
                    Value(b'\x00""E\xfb\x00!', 49), Value(b'\x00""E\xfc\x00!', 49), Value(b'\x00""E\xfd\x00!', 49),
                    Value(b'\x00""E\xfe\x00!', 49), Value(b'\x00""E\xff\x00!', 49), Value(b'\x00""D\xfc\x00!', 49),
                    Value(b'\x00""D\xfd\x00!', 49), Value(b'\x00""D\xfe\x00!', 49), Value(b'\x00""D\xff\x00!', 49),
                    Value(b'\x00""E\x00\x00!', 49), Value(b'\x00""F\x00\x00!', 49), Value(b'\x00""G\x00\x00!', 49),
                    Value(b'\x00""D\x00\x00!', 49), Value(b'\x00DD\x88\x00\x00"', 50),
                    Value(b'\x00DD\x88\x01\x00"', 50), Value(b'\x00DD\x88\x02\x00"', 50),
                    Value(b'\x00DD\x88\x03\x00"', 50), Value(b'\x00DD\x88\x04\x00"', 50),
                    Value(b'\x00DD\x8b\xfb\x00"', 50), Value(b'\x00DD\x8b\xfc\x00"', 50),
                    Value(b'\x00DD\x8b\xfd\x00"', 50), Value(b'\x00DD\x8b\xfe\x00"', 50),
                    Value(b'\x00DD\x8b\xff\x00"', 50), Value(b'\x00DD\x89\xfc\x00"', 50),
                    Value(b'\x00DD\x89\xfd\x00"', 50), Value(b'\x00DD\x89\xfe\x00"', 50),
                    Value(b'\x00DD\x89\xff\x00"', 50), Value(b'\x00DD\x89\x00\x00"', 50),
                    Value(b'\x00DD\x8a\x00\x00"', 50), Value(b'\x00DD\x8b\x00\x00"', 50),
                    Value(b'\x00DD\x8c\x00\x00"', 50), Value(b'\x00\x88\x89\x10\x00\x00#', 51),
                    Value(b'\x00\x88\x89\x10\x01\x00#', 51), Value(b'\x00\x88\x89\x10\x02\x00#', 51),
                    Value(b'\x00\x88\x89\x10\x03\x00#', 51), Value(b'\x00\x88\x89\x10\x04\x00#', 51),
                    Value(b'\x00\x88\x89\x17\xfb\x00#', 51), Value(b'\x00\x88\x89\x17\xfc\x00#', 51),
                    Value(b'\x00\x88\x89\x17\xfd\x00#', 51), Value(b'\x00\x88\x89\x17\xfe\x00#', 51),
                    Value(b'\x00\x88\x89\x17\xff\x00#', 51), Value(b'\x00\x88\x89\x13\xfc\x00#', 51),
                    Value(b'\x00\x88\x89\x13\xfd\x00#', 51), Value(b'\x00\x88\x89\x13\xfe\x00#', 51),
                    Value(b'\x00\x88\x89\x13\xff\x00#', 51), Value(b'\x00\x88\x89\x11\x00\x00#', 51),
                    Value(b'\x00\x88\x89\x12\x00\x00#', 51), Value(b'\x00\x88\x89\x13\x00\x00#', 51),
                    Value(b'\x00\x88\x89\x14\x00\x00#', 51), Value(b'\x01\x11\x12 \x00\x00$', 52),
                    Value(b'\x01\x11\x12 \x01\x00$', 52), Value(b'\x01\x11\x12 \x02\x00$', 52),
                    Value(b'\x01\x11\x12 \x03\x00$', 52), Value(b'\x01\x11\x12 \x04\x00$', 52),
                    Value(b'\x01\x11\x12/\xfb\x00$', 52), Value(b'\x01\x11\x12/\xfc\x00$', 52),
                    Value(b'\x01\x11\x12/\xfd\x00$', 52), Value(b'\x01\x11\x12/\xfe\x00$', 52),
                    Value(b'\x01\x11\x12/\xff\x00$', 52), Value(b"\x01\x11\x12'\xfc\x00$", 52),
                    Value(b"\x01\x11\x12'\xfd\x00$", 52), Value(b"\x01\x11\x12'\xfe\x00$", 52),
                    Value(b"\x01\x11\x12'\xff\x00$", 52), Value(b'\x01\x11\x12!\x00\x00$', 52),
                    Value(b'\x01\x11\x12"\x00\x00$', 52), Value(b'\x01\x11\x12#\x00\x00$', 52),
                    Value(b'\x01\x11\x12$\x00\x00$', 52), Value(b'\x02"$@\x00\x00%', 53),
                    Value(b'\x02"$@\x01\x00%', 53), Value(b'\x02"$@\x02\x00%', 53), Value(b'\x02"$@\x03\x00%', 53),
                    Value(b'\x02"$@\x04\x00%', 53), Value(b'\x02"$_\xfb\x00%', 53), Value(b'\x02"$_\xfc\x00%', 53),
                    Value(b'\x02"$_\xfd\x00%', 53), Value(b'\x02"$_\xfe\x00%', 53), Value(b'\x02"$_\xff\x00%', 53),
                    Value(b'\x02"$O\xfc\x00%', 53), Value(b'\x02"$O\xfd\x00%', 53), Value(b'\x02"$O\xfe\x00%', 53),
                    Value(b'\x02"$O\xff\x00%', 53), Value(b'\x02"$A\x00\x00%', 53), Value(b'\x02"$B\x00\x00%', 53),
                    Value(b'\x02"$C\x00\x00%', 53), Value(b'\x02"$D\x00\x00%', 53), Value(b'\x04DH\x80\x00\x00&', 54),
                    Value(b'\x04DH\x80\x01\x00&', 54), Value(b'\x04DH\x80\x02\x00&', 54),
                    Value(b'\x04DH\x80\x03\x00&', 54), Value(b'\x04DH\x80\x04\x00&', 54),
                    Value(b'\x04DH\xbf\xfb\x00&', 54), Value(b'\x04DH\xbf\xfc\x00&', 54),
                    Value(b'\x04DH\xbf\xfd\x00&', 54), Value(b'\x04DH\xbf\xfe\x00&', 54),
                    Value(b'\x04DH\xbf\xff\x00&', 54), Value(b'\x04DH\x9f\xfc\x00&', 54),
                    Value(b'\x04DH\x9f\xfd\x00&', 54), Value(b'\x04DH\x9f\xfe\x00&', 54),
                    Value(b'\x04DH\x9f\xff\x00&', 54), Value(b'\x04DH\x81\x00\x00&', 54),
                    Value(b'\x04DH\x82\x00\x00&', 54), Value(b'\x04DH\x83\x00\x00&', 54),
                    Value(b'\x04DH\x84\x00\x00&', 54), Value(b"\x08\x88\x91\x00\x00\x00'", 55),
                    Value(b"\x08\x88\x91\x00\x01\x00'", 55), Value(b"\x08\x88\x91\x00\x02\x00'", 55),
                    Value(b"\x08\x88\x91\x00\x03\x00'", 55), Value(b"\x08\x88\x91\x00\x04\x00'", 55),
                    Value(b"\x08\x88\x91\x7f\xfb\x00'", 55), Value(b"\x08\x88\x91\x7f\xfc\x00'", 55),
                    Value(b"\x08\x88\x91\x7f\xfd\x00'", 55), Value(b"\x08\x88\x91\x7f\xfe\x00'", 55),
                    Value(b"\x08\x88\x91\x7f\xff\x00'", 55), Value(b"\x08\x88\x91?\xfc\x00'", 55),
                    Value(b"\x08\x88\x91?\xfd\x00'", 55), Value(b"\x08\x88\x91?\xfe\x00'", 55),
                    Value(b"\x08\x88\x91?\xff\x00'", 55), Value(b"\x08\x88\x91\x01\x00\x00'", 55),
                    Value(b"\x08\x88\x91\x02\x00\x00'", 55), Value(b"\x08\x88\x91\x03\x00\x00'", 55),
                    Value(b"\x08\x88\x91\x04\x00\x00'", 55), Value(b'\x11\x11"\x00\x00\x00(', 56),
                    Value(b'\x11\x11"\x00\x01\x00(', 56), Value(b'\x11\x11"\x00\x02\x00(', 56),
                    Value(b'\x11\x11"\x00\x03\x00(', 56), Value(b'\x11\x11"\x00\x04\x00(', 56),
                    Value(b'\x11\x11"\xff\xfb\x00(', 56), Value(b'\x11\x11"\xff\xfc\x00(', 56),
                    Value(b'\x11\x11"\xff\xfd\x00(', 56), Value(b'\x11\x11"\xff\xfe\x00(', 56),
                    Value(b'\x11\x11"\xff\xff\x00(', 56), Value(b'\x11\x11"\x7f\xfc\x00(', 56),
                    Value(b'\x11\x11"\x7f\xfd\x00(', 56), Value(b'\x11\x11"\x7f\xfe\x00(', 56),
                    Value(b'\x11\x11"\x7f\xff\x00(', 56), Value(b'\x11\x11"\x01\x00\x00(', 56),
                    Value(b'\x11\x11"\x02\x00\x00(', 56), Value(b'\x11\x11"\x03\x00\x00(', 56),
                    Value(b'\x11\x11"\x04\x00\x00(', 56), Value(b'\x00""w3\x00\x00', 49),
                    Value(b'\x00""w3\x00\x01', 49), Value(b'\x00""w3\x00\x02', 49), Value(b'\x00""w3\x00\x03', 49),
                    Value(b'\x00""w3\x00\x04', 49), Value(b'\x00""w3\xff\xfb', 49), Value(b'\x00""w3\xff\xfc', 49),
                    Value(b'\x00""w3\xff\xfd', 49), Value(b'\x00""w3\xff\xfe', 49), Value(b'\x00""w3\xff\xff', 49),
                    Value(b'\x00""w3\x7f\xfc', 49), Value(b'\x00""w3\x7f\xfd', 49), Value(b'\x00""w3\x7f\xfe', 49),
                    Value(b'\x00""w3\x7f\xff', 49), Value(b'\x00""w3\x01\x00', 49), Value(b'\x00""w3\x02\x00', 49),
                    Value(b'\x00""w3\x03\x00', 49), Value(b'\x00""w3\x04\x00', 49)]

        objects = list()
        objects.append(Field("test0", b"\x11\x11", fuzz="std"))
        objects.append(Field("test1", b"\x22", fuzz="std"))
        objects.append(Field("test2", b"\x33\x33", slice(9, 17), fuzz="std"))
        objects.append(Field("length", b"\x00\x00", fuzz="std"))

        functions = list()
        functions.append(length("length", "test0", "test2"))

        d = Dizz("test", objects, functions, fuzz="std")

        self.assertEqual([i for i in d], expected)

    def test_length(self):
        objects = list()
        objects.append(Field("test0", b"\x01\xff", 10, "std"))
        objects.append(Field("test1", b"\xab", 8, "std"))
        objects.append(Field("test2", b"\x00\xff", 12, "std"))
        d = Dizz("test", objects, fuzz="std")
        self.assertEqual(len(list(d)), d.length())

    def test_start_at_std(self):
        objects = list()
        objects.append(Field("test0", b"\x01\xff", 10, "std"))
        objects.append(Field("test1", b"\xab", 8, "std"))
        objects.append(Field("test2", b"\x00\xff", 12, "std"))
        objects.append(Field("length", b"\x00\x00", fuzz="std"))

        functions = list()
        functions.append(length("length"))

        excepted = list(Dizz("test", objects, functions, fuzz="std"))
        for i in range(len(excepted)):
            got = list(Dizz("test", objects, functions, fuzz="std", start_at=i))
            self.assertEqual(excepted[i:], got)

    def test_start_at_full(self):
        objects = list()
        objects.append(Field("test0", b"\x01\xff", 10, "std"))
        objects.append(Field("test1", b"\xab", 8, "std"))
        objects.append(Field("test2", b"\x00\xff", 12, "std"))
        excepted = list(Dizz("test", objects, fuzz="full"))
        for i in range(len(excepted), 4):
            self.assertEqual(excepted[i:], list(Dizz("test", objects, fuzz="full", start_at=i)))

    def test_load(self):
        expected = Value(b'\x00\x00\x00.\xffSMBr\x00\x00\x00\x00\x18C\xc8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\xfe\xff\x00\x00\x00\x00\x00\x0b\x00\x02SMB 2.???\x00', 400)

        d = load_dizz("test", "dizzes/smb2/smb_com_negotiate_req.dizz")

        self.assertEqual(first(d), expected)

    def test_import(self):
        expected = [Value(b'\n\xed\xcc', 20), Value(b'\x02\xed\xcc', 20), Value(b'\x06\xed\xcc', 20),
                    Value(b'\n\xed\xcc', 20), Value(b'\x0e\xed\xcc', 20), Value(b'\n\xed\xcc', 20),
                    Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20),
                    Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20),
                    Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20),
                    Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20),
                    Value(b'\n\xed\xcc', 20), Value(b'\n\xec\xcc', 20), Value(b'\n\xed\xcc', 20),
                    Value(b'\n\xee\xcc', 20), Value(b'\n\xef\xcc', 20), Value(b'\n\xed\xcc', 20),
                    Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20),
                    Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20),
                    Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20),
                    Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20), Value(b'\n\xed\xcc', 20),
                    Value(b'\n\xed\xcc', 20)]

        objects = list()
        objects.append(Field("test0", b"\x01", 2, "full"))
        objects.append(Field("test1", b"\xff", 8, "std"))

        def func1(dizzy_iterator):
            dizzy_iterator["test1"] = b"\xaa"

        d1 = Dizz("test_import", objects, [(func1, BOTH)], fuzz="std")

        objects = list()
        objects.append(Field("test0", b"\x02", 2, "full"))
        objects.append(Field("test1", b"\xff", 8, "std"))
        objects.append(d1)

        def func0(dizzy_iterator):
            dizzy_iterator["test1"] = b"\xbb"
            dizzy_iterator["test_import"]["test1"] = b"\xcc"

        d0 = Dizz("test", objects, [(func0, BOTH)], fuzz="std")
        self.assertEqual(list(d0), expected)

    def test_int_assignment(self):
        objects = list()
        objects.append(Field("test0", b"\xaa", 10, "full", endian="<"))
        objects.append(Field("test1", b"\xff", 8, "std"))

        d0 = Dizz("test", objects, fuzz="std")
        d0_iter = iter(d0)
        d0_iter["test0"] = 1337
        self.assertEqual(d0_iter["test0"].byte, b'9\x05')

    def test_START_END(self):
        objects = list()
        objects.append(Field("test0", b"\x00"))
        objects.append(Field("test1", b"\xff\xff"))
        objects.append(Field("test2", b"\xaa"))

        d = Dizz("test", objects, [length("test1", endian="<")], fuzz="std")
        d_iter = iter(d)
        next(d_iter)
        self.assertEqual(d_iter[START], Value(b"\x00"))
        self.assertEqual(d_iter["test1"], Value(b"\x20\x00"))
        self.assertEqual(d_iter[END], Value(b"\xaa"))

if __name__ == '__main__':
    main()
