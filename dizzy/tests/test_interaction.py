#       test_interations.py
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
from dizzy.interaction import Interaction
from dizzy.objects.field import Field
from dizzy.functions.length import length
from dizzy.dizz import Dizz
from dizzy.functions.checksum import checksum
from dizzy.functions import BOTH
from dizzy.value import Value

class TestInteraction(TestCase):
    def __init__(self, arg):
        self.maxDiff = None
        TestCase.__init__(self, arg)

    def test_init(self):
        objects = [Field("test0", b"\x11\x11", fuzz="std"), Field("test1", b"\x22", fuzz="std"),
                   Field("test2", b"\x33\x33", slice(9, 17), fuzz="std")]
        d0 = Dizz("test0", objects, fuzz="std")

        objects = [Field("test0", b"\xff", fuzz="full"), Field("test1", b"\xaa", 10, fuzz="std")]
        d1 = Dizz("test1", objects, fuzz="std")

        act = Interaction("Test", [d0, d1])
        self.assertEqual(act.name, "Test")
        self.assertEqual(act.objects, [d0, d1])

    def test_iter(self):
        expected = [Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x00\x00w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x00\x02w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x00\x04w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x00\x06w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x00\x08w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\xff\xf6w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\xff\xf8w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\xff\xfaw3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\xff\xfcw3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\xff\xfew3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\xff\xf8w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\xff\xfaw3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\xff\xfcw3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\xff\xfew3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x02\x00w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x04\x00w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x06\x00w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x08\x00w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""33\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""33\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""73\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""73\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00"";3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00"#\xf73\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00"#\xfb3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00"#\xfb3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00"#\xff3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00"#\xff3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""\xfb3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""\xfb3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""\xff3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""\xff3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""D\x00\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""D\x01\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""D\x02\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""D\x03\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""D\x04\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""E\xfb\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""E\xfc\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""E\xfd\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""E\xfe\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""E\xff\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""D\xfc\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""D\xfd\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""D\xfe\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""D\xff\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""E\x00\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""F\x00\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""G\x00\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""D\x00\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x88\x00\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x88\x01\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x88\x02\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x88\x03\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x88\x04\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x8b\xfb\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x8b\xfc\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x8b\xfd\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x8b\xfe\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x8b\xff\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x89\xfc\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x89\xfd\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x89\xfe\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x89\xff\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x89\x00\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x8a\x00\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x8b\x00\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00DD\x8c\x00\x00"', 50), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x10\x00\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x10\x01\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x10\x02\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x10\x03\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x10\x04\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x17\xfb\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x17\xfc\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x17\xfd\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x17\xfe\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x17\xff\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x13\xfc\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x13\xfd\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x13\xfe\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x13\xff\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x11\x00\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x12\x00\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x13\x00\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00\x88\x89\x14\x00\x00#', 51), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12 \x00\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12 \x01\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12 \x02\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12 \x03\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12 \x04\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12/\xfb\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12/\xfc\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12/\xfd\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12/\xfe\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12/\xff\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x01\x11\x12'\xfc\x00$", 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x01\x11\x12'\xfd\x00$", 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x01\x11\x12'\xfe\x00$", 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x01\x11\x12'\xff\x00$", 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12!\x00\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12"\x00\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12#\x00\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x01\x11\x12$\x00\x00$', 52), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$@\x00\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$@\x01\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$@\x02\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$@\x03\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$@\x04\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$_\xfb\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$_\xfc\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$_\xfd\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$_\xfe\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$_\xff\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$O\xfc\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$O\xfd\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$O\xfe\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$O\xff\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$A\x00\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$B\x00\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$C\x00\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x02"$D\x00\x00%', 53), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\x80\x00\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\x80\x01\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\x80\x02\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\x80\x03\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\x80\x04\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\xbf\xfb\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\xbf\xfc\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\xbf\xfd\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\xbf\xfe\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\xbf\xff\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\x9f\xfc\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\x9f\xfd\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\x9f\xfe\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\x9f\xff\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\x81\x00\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\x82\x00\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\x83\x00\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x04DH\x84\x00\x00&', 54), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x00\x00\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x00\x01\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x00\x02\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x00\x03\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x00\x04\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x7f\xfb\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x7f\xfc\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x7f\xfd\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x7f\xfe\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x7f\xff\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91?\xfc\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91?\xfd\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91?\xfe\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91?\xff\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x01\x00\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x02\x00\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x03\x00\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b"\x08\x88\x91\x04\x00\x00'", 55), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\x00\x00\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\x00\x01\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\x00\x02\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\x00\x03\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\x00\x04\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\xff\xfb\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\xff\xfc\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\xff\xfd\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\xff\xfe\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\xff\xff\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\x7f\xfc\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\x7f\xfd\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\x7f\xfe\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\x7f\xff\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\x01\x00\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\x02\x00\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\x03\x00\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x11\x11"\x04\x00\x00(', 56), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x00\x00', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x00\x01', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x00\x02', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x00\x03', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x00\x04', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\xff\xfb', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\xff\xfc', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\xff\xfd', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\xff\xfe', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\xff\xff', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x7f\xfc', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x7f\xfd', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x7f\xfe', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x7f\xff', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x01\x00', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x02\x00', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x03\x00', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x04\x00', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x00\xaa\x00\x01\xc2\xe9', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x04\xaa\x00\x01\x16\x1d', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x08\xaa\x00\x01(\xee', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x0c\xaa\x00\x01v\x10', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x10\xaa\x00\x01\x1f\x89', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x14\xaa\x00\x01\xa6&', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x18\xaa\x00\x01\xf9o', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x1c\xaa\x00\x01\x9a\xe4', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00 \xaa\x00\x01\xd1\xa2', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00$\xaa\x00\x01M\xf0', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00(\xaa\x00\x01\xfe\x1e', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00,\xaa\x00\x01j\xf2', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x000\xaa\x00\x01\x8aH', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x004\xaa\x00\x01\x06[', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x008\xaa\x00\x01\xc0\x06', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00<\xaa\x00\x01\xa6;', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00@\xaa\x00\x01%c', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00D\xaa\x00\x01@\xa8', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00H\xaa\x00\x01\xfe*', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00L\xaa\x00\x01\x06\xdf', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00P\xaa\x00\x01\x07G', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00T\xaa\x00\x01\xb5\x16', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00X\xaa\x00\x01\xe1\x87', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\\\xaa\x00\x01?\xdd', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00`\xaa\x00\x012\x80', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00d\xaa\x00\x01l\xb2', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00h\xaa\x00\x01S\xfc', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00l\xaa\x00\x01\xd1J', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00p\xaa\x00\x01d\x12', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00t\xaa\x00\x01\xe3\xe6', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00x\xaa\x00\x01\xdf\x00', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00|\xaa\x00\x01i\xd7', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x80\xaa\x00\x01\xef\xeb', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x84\xaa\x00\x01\xc1\xce', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x88\xaa\x00\x01\x1e\xdb', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x8c\xaa\x00\x01\x0e\x87', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x90\xaa\x00\x01\xab7', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x94\xaa\x00\x01\xe9(', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x98\xaa\x00\x01F\x1e', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\x9c\xaa\x00\x01\x16}', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xa0\xaa\x00\x01%\xd6', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xa4\xaa\x00\x01]\xfd', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xa8\xaa\x00\x01\x151', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b"\x00\xac\xaa\x00\x01\xea'", 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xb0\xaa\x00\x01:\xdc', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xb4\xaa\x00\x01\xf5\xba', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xb8\xaa\x00\x01\x9e\xec', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xbc\xaa\x00\x013\xb0', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xc0\xaa\x00\x01\x9f\xa3', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xc4\xaa\x00\x01q\x1f', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xc8\xaa\x00\x01\xcaa', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xcc\xaa\x00\x01d\xc1', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xd0\xaa\x00\x01U\x14', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xd4\xaa\x00\x01<\xef', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xd8\xaa\x00\x01\x158', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xdc\xaa\x00\x01\x82\xc2', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xe0\xaa\x00\x018!', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xe4\xaa\x00\x01\xd9S', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xe8\xaa\x00\x01\x9fe', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xec\xaa\x00\x01\xec\x1d', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xf0\xaa\x00\x01\x1cH', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xf4\xaa\x00\x01\xd7\xbb', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xf8\xaa\x00\x01\xee[', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x00\xfc\xaa\x00\x01B`', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x00\xaa\x00\x01\xc3q', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x04\xaa\x00\x01\xae\x1c', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x08\xaa\x00\x01\xe6I', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x0c\xaa\x00\x01U=', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x10\xaa\x00\x01\x01\xec', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x14\xaa\x00\x01\xd3\xce', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x18\xaa\x00\x01j\x15', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x1c\xaa\x00\x01\xd1v', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01 \xaa\x00\x01\xdf\x8b', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01$\xaa\x00\x01\x14\x1a', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01(\xaa\x00\x01\xc7\x8e', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b"\x01,\xaa\x00\x01\xda'", 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x010\xaa\x00\x01\x9a\xc6', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x014\xaa\x00\x01\xdd\x18', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x018\xaa\x00\x01%A', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01<\xaa\x00\x01\xa5\x86', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01@\xaa\x00\x01\x10\xd3', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01D\xaa\x00\x01XE', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01H\xaa\x00\x01\x99\x07', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01L\xaa\x00\x013\x89', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01P\xaa\x00\x01\xd2\x8f', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01T\xaa\x00\x01A\xc1', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01X\xaa\x00\x01\xfa\xec', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\\\xaa\x00\x01@\x17', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01`\xaa\x00\x01\xfb[', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01d\xaa\x00\x01P\xbe', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01h\xaa\x00\x01\xcf\x89', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01l\xaa\x00\x01pg', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01p\xaa\x00\x019\x12', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01t\xaa\x00\x01\nT', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01x\xaa\x00\x01~g', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01|\xaa\x00\x01n\xc0', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x80\xaa\x00\x01\xd9\x9a', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x84\xaa\x00\x01q\x8a', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x88\xaa\x00\x01\xe9\xde', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x8c\xaa\x00\x01\xb6\xcb', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x90\xaa\x00\x01\xd7\xfd', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x94\xaa\x00\x01\x9b\xcf', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x98\xaa\x00\x01$\x8e', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\x9c\xaa\x00\x01\x0e\x9e', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xa0\xaa\x00\x01\xbf\xca', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xa4\xaa\x00\x01\xd5\xe7', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xa8\xaa\x00\x01A\x02', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xac\xaa\x00\x01\xd5\x96', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xb0\xaa\x00\x01\xfdf', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xb4\xaa\x00\x01S\x9a', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xb8\xaa\x00\x01O\x87', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xbc\xaa\x00\x01XM', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xc0\xaa\x00\x01v\xd3', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xc4\xaa\x00\x01ki', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xc8\xaa\x00\x01\xcd\x85', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xcc\xaa\x00\x01\xff~', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xd0\xaa\x00\x01x\x12', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xd4\xaa\x00\x01g\xa6', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xd8\xaa\x00\x01\x170', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xdc\xaa\x00\x01\xf4\xc7', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xe0\xaa\x00\x01\x85\xd4', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xe4\xaa\x00\x01\xf7\xde', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xe8\xaa\x00\x01\xd4\xee', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xec\xaa\x00\x01c\xd3', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xf0\xaa\x00\x01w\xd4', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xf4\xaa\x00\x01%\x91', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xf8\xaa\x00\x01\xdbg', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x01\xfc\xaa\x00\x01\x1a\xd4', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x00\xaa\x00\x01t\xc5', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x04\xaa\x00\x01\xfbw', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x08\xaa\x00\x01\xea\x92', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x0c\xaa\x00\x01\xc5d', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x10\xaa\x00\x01\x14#', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x14\xaa\x00\x01\x95N', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x18\xaa\x00\x01\xeb\xb9', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x1c\xaa\x00\x01\x97\x83', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02 \xaa\x00\x015\x95', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02$\xaa\x00\x01\x1fV', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02(\xaa\x00\x01T\x81', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02,\xaa\x00\x01M\x03', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x020\xaa\x00\x01y\x02', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x024\xaa\x00\x01\x80\xcd', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x028\xaa\x00\x015d', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02<\xaa\x00\x01\xff\xcf', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02@\xaa\x00\x01\x08O', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02D\xaa\x00\x01\x85V', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02H\xaa\x00\x01$H', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02L\xaa\x00\x01g\x90', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02P\xaa\x00\x01\tR', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02T\xaa\x00\x01\xae\xb4', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02X\xaa\x00\x01\xabY', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\\\xaa\x00\x01b\x17', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02`\xaa\x00\x01\xd4\xf2', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02d\xaa\x00\x01di', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02h\xaa\x00\x01\xce+', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02l\xaa\x00\x01\x90\xa6', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02p\xaa\x00\x01\x89\x07', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02t\xaa\x00\x01\x11\xee', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02x\xaa\x00\x01\x9e\xbe', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02|\xaa\x00\x01X\xf0', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x80\xaa\x00\x01h\x0e', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x84\xaa\x00\x01H\x1a', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x88\xaa\x00\x01\xfb\xc8', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x8c\xaa\x00\x01\xa4A', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x90\xaa\x00\x01\x0f7', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x94\xaa\x00\x01$?', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x98\xaa\x00\x01+\x18', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\x9c\xaa\x00\x01\ny', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xa0\xaa\x00\x01\xd2\x85', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xa4\xaa\x00\x01\xd0\xfb', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xa8\xaa\x00\x01\xdbh', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xac\xaa\x00\x01D\xd1', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xb0\xaa\x00\x01\x91\xe4', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xb4\xaa\x00\x01\x1a\x90', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xb8\xaa\x00\x01\x81\x12', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xbc\xaa\x00\x01\n\x94', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xc0\xaa\x00\x01\xe0\xea', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xc4\xaa\x00\x01,C', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xc8\xaa\x00\x01\xd5t', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xcc\xaa\x00\x01\xb6\x12', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xd0\xaa\x00\x01-\x0c', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xd4\xaa\x00\x01C\xe5', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xd8\xaa\x00\x01\x0e\xe8', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xdc\xaa\x00\x01U2', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xe0\xaa\x00\x010\xba', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xe4\xaa\x00\x01\xf2>', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xe8\xaa\x00\x01\xfc6', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xec\xaa\x00\x01\x1b.', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xf0\xaa\x00\x01S,', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xf4\xaa\x00\x01\x82\xce', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xf8\xaa\x00\x01\x1ea', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x02\xfc\xaa\x00\x01\xe6;', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x00\xaa\x00\x01"\x86', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x04\xaa\x00\x01\x97L', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x08\xaa\x00\x01G\xa9', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x0c\xaa\x00\x01\x9e\x1a', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b"\x03\x10\xaa\x00\x01\xb4'", 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x14\xaa\x00\x01\x16\xbc', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x18\xaa\x00\x01Y\xf5', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x1c\xaa\x00\x01^\xdf', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03 \xaa\x00\x01fl', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03$\xaa\x00\x01YA', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03(\xaa\x00\x01\xd5\xf4', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03,\xaa\x00\x01\x83(', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x030\xaa\x00\x01\x84\xc6', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x034\xaa\x00\x01y\xa0', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x038\xaa\x00\x01\x06\x93', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03<\xaa\x00\x01\x99:', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03@\xaa\x00\x01\xabT', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03D\xaa\x00\x01\xd9\xf0', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03H\xaa\x00\x01d\xdd', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03L\xaa\x00\x01\xfd~', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03P\xaa\x00\x01\x10\x7f', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03T\xaa\x00\x01qd', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03X\xaa\x00\x01\xf9\xed', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\\\xaa\x00\x01\x9a\x13', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03`\xaa\x00\x01p}', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03d\xaa\x00\x01`+', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03h\xaa\x00\x01.Q', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03l\xaa\x00\x01\x9f\xab', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03p\xaa\x00\x01.\\', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03t\xaa\x00\x01\x8d\xaf', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03x\xaa\x00\x01\xaf\xcd', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03|\xaa\x00\x01\xcby', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x80\xaa\x00\x01\x19H', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x84\xaa\x00\x01V\x86', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x88\xaa\x00\x01J\xce', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x8c\xaa\x00\x01\xd6\x82', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x90\xaa\x00\x01\x89@', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x94\xaa\x00\x01\x9f#', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x98\xaa\x00\x01\xc7+', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\x9c\xaa\x00\x01Zr', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xa0\xaa\x00\x01\xdb\xf1', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xa4\xaa\x00\x01\x1b\x1b', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xa8\xaa\x00\x0103', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xac\xaa\x00\x01\xc6\x92', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xb0\xaa\x00\x01\xa3\x96', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xb4\xaa\x00\x01\xd4\xd6', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xb8\xaa\x00\x01\x1c\x1a', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xbc\xaa\x00\x01l<', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xc0\xaa\x00\x01;\x19', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xc4\xaa\x00\x01V\xf4', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xc8\xaa\x00\x01L\xd9', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xcc\xaa\x00\x01\x07 ', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xd0\xaa\x00\x01\xb6$', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xd4\xaa\x00\x01%~', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xd8\xaa\x00\x01\xd9\xc7', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xdc\xaa\x00\x01?\xe2', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xe0\xaa\x00\x01\xdf\x12', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xe4\xaa\x00\x01\xb1\xa8', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xe8\xaa\x00\x01P\x10', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xec\xaa\x00\x01\x19\x8b', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xf0\xaa\x00\x01\r\xc8', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xf4\xaa\x00\x01.2', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xf8\xaa\x00\x01V\xab', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfc\xaa\x00\x018}', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfc\x00\x00\x01i{', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfc\x01\x00\x01\xc8\x98', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfc\x02\x00\x01\xe8,', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfc\x03\x00\x01\xf1\xf2', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfc\x04\x00\x01\xd2\xaa', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xff\xfb\x00\x01a\x93', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xff\xfc\x00\x01]\xf3', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xff\xfd\x00\x01\x9bE', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xff\xfe\x00\x01\xd9\x1b', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xff\xff\x00\x01\xe8R', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfd\xfc\x00\x01\xa1E', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfd\xfd\x00\x014\x1b', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfd\xfe\x00\x01\xac\xcd', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfd\xff\x00\x01.\xe0', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfd\x00\x00\x01\xb4d', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfe\x00\x00\x01)\x1d', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xff\x00\x00\x01\xbd\x08', 50), None,
                    Value(b'\x00""w3\x00!', 49), Value(b'\x03\xfc\x00\x00\x01i{', 50)]

        objects = [Field("test0", b"\x11\x11", fuzz="std"), Field("test1", b"\x22", fuzz="std"),
                   Field("test2", b"\x33\x33", slice(9, 17), fuzz="std"), Field("length", b"\x00\x00", fuzz="std")]
        functions = [length("length", "test0", "test2")]
        d0 = Dizz("test0", objects, functions, fuzz="std")

        objects = [Field("test0", b"\xff", fuzz="full"), Field("test1", b"\xaa", 10, fuzz="std"),
                   Field("test2", b"\x00\x00"), Field("checksum", b"\x00\x00")]
        functions = [checksum("checksum", "test0", "test2", "sha1")]
        d1 = Dizz("test1", objects, functions, fuzz="std")

        def inc(interaction_iterator, dizzy_iterator, response):
            i = int.from_bytes(dizzy_iterator["test2"].byte, "big") + 1
            dizzy_iterator["test2"] = i.to_bytes(2, "big")

        act = Interaction("Test", [d0, d1], {1: [inc]})
        self.assertEqual([i for i in act], expected)

    def test_length_std(self):
        objects = [Field("test0", b"\x11\x11", fuzz="std"), Field("test1", b"\x22", fuzz="std"),
                   Field("test2", b"\x33\x33", slice(9, 17), fuzz="std"), Field("length", b"\x00\x00", fuzz="std")]
        functions = [length("length", "test0", "test2")]
        d0 = Dizz("test0", objects, functions, fuzz="std")

        objects = [Field("test0", b"\xff", fuzz="full"), Field("test1", b"\xaa", 10, fuzz="std"),
                   Field("test2", b"\x00\x00"), Field("checksum", b"\x00\x00")]
        functions = [checksum("checksum", "test0", "test2", "sha1")]
        d1 = Dizz("test1", objects, functions, fuzz="std")

        objects = [Field("test0", b"\xff", fuzz="full"), Field("test1", b"\xaa", 10, fuzz="std"),
                   Field("test2", b"\x00\x00"), Field("checksum", b"\x00\x00")]
        functions = [checksum("checksum", "test0", "test2", "sha1")]
        d2 = Dizz("test2", objects, functions, fuzz="std")

        def inc(interaction_iterator, dizzy_iterator, response):
            i = int.from_bytes(dizzy_iterator["test2"].byte, "big") + 1
            dizzy_iterator["test2"] = Value(i.to_bytes(2, "big"))

        act = Interaction("Test", [d0, d1, d2], {1: [inc]}, fuzz="std")
        self.assertEqual(len([i for i in act]), act.length())

    def test_iterations_std(self):
        objects = [Field("test0", b"\x11\x11", fuzz="std"), Field("test1", b"\x22", fuzz="std"),
                   Field("test2", b"\x33\x33", slice(9, 17), fuzz="std"), Field("length", b"\x00\x00", fuzz="std")]
        functions = [length("length", "test0", "test2")]
        d0 = Dizz("test0", objects, functions, fuzz="std")

        objects = [Field("test0", b"\xff", fuzz="full"), Field("test1", b"\xaa", 10, fuzz="std"),
                   Field("test2", b"\x00\x00"), Field("checksum", b"\x00\x00")]
        functions = [checksum("checksum", "test0", "test2", "sha1")]
        d1 = Dizz("test1", objects, functions, fuzz="std")

        objects = [Field("test0", b"\xff", fuzz="full"), Field("test1", b"\xaa", 10, fuzz="std"),
                   Field("test2", b"\x00\x00"), Field("checksum", b"\x00\x00")]
        functions = [checksum("checksum", "test0", "test2", "sha1")]
        d2 = Dizz("test2", objects, functions, fuzz="std")

        def inc(_, dizzy_iterator, __):
            i = int.from_bytes(dizzy_iterator["test2"].byte, "big") + 1
            dizzy_iterator["test2"] = Value(i.to_bytes(2, "big"))

        act = Interaction("Test", [d0, d1, d2], {1: [inc]}, fuzz="std")

        iterations_1 = 1
        iterations_2 = 0
        for obj in act:
            if obj is None:
                iterations_1 += 1
            else:
                iterations_2 += 1

        self.assertEqual(iterations_1, act.iterations())
        self.assertEqual(iterations_2 // len(act.objects), act.iterations())

    def test_length_full(self):
        objects = [Field("test0", b"\x11\x11", fuzz="std"), Field("test1", b"\x22", fuzz="std"),
                   Field("test2", b"\x33\x33", slice(9, 17), fuzz="std"), Field("length", b"\x00\x00", fuzz="std")]
        functions = [length("length", "test0", "test2")]
        d0 = Dizz("test0", objects, functions, fuzz="std")

        objects = [Field("test0", b"\xff", fuzz="full"), Field("test1", b"\xaa", 10, fuzz="std"),
                   Field("test2", b"\x00\x00"), Field("checksum", b"\x00\x00")]
        functions = [checksum("checksum", "test0", "test2", "sha1")]
        d1 = Dizz("test1", objects, functions, fuzz="std")

        def inc(interaction_iterator, dizzy_iterator, response):
            i = int.from_bytes(dizzy_iterator["test2"].byte, "big") + 1
            dizzy_iterator["test2"] = Value(i.to_bytes(2, "big"))

        act = Interaction("Test", [d0, d1], {1: [inc]}, fuzz="full")
        self.assertEqual(len([i for i in act]), act.length())
    
    def test_iterations_full(self):
        objects = [Field("test0", b"\x11\x11", fuzz="std"), Field("test1", b"\x22", fuzz="std"),
                   Field("test2", b"\x33\x33", slice(9, 17), fuzz="std"), Field("length", b"\x00\x00", fuzz="std")]
        functions = [length("length", "test0", "test2")]
        d0 = Dizz("test0", objects, functions, fuzz="std")

        objects = [Field("test0", b"\xff", fuzz="full"), Field("test1", b"\xaa", 10, fuzz="std"),
                   Field("test2", b"\x00\x00"), Field("checksum", b"\x00\x00")]
        functions = [checksum("checksum", "test0", "test2", "sha1")]
        d1 = Dizz("test1", objects, functions, fuzz="std")

        def inc(_, dizzy_iterator, __):
            i = int.from_bytes(dizzy_iterator["test2"].byte, "big") + 1
            dizzy_iterator["test2"] = Value(i.to_bytes(2, "big"))

        act = Interaction("Test", [d0, d1], {1: [inc]}, fuzz="full")

        iterations_1 = 1
        iterations_2 = 0
        for obj in act:
            if obj is None:
                iterations_1 += 1
            else:
                iterations_2 += 1

        self.assertEqual(iterations_1, act.iterations())
        self.assertEqual(iterations_2 // len(act.objects), act.iterations())

    def test_start_at_std(self):
        objects = [Field("test0", b"\x11\x11", fuzz="std"), Field("test1", b"\x22", fuzz="std"),
                   Field("test2", b"\x33\x33", slice(9, 11), fuzz="std"), Field("length", b"\x00\x00")]
        functions = [length("length", "test0", "test2")]
        d0 = Dizz("test0", objects, functions, fuzz="std")

        objects = [Field("test0", b"\xff"), Field("test1", b"\xaa", 9, fuzz="std"), Field("test2", b"\x00\x00")]
        functions = list()
        d1 = Dizz("test1", objects, functions, fuzz="std")

        dizz_objects = [d0, d1]
        act = Interaction("Test", dizz_objects, {}, fuzz="std")
        excepted = list(act)
        for i in range(act.iterations()):
            got = list(Interaction("Test", dizz_objects, {}, fuzz="std", start_at=i))
            self.assertListEqual(excepted[(i * (len(dizz_objects) + 1)):], got)

    def test_start_at_full(self):
        objects = [Field("test0", b"\x11\x11", fuzz="std"), Field("test1", b"\x22", fuzz="std"),
                   Field("test2", b"\x33\x33", slice(9, 11), fuzz="std"), Field("length", b"\x00\x00")]
        functions = [length("length", "test0", "test2")]
        d0 = Dizz("test0", objects, functions, fuzz="std")

        objects = [Field("test0", b"\xff"), Field("test1", b"\xaa", 9, fuzz="std"), Field("test2", b"\x00\x00")]
        functions = list()
        d1 = Dizz("test1", objects, functions, fuzz="std")

        dizz_objects = [d0, d1]
        act = Interaction("Test", dizz_objects, {}, fuzz="full")
        excepted = list(act)
        for i in range(act.iterations()):
            got = list(Interaction("Test", [d0, d1], {}, fuzz="full", start_at=i))
            self.assertListEqual(excepted[(i * (len(dizz_objects) + 1)):], got)



if __name__ == '__main__':
    main()
