#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 PerFact Innovation GmbH & Co. KG <info@perfact.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import mqttrest.config
import paho.mqtt.client as mqtt
import requests
import subprocess
import logging
import argparse
import signal
import time

logformat = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logformat, level=logging.DEBUG)

def ipAdresses():
    return subprocess.check_output(['hostname', '-I']).strip().decode('ascii').split(' ')

class Forwarder(object):
    ''' Listenes to MQTT topics and posts to REST endpoints '''

    def __init__(self, path='config.json'):
        self.config = mqttrest.config.Config(path)
        self.clients = []
        self.running_clients = []
        self.defective_clients = []

    def connect(self):
        ''' connect all configured brokers and subscribe to the given topics '''
        for route in self.config.routes:
            # init client with callbacks
            client = mqtt.Client(userdata=route)
            client.on_connect = on_connect
            client.on_disconnect = on_disconnect
            client.on_message = on_message
            # connect client
            parts = route.broker.split(':')
            connect_params = {'host':parts[0]}
            if len(parts) > 1:
                connect_params['port']=int(parts[1])
            logging.debug('Connecting to %s' % parts)
            ips = ipAdresses()
            for ip in ips:
                connect_params['bind_address']=ip
                try:
                    client.connect(**connect_params)
                except:
                    pass
                else:
                    client.subscribe(route.topic)
                    self.clients.append(client)
                    break
            if client not in self.clients:
                logging.error('Connection failed')
                self.defective_clients.append(client)

    def start(self):
        ''' Start all clients that where connected successfully '''
        for client in self.clients:
            client.loop_start()
            self.running_clients.append(client)

    def stop(self):
        ''' Stop all running clients '''
        logging.info('disconnecting clients')
        for client in self.clients:
            client.disconnect()
        logging.debug('stopping loops')
        #for client in self.running_clients:
        #    client.loop_stop(force=True)

def on_connect(client, userdata, flags, rc):
        logging.debug("Client %s-%s connected" % (userdata.broker, userdata.topic))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logging.warn("Unexpected disconnection: %s-%s" % (userdata.broker, userdata.topic))
    else:
        logging.info("Client %s-%s disconnected" % (userdata.broker, userdata.topic))
    client.loop_stop()

def on_message(client, userdata, message):
    for endpoint in userdata.endpoints:
        logging.debug('Message for %s: %s' % (endpoint.url, message.payload))
        kw = endpoint.requests_params
        kw['data'] = message.payload
        try:
            requests.post(**kw)
        except Exception as err:
            logging.error('Post failed for endpoint: %s' % endpoint.url)
            logging.exception(err)

class ScriptStopper(object):

    def __init__(self):
        self.stop = False
        signal.signal(signal.SIGINT, self.stopThis)
        signal.signal(signal.SIGTERM, self.stopThis)

    def stopThis(self, signum, frame):
        logging.info('Got closing command')
        self.stop = True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Forward MQTT events to REST endpoints')
    parser.add_argument('path', type=str,
                        help='path to the config file',
                        default=None)
    args = parser.parse_args()
    stopper = ScriptStopper()
    fw_instance = Forwarder(path=args.path)
    fw_instance.connect()
    fw_instance.start()
    while not(stopper.stop):
        time.sleep(1)
    fw_instance.stop()
