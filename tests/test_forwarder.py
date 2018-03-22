#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .context import mqttrest
from mqttrest import forwarder
import unittest
from socketserver import BaseRequestHandler, TCPServer
import threading
import paho.mqtt.client as mqtt
import time

class ForwarderTC(unittest.TestCase):

    def test_withoutaction(self):
        fw = forwarder.Forwarder(path='tests/test.config.json')
        fw.start()
        time.sleep(1)
        fw.stop()

    def test_withaction(self):
        # set up http server
        TCPServer.allow_reuse_address = True
        http_server = TCPServer(('127.0.0.1', 8090), TCPAcceptHandler)
        http_server.last_payload = b''
        server_thread = threading.Thread(target=http_server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print('http server started')
        # set up the forwarder
        fw = forwarder.Forwarder(path='tests/test.config.json')
        fw.connect()
        fw.start()
        time.sleep(1)
        print('forwarder started')
        # create a MQTT client to publish events
        client = mqtt.Client()
        client.connect('127.0.0.1',1883)
        payload = 'foo'
        client.publish('hello/world', payload=payload)
        print('mqtt client published')
        time.sleep(1)
        self.assertEqual(payload,http_server.last_payload)
        client.disconnect()
        print('mqtt client disconnected')
        fw.stop()
        print('forwarder stopped')
        http_server.shutdown()
        print('httpserver shut down')
        http_server.server_close()
        print('http server stopped')
        self.assertTrue(True)


class TCPAcceptHandler(BaseRequestHandler):
    ''' a HTTPHandler that responds 200 to everything'''

    STATIC_RESPONSE = b'''HTTP/1.1 200 OK
Content-Length: 0
'''
    def handle(self):
        data = self.request.recv(1024)
        payload = str(data, 'ascii').split('\r\n')[-1]
        if data:
            print('*Incoming data: \n{}'.format(data))
            self.server.last_payload = payload
        self.request.sendall(TCPAcceptHandler.STATIC_RESPONSE)
