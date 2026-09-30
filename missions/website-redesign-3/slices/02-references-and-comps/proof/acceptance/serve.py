# static proof server for proof/comps: threaded, with a deep accept backlog (http.server's default of 5 resets
# connections when Chromium opens a page's subresources in parallel). Usage: python3 srv.py <port> <root>
import sys, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
class S(ThreadingHTTPServer):
    request_queue_size = 128
    daemon_threads = True
port, root = int(sys.argv[1]), sys.argv[2]
S(("127.0.0.1", port), functools.partial(SimpleHTTPRequestHandler, directory=root)).serve_forever()
