from dizzy.interaction import Interaction
from dizzy.objects.field import Field
from dizzy.functions.length import length
from dizzy.dizz import Dizz, load_dizz
from dizzy.tests import first
from dizzy.functions.padding import padding
from dizzy.functions.run_cmd import run_cmd
from dizzy.functions.checksum import checksum
from dizzy.value import Value
from dizzy.objects.list import List
from dizzy.log import print_dizzy, DEBUG, VERBOSE_2, VERBOSE_1, NORMAL, REDUCE, NONE, print_level, set_print_level
from timeit import timeit
from binascii import hexlify

#print(timeit("print_dizzy('TEST', )", "from dizzy.log import print_dizzy, NORMAL", number=100000))

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


act = Interaction("Test", [d0, d1], {1: [inc]})



for i in List("List"):
    print(i)


"""

def checksum_inet(target, start, stop):
    def func(dizzy_iterator):
        dizzy_iterator[""]
        dizzy_iterator["NAME"]["ELEE"] = b"TTTTTT"

    return func

objects = [Field("test0", b"\x11\x11", fuzz="std"), Field("test1", b"\x22", fuzz="std"),
           Field("test2", b"\x33\x33", slice(9, 17), fuzz="std"), Field("length", b"\x00\x00", fuzz="std"),
           Field("padding"), "dizzes/bgp/keepalive.dizz", Dizzy("NAME", "PFAD")]
functions = [length("length", "test0", "test2"), padding("padding", "test0", "length", 8),]
d0 = Dizzy("test0", objects, functions, fuzz="std", start_at=0)

for i in d0:
    print(i)

run_cmd('echo "AAA"')
objects = [Field("test0", b"\xff", fuzz="full"), Field("test1", b"\xaa", 10, fuzz="std"),
           Field("test2", b"\x00\x00"), Field("checksum", b"\x00\x00")]
functions = [checksum("checksum", "test0", "test2", "sha1")]
d1 = Dizzy("test1", objects, functions, fuzz="std")

def inc(interaction_iterator, dizzy_iterator, response):
    i = int.from_bytes(dizzy_iterator["test2"].byte, "big") + 1
    dizzy_iterator["test2"] = Value(i.to_bytes(2, "big"))


for x in Interaction("Test", [d0, d1], {1: [inc]}):
    print(x)


for i in List("WWW"):
    print(i)
    
"""
