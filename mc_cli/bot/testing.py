import os
import requests
import subprocess
import BaseHTTPServer

request_data = None


def start_tunnel(port=8181):
    """map a local port to a public url,
    to use as a webhook endpoint"""
    devnull = open(os.devnull, 'w')
    proc = subprocess.Popen(['ngrok', 'http', str(port)],
                                  stdout=devnull)

    resp = requests.get('http://localhost:4040/api/tunnels')
    tuns = resp.json()['tunnels']

    # grab the first, assuming it's the right one
    public_url = tuns[0]['public_url']

    return public_url, proc


def await_hook(port):
    """setup a local server to receive a webhook request,
    returning the data from the first request"""

    server_address = ('', port)
    httpd = BaseHTTPServer.HTTPServer(server_address, TestRequestHandler)

    while request_data is None:
        httpd.handle_request()

    return request_data


class TestRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST(self):
        global request_data
        request_data = self.rfile.read(int(self.headers.getheader('Content-Length')))
        self.send_response(200)
        self.end_headers()
