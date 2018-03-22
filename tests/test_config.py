#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .context import mqttrest
from mqttrest import config
import unittest

class ConfigTC(unittest.TestCase):

    def test_wrongpath(self):
        with self.assertRaises(Exception):
            config.Config(path='afilenot.existing')

    def test_exampleconfig(self):
        conf = config.Config(path='tests/example.config.json')
        self.assertEqual(len(conf.routes),3)
        example = None
        for route in conf.routes:
            if route.broker == "127.0.0.1:1883":
                example = route
                break
        self.assertEqual(example.topic, "testcase/demo/d1")
        self.assertEqual(len(example.endpoints), 2)
        self.assertEqual(example.endpoints[0].creds, ('foo', 'bar'))
