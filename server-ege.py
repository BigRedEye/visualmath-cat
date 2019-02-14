from http.server import BaseHTTPRequestHandler, HTTPServer
import binascii
import http.cookies
import os
import socketserver as SocketServer
import sys
import time
import json
import random

from catsim.cat import generate_item_bank
from catsim.simulation import *
from catsim.initialization import *
from catsim.selection import *
from catsim.estimation import *
from catsim.stopping import *

import numpy as np
import math

HOST_NAME = '0.0.0.0'
PORT_NUMBER = 43210

sessions = {}
max_tasks = 10

with open('fipi/nice.json') as f:
    db = json.load(f)
print(f'Loaded db of size {len(db)}')

cat_db = generate_item_bank(len(db), '1PL')
for it in range(len(db)):
    percent = float(db[it]['solved']) / 100
    # http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.489.86&rep=rep1&type=pdf
    beta = math.log((1 - percent) / percent)
    cat_db[it][1] = beta

print(cat_db)

initializer = RandomInitializer()
# selector = AStratBBlockSelector(max_tasks)
selector = RandomesqueSelector(10)
estimator = HillClimbingEstimator()
stopper = MaxItemStopper(max_tasks)

def init_session():
    theta = initializer.initialize()
    task = selector.select(items=cat_db, administered_items=[], est_theta=theta)
    return {
        'items': [],
        'answers': [],
        'theta': theta,
        'task': task,
        'stop': False,
        'done': 0,
        'correct': 0,
    }

def next_step(session, answer):
    answer = answer.decode('utf-8').strip().replace('.', ',')
    ans = db[int(session['task'])]['answer'] == answer
    print("Got answer '{}', correct is '{}'".format(answer, db[int(session['task'])]['answer']))
    session['answers'].append(ans)
    session['items'].append(session['task'])
    answers = session['answers']
    items = session['items']
    est_theta = session['theta']
    new_theta = estimator.estimate(items=cat_db, administered_items=items, response_vector=answers, est_theta=est_theta)
    item_index = selector.select(items=cat_db, administered_items=items, est_theta=new_theta)
    session['theta'] = new_theta
    session['task'] = item_index
    session['stop'] = stopper.stop(administered_items=cat_db[items], theta=est_theta)
    session['done'] += 1
    if ans:
        session['correct'] += 1
    print("New theta: {}, items = {}, answers = {}".format(new_theta, items, answers))
    return session

def mark(session):
    return 10 - 10 / (1 + math.exp(session['theta']))

class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if self.path[-1] == '?':
            self.path = self.path[:-1]

        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/tasks')
            self.end_headers()
            return

        cookies = http.cookies.SimpleCookie(self.headers.get('Cookie'))
        sid = str(binascii.b2a_hex(os.urandom(16)))
        if 'session_id' in cookies:
            sid = str(cookies['session_id'].value)
        if sid not in sessions:
            sessions[sid] = init_session()

        paths = {
            '/tasks': {'status': 200, 'sid': sid},
        }

        check = lambda x : x in paths or x[-4:] == '.png'

        if check(self.path):
            self.respond({'status': 200, 'sid': sid})
        else:
            self.respond({'status': 404, 'sid': sid})

    def do_POST(self):
        print(self.headers['content-length'])
        body = self.rfile.read(int(self.headers['content-length']))
        ans = body[7:]

        cookie = http.cookies.SimpleCookie(self.headers.get('Cookie'))
        sid = str(cookie['session_id'].value)
        if sid in sessions:
            sessions[sid] = next_step(sessions[sid], ans)

        self.respond({'status': 200, 'sid': sid})

    def handle_http(self, status_code, path, sid):
        self.send_response(status_code)
        if status_code == 200 and self.path[-4:] == '.png':
            with open('fipi/tasks/' + self.path, 'rb') as f:
                content = bytes(f.read())
                self.end_headers()
                return content

        cookies = http.cookies.SimpleCookie(self.headers.get('Cookie'))
        content = f'''
        <html>
            <head>
                <title>
                    Status code = {status_code}
                </title>
            </head>
            <body>
                <p>Status code = {status_code}</p>
            </body>
        </html>
        '''
        if sid in sessions:
            if 'session_id' not in cookies:
                cookie = http.cookies.SimpleCookie()
                cookie['session_id'] = sid
                self.send_header("Set-Cookie", cookie.output(header='', sep=''))
            if status_code == 200:
                if self.path == '/tasks':
                    session = sessions[sid]
                    if session['stop']:
                        content = '''
                        <html>
                            <head>
                                <title>
                                    Test finished
                                </title>
                            </head>
                            <body>
                                <p>Test finished</p>
                                <p>Correct answers: {} / {}</p>
                                <p>Estimated mark: {}</p>
                                <form action="/tasks" method="get">
                                    <input type="submit" value="Restart">
                                </form>
                            </body>
                        </html>
                        '''.format(session['correct'], session['done'], mark(session))
                        cookie = http.cookies.SimpleCookie()
                        cookie['session_id'] = sid
                        cookie['session_id']['expires'] = 0
                        self.send_header("Set-Cookie", cookie.output(header='', sep=''))
                    else:
                        content = db[session['task']]['html']
        else:
            content = '''
            <html>
                <head>
                    <title>
                        Invalid session
                    </title>
                </head>
                <body>
                    <p>Invalid session</p>
                </body>
            </html>
            '''
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        return bytes(content, 'UTF-8')

    def respond(self, opts):
        response = self.handle_http(opts['status'], self.path, opts['sid'])
        self.wfile.write(response)


class ThreadedHTTPServer(SocketServer.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    server_class = HTTPServer
    httpd = ThreadedHTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)
    print(time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        while 1:
            sys.stdout.flush()
            httpd.handle_request()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER))
