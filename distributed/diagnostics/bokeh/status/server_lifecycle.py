#!/usr/bin/env python

from __future__ import print_function, division, absolute_import

from collections import deque
from datetime import datetime
import json

from tornado import gen
from tornado.locks import Condition
from tornado.httpclient import AsyncHTTPClient

import distributed.diagnostics
from distributed.utils import log_errors

client = AsyncHTTPClient()

messages = {}  # Globally visible store of messages
distributed.diagnostics.messages = messages  # monkey-patching


@gen.coroutine
def http_get(route):
    """ Get data from JSON route, store in messages deques """
    with log_errors():
        response = yield client.fetch('http://localhost:9786/%s.json' % route)
        msg = json.loads(response.body.decode())
        messages[route]['deque'].append(msg)
        messages[route]['condition'].notify_all()
        messages[route]['times'].append(datetime.now())


def on_server_loaded(server_context):
    messages['workers'] = {'interval': 1000,
                           'deque': deque(maxlen=1000),
                           'times': deque(maxlen=1000),
                           'condition': Condition()}
    server_context.add_periodic_callback(lambda: http_get('workers'), 1000)

    messages['tasks'] = {'interval': 100,
                         'deque': deque(maxlen=1000),
                         'times': deque(maxlen=1000),
                         'condition': Condition()}
    server_context.add_periodic_callback(lambda: http_get('tasks'), 100)
