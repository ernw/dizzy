#       interaction.py
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

from . import InteractParseException, DizzyParseException
from dizzy.interaction_iterator import InteractionIterator
from dizzy.functions.call import call
from dizzy.dizz import load_dizz, null_dizz, Dizz
from dizzy.config import CONFIG
from dizzy.log import print_dizzy, DEBUG

def length_std(self):
    length = 0
    for obj in self.objects:
        length += obj.length()
    return (length - (len(self.objects) - 1)) * (len(self.objects) + 1) - 1

def iterations_std(self):
    iterations = 0
    for obj in self.objects:
        iterations += obj.length()
    return iterations - (len(self.objects) - 1)

def length_full(self):
    length = 1
    for obj in self.objects:
        length *= obj.length()
    return length * (len(self.objects) + 1) - 1

def iterations_full(self):
    iterations = 1
    for obj in self.objects:
        iterations *= obj.length()
    return iterations

def length_none(self):
    return len(self.objects)

def iterations_none(_):
    return 1

class Interaction(object):
    # TODO: start_object
    def __init__(self, name, objects=[], functions={}, fuzz='std', start_at=0):
        self.name = name
        self.objects = objects
        self.functions = functions
        self.fuzz = fuzz
        self.start_at = start_at
        self.response = b''

        if self.fuzz == 'std':
            self.len = length_std
            self.iter = iterations_std
        elif self.fuzz == 'full':
            self.len = length_full
            self.iter = iterations_full
        elif self.fuzz == "none":
            self.len = length_none
            self.iter = iterations_none
        else:
            raise DizzyParseException("fuzz mode is unknown.")

    def __repr__(self):
        return "Interaction '%s' %d objects, %d functions" % (self.name, len(self.objects), len(self.functions))

    def __iter__(self):
        return InteractionIterator(self)

    def length(self):
        return self.len(self)
        
    def iterations(self):
        return self.iter(self)
    
    def dump(self):
        return "Name: '%s'\nObjects: '[%s]'\nFunktions: '%s'\n" % (self.name, ", ".join(map(Dizz.dump, self.objects)), self.functions) 

def load_interaction(filename, fuzz="std", start_at=0, config_values={}):
    if exists(filename):
        with open(filename) as f:
            return parse_interaction(f.read(), filename, fuzz, start_at, config_values)
    else:
        if filename in CONFIG["ACT"]:
            return parse_interaction(CONFIG["ACT"][filename], filename, fuzz, start_at, config_values)

def parse_interaction(file, filename, fuzz="std", start_at=0, config_values={}):
    def not_impl(*args, **kwargs):
        raise InteractParseException("Not implemented")

    def load_dizz_conf(*args, **kwargs):
        if not 'config_values' in kwargs:
            kwargs['config_values'] = config_values
        return load_dizz(*args, **kwargs)
    def config_value(name):
        return config_values[name]

    ns = {"Dizzy": load_dizz_conf,
          "NullDizzy": null_dizz,
          "copy": not_impl,
          "call": call,
          "f": not_impl,
          "print_dizz": not_impl,
          "print_field": not_impl,
          "global": CONFIG["GLOBALS"]["INTERACTION_GLOBALS"],
          "get_session": lambda : CONFIG["GLOBALS"]["SESSION"],
          "config_value": config_value}

    exec(compile(file, filename, 'exec'), ns)
    act = Interaction(ns["name"], ns["objects"], ns["functions"], fuzz, start_at)
    print_dizzy("interaction/%s: '%s'." % (act.name, act.dump()), DEBUG)
    return act
