#!/usr/bin/env python
#
# Copyright (C) 2019 Jay Schulist jayschulist@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

'''
./sensorpush -u name@email.com -p password
'''

from __future__ import print_function

from __future__ import absolute_import

import os, sys, re, getopt, getpass
import time
import datetime
import oauth2
import urllib2
import urlparse
import urllib
import json

class SensorPush(object):
    apiURL = "https://api.sensorpush.com"

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def authorize(self):
        path   = "/api/v1/oauth/authorize"
        params = {
            'email': self.email,
            'password': self.password
        }
        data = self.postToSensorPush(path, params)
        print(data)
        self.authorization = data
        return self.authorization

    def accessToken(self):
        path = "/api/v1/oauth/accesstoken"
        params = {
            authorization: self.authorization
        }
        data = self.postToSensorPush(path, params)
        print(data)
        self.accesstoken = data
        return self.accesstoken

    def gateways(self):
        path = "/api/v1/devices/gateways"
        params = {
            accesstoken: self.accesstoken
        }
        data = self.postToSensorPush(path, params)
        print(data)
        return data

    def sensors(self):
        path = "/api/v1/devices/sensors"
        params = {
            accesstoken: self.accesstoken
        }
        data = self.postToSensorPush(path, params)
        print(data)
        return data

    def samples(self, limit, startTime):
        path = "/api/v1/samples"
        params = {
            accesstoken: self.accesstoken,
            limit: limit,
            startTime: startTime.isoformat()
        }
        data = self.postToSensorPush(path, params)
        print(data)
        return data

    def postToSensorPush(self, path, params):
        data = json.dumps(params, sort_keys=True)
        headers = {}
        headers['accept']       = 'application/json'
        headers['Content-Type'] = 'application/json'
        headers['User-Agent']   = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        headers['Content-Length'] = len(data)
        req = urllib2.Request(self.apiURL + path, data, headers)
        print(req.get_full_url())
        print(req.get_method())
        print(req.headers)
        print(req.get_data())
        resp = urllib2.urlopen(req)
        respData = resp.read()
        print(respData)
        return respData


def exit_with_usage():
    print(globals()['__doc__'])
    os._exit(1)


def main():
    # get username and password for authorization
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'u:p:')
    except Exception as e:
        print(str(e))
        exit_with_usage()
    options = dict(optlist)
    if len(args) > 3:
        exit_with_usage()

    if '-u' in options:
        username = options['-u']
    else:
        username = raw_input('username: ')
    if '-p' in options:
        password = options['-p']
    else:
        password = getpass.getpass('password: ')
    
    # use app email/password to begin authorization
    sensor = SensorPush(email=username, password=password)

    # 1: get authorization code
    sensor.authorize()

    # 2: get access token
    sensor.accessToken()

    # 3: get sensor data
    sensor.sensors()

    # 4: get gateway data
    sensor.gateways()

    # 5: get temperature/humidity data from last 10 minutes
    startTime = datetime.now() - 60 * 1000 * 10
    sensor.samples(limit=10, startTime=startTime)

    sys.exit(0)

if __name__ == "__main__":
    main()
