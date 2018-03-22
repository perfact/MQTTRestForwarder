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

from setuptools import setup, find_packages

setup(name='mqttrestforwarder',
      version='0.0.1',
      description='Forwards events from MQTT to REST endpoints',
      author_email='jh@perfact.de',
      classifiers=['Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
                   'Programming Language :: Python :: 3'],
      keywords='mqtt rest',
      packages=find_packages(exclude=['tests']),
      install_requires=['paho-mqtt','requests'],
      python_requires='>=3',
      entry_points={
        'console_scripts': [
        'mqttrestforwarder=mqttrest.forwarder:main',
            ],
        },
       )
