#       dizz.py
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
from os.path import exists
import string
from random import choice

from dizzy.functions.length import length_string_bytes, length, length_bytes, length_lambda, length_lambda2
from dizzy.functions.link import link
from dizzy.functions.rand import rand
from dizzy.functions.checksum import checksum
from dizzy.functions.run_cmd import run_cmd
from dizzy.functions.padding import padding, padding_zero, padding_pkcs7, padding_ansi_x923, padding_iso_10126, \
    padding_iso_iec_7816_4
from dizzy.functions.time import time, time_no_fracs
from dizzy.objects.regex import Regex
from dizzy.objects.field import Field
from dizzy.objects.list import List
from dizzy.objects.rand import Rand
from . import DizzyParseException
from dizzy.dizz_iterator import DizzIterator
from dizzy.config import CONFIG

def length_std(self):
    iter_length = 0
    for obj in self.objects:
        iter_length += obj.length()
    return iter_length - (len(self.objects) - 1)

def length_full(self):
    iter_length = 1
    for obj in self.objects:
        iter_length *= obj.length()
    return iter_length

def length_none(self):
    return 1

class Dizz:
    def __init__(self, name, objects=[], functions=[], readback=0, fuzz='full', start_at=0, extra_encoding=None, extra_encoding_data=None):
        self.name = name
        self.readback = readback
        self.start_at = start_at

        self.objects = []
        self.functions = []
        allchar = string.ascii_letters + string.punctuation + string.digits

        for obj in objects:
            if isinstance(obj, str):
                name = "".join(choice(allchar) for x in range(12))
                self.objects.append(Field(name, obj, fuzz='none'))
                #data = include_dizz(obj)
                #self.objects += data["objects"]
                #self.functions += data["functions"]
            else:
                self.objects.append(obj)
        self.functions += functions

        self.fuzz = fuzz
        if self.fuzz == 'std':
            self.len = length_std
        elif self.fuzz == 'full':
            self.len = length_full
        elif self.fuzz == "none":
            self.len = length_none
        else:
            raise DizzyParseException("fuzz mode is unknown.")
        
        self.extra_encoding = extra_encoding
        self.extra_encoding_data = extra_encoding_data

    def __repr__(self):
        return "Dizz '%s' %d objects, %d functions" % (self.name, len(self.objects), len(self.functions))

    def __iter__(self):
        return DizzIterator(self)

    def length(self):
        return self.len(self)
    
    def dump(self):
        return "Name: '%s'\nObjects: '%s'\nFunctions: '%s'\n" % (self.name, self.objects, self.functions)

def include_dizz(filename, config_values):
    if exists(filename):
        with open(filename) as f:
            return parse_dizz(f.read(), filename, config_values)
    else:
        if filename in CONFIG["DIZZ"]:
            return parse_dizz(CONFIG["DIZZ"][filename], filename, config_values)
        else:
            raise DizzyParseException("cannot find dizz %s" % filename)

def parse_dizz(file, filename, config_values):
    class FilterFormatDict(dict):
        def __init__(self):
            self.format = 1
        def __getitem__(self, item):
            if item == "format":
                return self.format
            def noFunc(*args, **kwargs):
                pass
            return noFunc
        def __setitem__(self, key, value):
            if key == "format":
                self.format = value

    namespace = FilterFormatDict()
    exec(compile(file, filename, 'exec'), namespace)
    if namespace["format"] == 2:
        return parse_dizz_v2(file, filename, config_values)
    elif namespace["format"] == 1:
        return parse_dizz_v1(file, filename, config_values)
    else:
        raise DizzyParseException("Dizzfile format '%s' unknown!" % namespace["format"])

