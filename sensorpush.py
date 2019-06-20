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
import urllib2
import json


class Gateway(object):
    last_alert  = None
    last_seen   = None
    message     = None
    name        = None
    paired      = None
    version     = None

    def __init__(self, data):
        self.last_alert = data['last_alert']
        self.last_seen  = data['last_seen']
        self.message    = data['message']
        self.name       = data['name']
        self.paired     = data['paired']
        self.version    = data['version']

    def __repr__(self):
        return "%s: version %s, %s, last %s" % (self.name, self.version, ("paired" if (self.paired) else "unpaired"), self.last_seen)


class Sensor(object):
    active              = None 
    address             = None
    alert_humidity      = None
    alert_temperature   = None
    battery_voltage     = None
    cal_humidity        = None
    cal_temperature     = None
    deviceId            = None
    id                  = None
    name                = None

    sampleList          = []

    def __init__(self, data):
        self.active = data['active']
        self.address = data['address']
        self.alert_humidity = data['alerts']['humidity']['enabled']
        self.alert_temperature = data['alerts']['temperature']['enabled']
        self.battery_voltage = data['battery_voltage']
        self.cal_humidity = data['calibration']['humidity']
        self.cal_temperature = data['calibration']['temperature']
        self.deviceId = data['deviceId']
        self.id = data['id']
        self.name = data['name']

    def getLastSample(self):
        return self.sampleList[0]

    def __repr__(self):
        output = "[%s] %s, battery %sv, %s, %s" % (self.address, self.deviceId, self.battery_voltage, ("active" if self.active else "inactive"), self.name)
        if (self.sampleList):
            for s in self.sampleList:
                output += "\n%s" % str(s)
        return output

class Sample(object):
    deviceId    = None
    humidity    = None
    temperature = None
    observered  = None

    def __init__(self, deviceId, data):
        self.deviceId = deviceId
        self.humidity = data['humidity']
        self.temperature = data['temperature']
        self.observed = data['observed']

    def __repr__(self):
        return "%s: observed=%s, temperature=%s, humidity=%s" % (self.deviceId, self.observed, self.temperature, self.humidity)


class SensorPush(object):
    apiURL = "https://api.sensorpush.com"

    # api restrictions
    authTimeout     = 60 * 60   # new authorization req every 60 minutes
    tokenTimeout    = 30 * 60   # new token req every 30 minutes
    reqTimeout      = 15        # max 1 req per minute, cheat do every 15 sec

    # authentication data
    authorization   = None
    accesstoken     = None

    # track access
    lastAccess  = None
    lastToken   = None
    lastAuthentication = None

    # track data
    sensorData  = None
    sensorList  = []
    gatewayData = None
    gatewayList = []
    sampleData  = None

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
        timeout = timedelta(seconds=self.reqTimeout) - (datetime.now() - self.lastAccess)
        if (timeout >= timedelta(seconds=self.reqTimeout)):
            return True
        if (block):
            #print("block request for %d seconds" % timeout.total_seconds())
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
        #print("authorization: %s" % self.authorization)
        #print("apikey: %s" % self.apikey)
        print("Authentication time: %s" % self.lastAuthentication)
        return self.authorization

    def accessToken(self):
        path = "/api/v1/oauth/accesstoken"
        params = {
            'authorization': self.authorization
        }
        data = self.postToSensorPush(path, params)
        self.accesstoken = data['accesstoken']
        self.lastToken = datetime.now()
        #print("accesstoken: %s" % self.accesstoken)
        print("Token time: %s" % self.lastToken)
        return self.accesstoken

    def connect(self):
        if (self.authOk()):
            return True
        #print("connect to sensorpush API")
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
        for d in self.gatewayData:
            g = Gateway(self.gatewayData[d])
            #print(g)
            self.gatewayList.append(g)
        return self.gatewayList

    def sensors(self):
        path = "/api/v1/devices/sensors"
        self.connect()
        self.reqOk()
        data = self.postToSensorPush(path, params=None, accesstoken=self.accesstoken)
        self.sensorData = data
        for d in self.sensorData:
            s = Sensor(self.sensorData[d])
            #print(s)
            self.sensorList.append(s)
        return self.sensorList

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
        #print("data:\n %s" % data)
        # iterate over each sensor
        for d in self.sampleData['sensors']:
            deviceId = d.split(".")[0]
            sen = self.getSensor(deviceId=deviceId)
            sampleList = []
            #print("sensor: %s" % str(sen))
            # iterate over each sample
            for c, s in enumerate(self.sampleData['sensors'][d]):
                #print("%d: %s" % (c, s))
                sam = Sample(deviceId, s)
                #print("sample: %s" % str(sam))
                if (sen):
                    sampleList.append(sam)
            sen.sampleList = sampleList
            #print("sampleList:\n%s" % sen.sampleList)
        return self.sampleData

    def getGateway(self, name=None):
        if (self.gatewayList is None):
            self.gateways()
        for g in self.gatewayList:
            if (name is g.name):
                return g
        return None

    def getSensor(self, name=None, deviceId=None):
        if (self.sensorList is None):
            self.sensors()
        for s in self.sensorList:
            if (name != None):
                if (name == s.name):
                    #print("name match: %s" % str(s))
                    return s
            elif (deviceId != None):
                if (deviceId == s.deviceId):
                    #print("deviceId match: %s" % str(s))
                    return s
        return None

    def getSamples(self, name=None, deviceId=None):
        if (self.sensorList is None):
            self.sensors()
        if (self.sampleList is None):
            self.samples()
        s = self.getSensor(name=name, deviceId=deviceId)
        if (s == None):
            return None
        return s.sampleList

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
        
        #print(req.get_full_url())
        #print(req.get_method())
        #print(req.headers)
        #print(req.get_data())

        self.lastAccess = datetime.now()
        resp = urllib2.urlopen(req)
        #print("last access time: %s" % str(self.lastAccess))
        respData = resp.read()
        respJson = json.loads(respData)
        #print(json.dumps(respJson, sort_keys=True, indent=4))
        return respJson


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

    # 3: get gateway data
    g = sensor.gateways()
    print("Gateways:")
    for d in g:
        print("  %s" % str(d))

    # 4: get sensor data
    s = sensor.sensors()
    print("Sensors:")
    for d in s:
        print("  %s" % str(d))

    # 5: get temperature/humidity last 10 samples 
    sensor.samples(limit=10)

    # 6: get temperature/humidity last 30 minutes, max 1000 samples
    #stopTime = datetime.now()
    #startTime = stopTime - timedelta(minutes=30)
    #sensor.samples(limit=1000, startTime=startTime, stopTime=stopTime)

    # 7: print most recent sample from each sensor
    print("Last sample:")
    for d in sensor.sensorList:
        print("  %s, %s" % (d.name, d.getLastSample()))

    sys.exit(0)

if __name__ == "__main__":
    main()
