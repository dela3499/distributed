from __future__ import print_function, division, absolute_import

import requests
import socket
from subprocess import Popen, PIPE
from time import sleep, time

import pytest

from distributed import Scheduler, Executor
from distributed.utils import get_ip, ignoring


def test_defaults():
    try:
        proc = Popen(['dscheduler'], stdout=PIPE, stderr=PIPE)
        e = Executor('127.0.0.1:%d' % Scheduler.default_port)

        response = requests.get('http://127.0.0.1:9786/info.json')
        assert response.ok
        assert response.json()['status'] == 'running'
    finally:
        e.shutdown()
        proc.kill()


def test_bokeh():
    pytest.importorskip('bokeh')

    try:
        proc = Popen(['dscheduler'], stdout=PIPE, stderr=PIPE)
        e = Executor('127.0.0.1:%d' % Scheduler.default_port)

        while True:
            line = proc.stderr.readline()
            if b'Start Bokeh UI' in line:
                break

        start = time()
        while True:
            try:
                for name in [socket.gethostname(), 'localhost', '127.0.0.1', get_ip()]:
                    response = requests.get('http://%s:8787/status/' % name)
                    assert response.ok
                break
            except:
                sleep(0.1)
                assert time() < start + 5

    finally:
        with ignoring(Exception):
            e.shutdown()
        with ignoring(Exception):
            import distributed.diagnostics.bokeh
            distributed.diagnostics.bokeh.server_process.kill()
        with ignoring(Exception):
            proc.kill()