def parse_dizz_v2(file, filename, config_values):
    #def not_impl(*args, **kwargs):
    #    raise DizzyParseException("Not implemented")
    def config_value(name):
        return config_values[name]

    namespace = {"Field":           Field,
                 "Regex":           Regex,
                 "List":            List,
                 "Rand":            Rand,
                 "config_value":    config_value,
                 "rand":            rand,
                 "link":            link,
                 "padding":         padding,
                 "padding_zero":    padding_zero,
                 "padding_pkcs7":   padding_pkcs7,
                 "padding_ansi_x923": padding_ansi_x923,
                 "padding_iso_10126": padding_iso_10126,
                 "padding_iso_iec_7816_4": padding_iso_iec_7816_4,
                 "run_cmd":         run_cmd,
                 "time":            time,
                 "time_no_fracs":   time_no_fracs,
                 "length":          length,
                 "length_bytes":    length_bytes,
                 "length_string_bytes": length_string_bytes,
                 "length_lambda":   length_lambda,
                 "length_lambda2":  length_lambda2,
                 "checksum":        checksum,
                 "none":            "none",
                 "std":             "std",
                 "full":            "full",
                 }
    exec(compile(file, filename, 'exec'), namespace)

    return {"name": namespace["name"], "objects": namespace["objects"], "functions": namespace["functions"]}

def parse_dizz_v1(file, filename, config_values):
    #def not_impl(*args, **kwargs):
    #    raise DizzyParseException("Not implemented")
    def config_value(name):
        return config_values[name]

    def field(name, length, default, fuzz, endian='!', encoding=CONFIG["GLOBALS"]["CODEC"]):
        if length == None:
            return List(name, default, CONFIG["GLOBALS"]["DEFAULT_STR_LIB"], encoding)
        else:
            return Field(name, default, length, fuzz, endian, encoding)

    def list(name, default, listname, ascii=True):
        if ascii:
            encoding = "ascii"
        else:
            encoding = CONFIG["GLOBALS"]["CODEC"]
        return List(name, default, listname, encoding)

    def ascii_length(dest, start, end, _endian="!"):
        return length_string_bytes(dest, start, end, "ascii")

    class Link_class:
        def __init__(self, name, source):
            self.name = name
            self.source = source

    class Padding_class:
        def __init__(self, name, start, stop, modulo, pattern):
            self.name = name
            self.start = start
            self.stop = stop
            self.modulo = modulo
            self.pattern = pattern

    class Rand_class:
        def __init__(self, name, size, encoding):
            self.name = name
            self.size = size


    namespace = {"field":       field,
                 "list":        list,
                 "rand":        Rand_class,
                 "link":        Link_class,
                 "fill":        Padding_class,
                 "padding":     Padding_class,

                 "none":        "none",
                 "std":         "std",
                 "full":        "full",

                 "run_cmd":         run_cmd,
                 "time":            time,
                 "time_no_fracs":   time_no_fracs,
                 "length":          length,
                 "ascii_length":    ascii_length,
                 "lambda_length":   length_lambda,
                 "csum":            checksum,
                 "lambda_csum":     length_lambda,
                 "lambda2_csum":    length_lambda2,
                 }
    exec(compile(file, filename, 'exec'), namespace)

    new_functions = []

    def convert(i):
        if isinstance(i, Link_class):
            new_functions.append(link(i.source, i.name))
            return Field(i.name)
        elif isinstance(i, Padding_class):
            new_functions.append(padding(i.name, i.start, i.stop, i.modulo, i.pattern))
            return Field(i.name)
        elif isinstance(i, Rand_class):
            new_functions.append(rand(i.name))
            return Field(i.name, i.size)
        return i

    namespace["objects"] = list(map(convert, namespace["objects"]))
    namespace["functions"] = new_functions + namespace["functions"]

    return {"name": namespace["name"], "objects": namespace["objects"], "functions": namespace["functions"]}

def load_dizz(name, filename, readback=0, fuzz="std", start_at=0, config_values={}):
    data = include_dizz(filename, config_values)
    return Dizz(name, data["objects"], data["functions"], readback, fuzz, start_at)

def null_dizz(name):
    return Dizz(name, fuzz="none")
