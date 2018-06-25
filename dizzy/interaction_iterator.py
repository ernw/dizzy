#       interaction_iterator.py
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
from dizzy.interaction_state import InteractionState
from dizzy import DizzyRuntimeException, DizzyParseException
from dizzy.log import print_dizzy
from dizzy.functions import POST

class InteractionIterator:
    def __init__(self, interaction):
        from dizzy.interaction import Interaction
        if not isinstance(interaction, Interaction):
            raise DizzyParseException('interaction must be Interaction object.')

        self.interaction = interaction
        self.state = []
        self.objects = {}
        for obj in interaction.objects:
            state = InteractionState(obj)
            if obj.name in self.objects:
                raise DizzyParseException("duplicate names: %s" % obj.name)
            else:
                self.objects.update({obj.name: state})
            self.state.append(state)

        self.current_iterator = enumerate(self.state)

        if self.interaction.fuzz == 'std':
            self.mutate = self.mutate_std
            for cur in self.state:
                cur.done = False
        elif self.interaction.fuzz == 'full':
            self.mutate = self.mutate_full
        else:
            self.mutate = self.mutate_none

        if interaction.start_at != 0:
            length = interaction.length()
            if length <= interaction.start_at:
                raise DizzyRuntimeException("start_at out of bounds: %s" % obj.name)

            if interaction.fuzz == 'std':
                self.start_at_std(interaction.start_at)
            elif interaction.fuzz == 'full':
                self.start_at_full(interaction.start_at)

    def __next__(self):
        try:
            # Get the next packet in the iteration
            self.index, self.current_object = next(self.current_iterator)
            # Call the act functions and then the dizz functions and return the current state of the packet
            return self.call_functions()
        except StopIteration:
            # The iteration is done
            # Set all packets to value before the dizz and act functions was called
            # This have to be done, because the act functions can change the value in all packets
            self.reset_packets()

            # Set the first object to the current object
            self.current_iterator = enumerate(self.state)

            # Mutate the next packet
            # The function behind self.mutate() depends on the fuzzing mode:
            # none: mutate_none()
            # std:  mutate_std()
            # full: mutate_full()
            # This function return always None to mark the next iteration
            return self.mutate()

    def mutate_std(self):
        # Mutate the next packet
        self.current_iterator = enumerate(self.state)
        for current in self.state:
            if not current.done:
                try:
                    # Found a packet to mutate, if next() is not raise a StopIteration
                    # next(current) call State.__next__() which call DizzIterator.__next__()
                    next(current)
                    # Return None to mark the next iteration
                    return None
                except StopIteration:
                    # current Dizz Object
                    current.done = True
        raise StopIteration

    def start_at_std(self, start_at):
        for state in self.state:
            obj_length = state.obj.length()

            if start_at < obj_length:
                state.obj.start_at = (state.obj.start_at + start_at) % obj_length
                state.iter = iter(state.obj)
                state.cur = next(state.iter)
                state.obj.start_at = 0
                break
            else:
                start_at -= obj_length - 1
                state.done = True

            if start_at == 0:
                break

    def mutate_full(self):
        # Mutate the next packet
        for current in self.state:
            try:
                # Found a packet to mutate, if next() is not raise a StopIteration
                # next(current) call State.__next__() which call DizzIterator.__next__()
                next(current)
                # Return None to mark the next iteration
                return None
            except StopIteration:
                pass
        raise StopIteration

    def start_at_full(self, start_at):
        for state in self.state:
            obj_length = state.obj.length()
            start_at, length = divmod(start_at, obj_length)

            if length > 0:
                state.obj.start_at = (state.obj.start_at + length) % obj_length
                state.iter = iter(state.obj)
                state.cur = next(state.iter)
                state.obj.start_at = 0

            if start_at == 0:
                break

    def mutate_none(self):
        raise StopIteration

    def __getitem__(self, item):
        return self.objects[item].iter

    def call_functions(self):
        if self.current_object is None:
            return None

        # Call the act functions
        if self.index in self.interaction.functions:
            # There is a function list to call
            for func in self.interaction.functions[self.index]:
                try:
                    func(self, self.current_object.iter, self.interaction.response)
                except Exception as e:
                    print_dizzy("%s: Exception in function" % self.interaction)
                    print_dizzy(e)

        # Call the dizz functions(for example to correct the length fields) and return the current state
        return self.current_object.call_functions(POST)

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise RuntimeError('Error')

        for c in self.state:
            if c.obj.name == key:
                c.cur = value
                return

        raise RuntimeError('Not found')

    def reset_packets(self):
        for a in self.state:
            a.reset()
