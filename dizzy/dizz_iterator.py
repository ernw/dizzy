#       dizz_iterator.py
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
from dizzy import DizzyRuntimeException, DizzyParseException
from dizzy.value import Value
from dizzy.dizz_state import DizzState
from dizzy.objects import START, END
from dizzy.functions import PRE, BOTH
from dizzy.tools import endian_format
from dizzy.log import print_dizzy, DEBUG
from dizzy.encodings.encoding import apply_extra_encoding

class DizzIterator:
    def __init__(self, dizz):
        from dizzy.dizz import Dizz
        if not isinstance(dizz, Dizz):
            raise DizzyParseException('dizzy must be dizz object.')

        self.dizz = dizz

        self.state = []
        self.objects = {}
        self.encoded = False
        self.current_mutated_objects = set()
        for obj in dizz.objects:
            state = DizzState(obj)
            if obj.name == START or obj.name == END:
                raise DizzyParseException("name '%s' and '%s' are reserved." % (START, END))
            elif obj.name in self.objects:
                raise DizzyParseException("duplicate names: %s" % obj.name)
            else:
                self.objects.update({obj.name: state})
            self.state.append(state)

        if self.dizz.fuzz == 'std':
            for cur in self.state:
                cur.done = False

        if dizz.start_at != 0:
            length = dizz.length()
            if length <= dizz.start_at:
                raise DizzyRuntimeException("start_at out of bounds: %s" % obj.name)

            if dizz.fuzz == 'std':
                self.mutate = self.mutate_std
                self.start_at_std(dizz.start_at - 1)
            elif dizz.fuzz == 'full':
                self.mutate = self.mutate_full
                self.start_at_full(dizz.start_at - 1)
            else:
                raise Exception("Unknown fuzz mode")

    def reset(self):
        for a in self.state:
            a.reset()
        self.encoded = False

    # This function is called when the dizz object is iterated directly or the start_at != 0 for example:
    # for i in Dizz(..., fuzz="std"):
    #     print(i)
    #
    # When the dizz object is iterate through a act object see the function State.__next__() and State.next()
    def __next__(self):
        # Set to the value before the dizz or act functions was called
        # This have to be done, because a field which is not currently iterated
        # can be change by a the dizz function(and maybe act function)
        self.reset()
        # Mutate the dizz object
        # The function behind self.mutate() depends on the fuzzing mode after the first vale:
        # none: mutate_none()
        # std:  mutate_std()
        # full: mutate_full()
        self.mutate()
        # Call the dizz functions and return the current state
        return self.call_functions()

    def mutate(self):
        if self.dizz.fuzz == 'std':
            self.mutate = self.mutate_std
        elif self.dizz.fuzz == 'full':
            self.mutate = self.mutate_full
        else:
            self.mutate = self.mutate_none

        return self.get_current_state()

    def mutate_std(self):
        for current in self.state:
            if not current.done:
                try:
                    next(current)
                    self.current_mutated_objects.add(current.obj.name)
                    return self.get_current_state()
                except StopIteration:
                    current.done = True
                    self.current_mutated_objects.discard(current.obj.name)
        raise StopIteration

    def start_at_std(self, start_at):
        for state in self.state:
            length = state.obj.length()
            if start_at < length:
                i = 0
                while i < start_at:
                    next(state)
                    i += 1
                return
            else:
                start_at -= length - 1
                state.done = True

    def mutate_full(self):
        for current in self.state:
            try:
                next(current)
                self.current_mutated_objects.add(current.obj.name)
                return self.get_current_state()
            except StopIteration:
                pass

        raise StopIteration

    def start_at_full(self, start_at):
        for state in self.state:
            start_at, length = divmod(start_at, state.obj.length())

            i = 0
            while i < length:
                next(state)
                i += 1

            if start_at == 0:
                return

    def mutate_none(self):
        raise StopIteration

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.state[item].cur
        elif isinstance(item, str):
            if item == START:
                return self.state[0].cur
            elif item == END:
                return self.state[-1].cur
            return self.objects[item].cur
        elif isinstance(item, slice):
            if not isinstance(item.start, str) or not isinstance(item.stop, str):
                raise RuntimeError('Start and stop have to be str: %s' % self.name)
            if item.start == START:
                start = self.state[0].obj.name
            else:
                start = item.start
            if item.stop == END:
                stop = self.state[-1].obj.name
            else:
                stop = item.stop
            value = None
            found = False
            for cur in self.state:
                if not found:
                    if cur.obj.name == start:
                        found = True
                        value = cur.cur
                        if item.start == stop:
                            return value
                else:
                    value = value + cur.cur
                    if cur.obj.name == stop:
                        return value

            raise DizzyParseException("Not found: %s:%s" % (item.start, item.stop))
        raise RuntimeError('item have to be int, str or slice')

    def __setitem__(self, key, value):
        if isinstance(value, int):
            if not isinstance(key, str):
                raise RuntimeError('%s: error during assignment' % self) #Needz moar context
            current_object = self.objects[key]
            size = current_object.cur.size
            value = Value(value.to_bytes((size + 7) // 8, endian_format[current_object.obj.endian]), size) #Do Not Like
        elif not isinstance(value, Value):
            value = Value(value)

        if isinstance(key, str):
            if key == START:
                key = self.state[0].obj.name
            elif key == END:
                key = self.state[-1].obj.name
            self.objects[key].cur = value
        elif isinstance(key, slice):
            if not isinstance(key.start, str) or not isinstance(key.stop, str):
                raise RuntimeError('Start and stop have to be str: %s' % self.name)
            if key.start == START:
                start = self.state[0].obj.name
            else:
                start = key.start
            if key.stop == END:
                stop = self.state[-1].obj.name
            else:
                stop = key.stop
            found = False
            for cur in self.state:
                if not found:
                    if cur.obj.name == start:
                        found = True
                        cur.cur = value
                        if key.start == stop:
                            return
                else:
                    cur.cur = value
                    if cur.obj.name == stop:
                        return
            if found:
                raise DizzyParseException("Not found: %s" % (key.stop))
            else:
                raise DizzyParseException("Not found: %s:%s" % (key.start, key.stop))
        else:
            raise RuntimeError('key has to be str or slice')

    def get_current_state(self):
        result = Value()

        if not self.encoded:
            apply_extra_encoding(self.state)
            self.encoded = True

        for a in self.state:
            if not isinstance(a.cur, Value):
                raise RuntimeError('Panic: cur has to be Value: %s' % self.dizz)
            result = result + a.cur

        return StructuredValue(result, self)

    def call_functions(self, when=PRE):
        # Call the functions of the objects, if it is a dizz object(nested dizz)
        for a in self.state:
            if a.is_dizz():
                a.call_functions(when)

        # Call the functions
        for (func, call_at) in self.dizz.functions:
            if call_at == when or call_at == BOTH:
                try:
                    func(self)
                except Exception as e:
                    print_dizzy("%s: Exception in function: %s" % (self.dizz, e))
        return self.get_current_state()


class StructuredValue(Value):
    def __init__(self, value, dizz_iterator):
        self.byte = value.byte
        self.size = value.size
        self.dizz_iterator = dizz_iterator

    def __setitem__(self, key, value):
        self.dizz_iterator[key] = value
        value = self.dizz_iterator.get_current_state()
        self.byte = value.byte
        self.size = value.size

    def __getitem__(self, item):
        return self.dizz_iterator[item]
