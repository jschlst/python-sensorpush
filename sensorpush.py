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
from datetime import datetime, timedelta
import oauth2
import urllib2
import urlparse
import urllib
import json

class SensorPush(object):
    apiURL = "https://api.sensorpush.com"

    # track authentication
    authorization = None
    accesstoken = None
    lastAuthentication = None
    lastToken = None
    authTimeout = 60 * 60
    tokenTimeout = 30 * 60

    # track access
    lastAccess = None
    reqTimeout = 60     # max 1 req per minute

    # track data
    sensorData = None
    gatewayData = None
    sampleData = None

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def authOk(self):
        if (self.lastAuthentication == None or self.lastToken == None):
            return False
        authTime = datetime.now() - self.lastAuthentication
        tokenTime = datetime.now() - self.lastToken
        if (authTime > timedelta(seconds=self.authTimeout)):
            # need to re-autenticate
            return False
        if (tokenTime > timedelta(seconds=self.tokenTimeout)):
            # need new token
            return False
        return True

    def reqOk(self, block=True):
        timeout = datetime.now() - self.lastAccess
        if (timeout >= timedelta(seconds=self.reqTimeout)):
            return True
        if (block):
            print("block request for %d seconds" % timeout.total_seconds())
            time.sleep(timeout.total_seconds())
            return True
        else:
            return False

    def authorize(self):
        path   = "/api/v1/oauth/authorize"
        params = {
            'email': self.email,
            'password': self.password
        }
        data = self.postToSensorPush(path, params)
        self.authorization  = data['authorization']
        self.apikey         = data['apikey']
        self.lastAuthentication = datetime.now()
        print("authorization: %s" % self.authorization)
        print("apikey: %s" % self.apikey)
        print("last authentication: %s" % self.lastAuthentication)
        return self.authorization

    def accessToken(self):
        path = "/api/v1/oauth/accesstoken"
        params = {
            'authorization': self.authorization
        }
        data = self.postToSensorPush(path, params)
        self.accesstoken = data['accesstoken']
        self.lastToken = datetime.now()
        print("accesstoken: %s" % self.accesstoken)
        print("last token: %s" % self.lastToken)
        return self.accesstoken

    def connect(self):
        if (self.authOk()):
            return True
        print("connect to sensorpush API")
        # do initial authorization or re-authorize
        self.authorize()
        self.accessToken()
        return True

    def gateways(self):
        path = "/api/v1/devices/gateways"
        self.connect()
        self.reqOk()
        data = self.postToSensorPush(path, params=None, accesstoken=self.accesstoken)
        self.gatewayData = data
        return data

    def sensors(self):
        path = "/api/v1/devices/sensors"
        self.connect()
        self.reqOk()
        data = self.postToSensorPush(path, params=None, accesstoken=self.accesstoken)
        self.sensorData = data
        return data

    def samples(self, limit=100, startTime=None, stopTime=None):
        path = "/api/v1/samples"
        params = {
            'limit': limit
        }
        if (startTime != None):
            params['startTime'] = startTime.isoformat()
        if (stopTime != None):
            params['stopTime'] = stopTime.isoformat()
        self.connect()
        self.reqOk()
        data = self.postToSensorPush(path, params, self.accesstoken)
        self.sampleData = data
        return data

    def postToSensorPush(self, path, params=None, accesstoken=None):
        headers = {}
        if (params != None):
            data = json.dumps(params, sort_keys=True)
            headers['Content-Length'] = len(data)
            headers['Content-Type'] = 'application/json'
        else:
            data = ''
        headers['accept']       = 'application/json'
        headers['User-Agent']   = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        if (accesstoken != None):
            headers['Authorization'] = accesstoken
        req = urllib2.Request(self.apiURL + path, data, headers)
        
        print(req.get_full_url())
        print(req.get_method())
        print(req.headers)
        print(req.get_data())

        self.lastAccess = datetime.now()
        resp = urllib2.urlopen(req)
        print("last access time: %s" % str(self.lastAccess))
        respData = json.loads(resp.read())
        print(json.dumps(respData, sort_keys=True, indent=4))
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
    # 2: get access token
    # automatically checked and maintained through sensors(), gateways(), and samples() call

    # 3: get sensor data
    sensor.sensors()

    # 4: get gateway data
    sensor.gateways()

    # 5: get temperature/humidity last 10 samples 
    sensor.samples(limit=10)

    # 6: get temperature/humidity last 10 minutes, max 1000 samples
    stopTime = datetime.now()
    startTime = stopTime - timedelta(minutes=10)
    sensor.samples(limit=1000, startTime=startTime, stopTime=stopTime)

    sys.exit(0)

if __name__ == "__main__":
    main()
