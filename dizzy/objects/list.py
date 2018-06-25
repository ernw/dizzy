#       list.py
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
from dizzy import DizzyParseException
from dizzy.config import CONFIG
from dizzy.value import Value

class List:
    def __init__(self, name, default=b'', path=CONFIG["GLOBALS"]["DEFAULT_STR_LIB"], encoding=CONFIG["GLOBALS"]["CODEC"], extra_encoding=None, extra_encoding_data=None):
        if isinstance(name, str) and name:
            self.name = name
        else:
            raise DizzyParseException("Name must be str and not empty.")

        self.default = default
        if isinstance(default, Value):
            self.list_ = [default]
        elif isinstance(default, str):
            self.list_ = [Value(default.encode(encoding))]
        else:
            self.list_ = [Value(default)]

        self.path = path
        self.flist_ = CONFIG["GLOBALS"]["GLOBAL_LIBRARY"].load_file(path)   #encoding?

        self.extra_encoding = extra_encoding
        self.extra_encoding_data = extra_encoding_data

    def __repr__(self):
        return "List(name=%s, default=%s, path=%s)" % (self.name, self.default, self.path)

    def __iter__(self):
        return iter(self.list_ + self.flist_)

    def length(self):
        return len(self.list_ + self.flist_)
