#       regex.py
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
from dizzy.value import Value
from dizzy.config import CONFIG
from dizzy import DizzyParseException

if CONFIG["DEPS"]["exrex"]:
    from exrex import generate, count

    class Regex:
        def __init__(self, name, regex, limit=20):
            if isinstance(name, str) and name:
                self.name = name
            else:
                raise DizzyParseException("Name must be str and not empty.")

            if isinstance(regex, str):
                self.regex = regex
            else:
                raise DizzyParseException("regex must be str.")

            if isinstance(limit, int):
                self.limit = limit
            else:
                raise DizzyParseException("limit must be int.")

            self.len = count(self.regex, self.limit)

        def __iter__(self):
            for string in generate(self.regex, self.limit):
                value = bytes(string, encoding=CONFIG["GLOBALS"]["CODEC"])
                yield Value(value, len(value) * 8)

        def length(self):
            return self.len
else:
    class Regex:
        def __init__(self, _1, _2, _3=None):
            raise DizzyParseException("python egrex module not available.")
