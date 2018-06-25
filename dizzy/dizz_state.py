#       dizz_state.py
#       
#       Copyright 2018 Daniel Mende <mail@c0decafe.de>
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

from types import GeneratorType
from dizzy.state import State

class DizzState(State):
    def __init__(self, obj):
        State.__init__(self, obj)

    def next(self):
        if isinstance(self.iter, GeneratorType):
            # Mutate
            self.bak = next(self.iter)
            self.cur = self.bak
        else:
            # Mutate the dizz object before the dizz functions is call
            self.bak = self.iter.mutate()
            # Call the dizz functions and return the current state
            self.cur = self.iter.call_functions()

    def is_dizz(self):
        return not isinstance(self.iter, GeneratorType)

    def reset(self):
        # To reset the state to the value before a function is call, it have to be checked
        # if the self.iter is DizzIterator (nested Dizz object).
        # If self.iter is DizzIterator, the fields of the dizz object have to be reset, too.
        if not isinstance(self.iter, GeneratorType):
            self.iter.reset()

        self.cur = self.bak
