#       der.py
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
from dizzy import DizzyRuntimeException
from dizzy.value import Value
from struct import pack

class Tree(object):
    def __init__(self, up, data):
        self.up = up
        self.down = []
        self.data = data

    def __repr__(self):
        return "%s: Data: %s Up: %s Down: %s" % (id(self), self.data.obj.name, id(self.up), [ i.data.obj.name for i in self.down ])

def encode(dizz_state):
    tree = None
    cur_depth = 0
    cur_node = None

    for obj in dizz_state:
        enc = obj.obj.extra_encoding
        if enc is "DER":
            (_, depth) = obj.obj.extra_encoding_data
            if tree is None:
                if not depth is 0:
                    raise DizzyRuntimeException("DER encoding: First element needs depth 0.")
                else:
                    tree = Tree(None, obj)
                    cur_node = tree
            else:
                if depth is cur_depth + 1:
                    new_node = Tree(cur_node, obj)
                    cur_node.down.append(new_node)
                    cur_node = new_node
                    cur_depth = depth
                elif depth > cur_depth:
                    raise DizzyRuntimeException("DER encoding: Can only increment depth by one.")
                elif depth is cur_depth:
                    new_node = Tree(cur_node.up, obj)
                    cur_node.up.down.append(new_node)
                    cur_node = new_node
                else:
                    lam = cur_depth - depth
                    #print(cur_depth, lam)
                    for _ in range(lam):
                        #print (".")
                        if not cur_node.up is None:
                            #print (",")
                            cur_node = cur_node.up
                    #print(cur_node)
                    new_node = Tree(cur_node.up, obj)
                    cur_node.up.down.append(new_node)
                    cur_node = new_node
                    cur_depth = depth

    from pprint import pprint
    #pprint(tree)

    return enc_tree(tree)

def calc_len(node):
    length = len(node.data.cur.byte)
    for i in node.down:
        length += calc_len(i)
    return length

def enc_tree(node):
    for i in node.down:
        enc_tree(i)
    (tag, _) = node.data.obj.extra_encoding_data
    length = calc_len(node)
    if length < 128:
        len_octets = length.to_bytes(1, byteorder='big')
    else:
        len_bytes = length.bit_length() // 8
        if length.bit_length() % 8 > 0:
            len_bytes += 1
        len_octets = (0x80 | len_bytes).to_bytes(1, byteorder='big') + length.to_bytes(len_bytes, byteorder='big')
    #print("tag: %s len: %s, len_octets: %s" % (tag.hex(), length, len_octets.hex()))
    #print("old_cur: %s" % node.data.cur.byte.hex())
    new_cur = Value(tag) + Value(len_octets) + node.data.cur
    #print("new_cur: %s" % new_cur.byte.hex())
    node.data.cur = new_cur
