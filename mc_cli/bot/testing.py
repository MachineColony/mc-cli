import os
import time
import requests
import subprocess
import BaseHTTPServer
from multiprocessing.pool import ThreadPool

request_data = None
ngrok_tunnels_url = 'http://localhost:4040/api/tunnels'


def _start_tunnel(port):
    """map a local port to a public url,
    to use as a webhook endpoint"""
    try:
        requests.get(ngrok_tunnels_url)

    # only start ngrok process if the endpoint is unavailable
    except requests.exceptions.ConnectionError:
        devnull = open(os.devnull, 'w')
        proc = subprocess.Popen(['ngrok', 'http', str(port)],
                                    stdout=devnull)
        proc.communicate()


def start_tunnel(port=8181, n_tries=5):
    pool = ThreadPool(processes=1)
    pool.apply_async(_start_tunnel, (port,))

    resp = None
    while n_tries and resp is None:
        try:
            resp = requests.get(ngrok_tunnels_url)
        except requests.exceptions.ConnectionError:
            n_tries -= 1
            time.sleep(1)
    if resp is None:
        raise requests.exceptions.ConnectTimeout
    tuns = resp.json()['tunnels']

    # grab the first, assuming it's the right one
    public_url = tuns[0]['public_url']

    return public_url


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

    def log_message(self, format, *args):
        # silence the handler
        return
