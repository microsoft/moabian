#!/usr/bin/env python3

import os
port = int(os.getenv('PORT', 8000))

from http.server import HTTPServer, SimpleHTTPRequestHandler

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    print(f"Listening on {port}")
    server_address = ("0.0.0.0", port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    run()
