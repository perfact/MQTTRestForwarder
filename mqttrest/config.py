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

import json

class Endpoint(object):
    ''' REST-Endpoint with or without credentials '''

    def __init__(self, url, user=None, pw=None):
        self.url = url
        self.requests_params = {'url':self.url}
        if (user is not None) and (pw is not None):
            self.creds = (user, pw)
            self.requests_params['auth'] = self.creds

class Route(object):
    ''' Broker and topic with a list of endpoints as destinations '''

    def __init__(self,broker, topic):
        self.broker = broker
        self.topic = topic
        self.endpoints = []

class Config(object):

    def __init__(self, path='config.json'):
        pairs = self.readConfig(path)
        route_merger = {}
        for pair in pairs:
            broker = pair['broker']
            topic = pair['topic']
            key = broker+'justmakingsure'+topic
            route_merger[key] = route_merger.get(key, Route(broker=broker, topic=topic))
            endpoint = Endpoint(url=pair['endpoint'],
                                user=pair.get('endpoint_user', None),
                                pw=pair.get('endpoint_pw',None))
            route_merger[key].endpoints.append(endpoint)
        self.routes = [r for r in route_merger.values()]


    def readConfig(self, path):
        '''read the given config file and return a list of broker, topic, endpoint triplets
        '''
        with open(path) as json_data:
            config = json.load(json_data)
            return config['routes']
            # TODO: use db connectstring to read config from db
