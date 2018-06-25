#       http.py
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
#       THEORY OF LIABILITY, frWHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#       OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from . import SessionException, SessionParseException
from http.client import HTTPConnection
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread, Lock
from time import sleep
from dizzy.log import print_dizzy, DEBUG, VERBOSE_1, VERBOSE_2

class DizzyHTTPServerThread(Thread):
    def __init__(self, server):
        Thread.__init__(self)
        self.server = server

    def run(self):
        self.server.serve_forever()

class DizzySession(object):
    def __init__(self, section_proxy):
        self.dest = section_proxy.get('target_host')
        self.dport = section_proxy.getint('target_port', 80)
        self.src = section_proxy.get('source_host', '')
        self.src_str = self.src
        if self.src == '':
            self.src = None
        self.sport = section_proxy.getint('source_port', 80)
        self.method = section_proxy.get('method', 'GET')
        self.url = section_proxy.get('url')
        self.headers = {}
        headers = section_proxy.get('headers', '')
        if not headers == '':
            for l in headers.split(";"):
                r = l.split(":")
                self.headers[r[0]] = ":".join(r[1:])
        self.cookies = {}
        self.timeout = section_proxy.getfloat('timeout', 1)
        self.auto_reopen = section_proxy.getboolean('auto_reopen', True)
        self.retry = section_proxy.getint('retry', 3)
        self.server_side = section_proxy.getboolean('server', False)
        self.read_first = self.server_side
        self.read_first = section_proxy.getboolean('read_first', self.read_first)
        self.is_open = False
        self.res = None
        self.thread = None
        self.send_lock = Lock()
        self.recv_lock = Lock()
        self.rlist = []
        self.slist = []

        class DizzyHTTPRequestHandler(BaseHTTPRequestHandler):
            dest = self.dest
            dport = self.dport
            send_lock = self.send_lock
            recv_lock = self.recv_lock
            rlist = self.rlist
            slist = self.slist
            set_headers = self.headers
            protocol_version = "HTTP/1.1"

            def all_methods(self):
                (addr, port) = self.client_address
                if addr == self.dest:
                    print_dizzy("http/request_handler: handling request from %s" % addr, VERBOSE_2)
                    while True and not self.server._BaseServer__shutdown_request:
                        with self.recv_lock:
                            if len(self.rlist) == 0:
                                break
                        print_dizzy("http/request_handler: rlist not empty", DEBUG)
                        sleep(0.1)
                    with self.recv_lock:
                        length = int(self.headers['content-length'])
                        self.rlist.append(self.rfile.read(length))
                    while True and not self.server._BaseServer__shutdown_request:
                        with self.send_lock:
                            if len(self.slist) == 1:
                                break
                        print_dizzy("http/request_handler: slist empty", DEBUG)
                        sleep(0.1)
                    with self.send_lock:
                        data = self.slist.pop()
                        self.send_response(200)
                        for i in self.set_headers:
                            self.send_header(i, self.set_headers[i])
                        self.send_header('Content-Length', len(data))
                        self.end_headers()
                        self.wfile.write(data)
                else:
                    print_dizzy("http/request_handler: denied access for %s" % addr, VERBOSE_2)

            def log_message(self, format, *args):
                return

            do_GET = all_methods
            do_HEAD = all_methods
            do_POST = all_methods
            do_PUT = all_methods
            do_DELETE = all_methods
            do_CONNECT = all_methods
            do_OPTIONS = all_methods
            do_TRACE = all_methods
            do_PATCH = all_methods

        self.request_handler = DizzyHTTPRequestHandler

    def open(self):
        try:
            if not self.server_side:
                self.connection = HTTPConnection(self.dest, self.dport, timeout=self.timeout, source_address=self.src)
            else:
                attempt = 0
                while attempt < self.retry:
                    try:
                        self.connection = HTTPServer((self.src_str, self.sport), self.request_handler)
                    except OSError:
                        attempt += 1
                        sleep(1)
                        continue
                    else:
                        break

                self.thread = DizzyHTTPServerThread(self.connection)
                self.thread.start()
        except Exception as e:
            raise SessionException("http/open: cant open session: %s" % e)
        else:
            self.is_open = True

    def close(self):
        if not self.is_open:
            return
        if not self.server_side:
            self.connection.close()
            self.res = None
        else:
            self.connection.shutdown()
        self.is_open = False

    def send(self, data):
        try:
            if not self.server_side:
                headers = self.headers
                cookies = ";".join(["%s=%s" % (n, v) for (n, v) in self.cookies.items()])
                if len(cookies) > 0:
                    headers.update({"Cookie" : cookies})
                self.connection.request(self.method, self.url, body=data, headers=headers)
                self.res = self.connection.getresponse()
                headers = dict(self.res.getheaders())
                for h in headers:
                    if h == "Set-Cookie":
                        try:
                            nv = headers[h].split(";")[0].split("=")
                            self.cookies[nv[0]] = nv[1]
                        except:
                            print_dizzy("http/send: failed to parse set-cookie: %s" % headers[h], VERBOSE_1)
            else:
                while True:
                    with self.send_lock:
                        if len(self.slist) == 0:
                            break
                    print_dizzy("http/send: slist not empty", DEBUG)
                    sleep(0.1)
                with self.send_lock:
                    self.slist.append(data)
                    print_dizzy("http/send: pushed %s" % data, DEBUG)
        except Exception as e:
            if self.auto_reopen:
                print_dizzy("http/send: session got closed '%s', auto reopening..." % e, DEBUG)
                print_dizzy(e, DEBUG)
                self.close()
                self.open()
            else:
                self.close()
                raise SessionException("http/send: error on sending '%s', connection closed." % e)

    def recv(self):
        #from traceback import print_stack
        #print_stack()

        if not self.server_side:
            if not self.res is None:
                return self.res.read()
        else:
            while True:
                with self.recv_lock:
                    if len(self.rlist) == 1:
                        break
                print_dizzy("http/recv: rlist empty", DEBUG)
                sleep(0.1)
            with self.recv_lock:
                data = self.rlist.pop()
                print_dizzy("http/recv: poped %s" % data, DEBUG)
                return data
