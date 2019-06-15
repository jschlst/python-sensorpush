# python-sensorpush

Python SensorPush API

For use with [SensorPush](http://www.sensorpush.com) wireless sensors with alerts for monitoring temperature, humidity and more.

Version 0.1.3

Date 06/15/2019

Written by Jay Schulist <jayschulist@gmail.com>


## Example
```
$ python sensorpush.py -u name@email.com -p password

Authentication time: 2019-06-15 12:32:58.095983
Token time: 2019-06-15 12:33:00.731144
Gateways:
  Shop: version 1.0.9(11), paired, last 2019-06-15T17:31:06.000Z
  Heeren: version 1.0.9(11), paired, last 2019-06-15T17:32:59.000Z
  Iola: version 1.0.9(11), paired, last 2019-06-15T17:28:23.000Z
Sensors:
  [EF:45:64:38:76:46] 16965, battery 2.82v, active, Iola Intake
  [CD:D8:E8:19:9E:BA] 26084, battery 2.69v, active, Chicken Roost
  [DA:DE:C5:6D:6D:2E] 43298, battery 3.03v, active, Iola Basement
  [FB:32:7F:9C:1D:88] 26056, battery 2.78v, active, Bee Room
  [C8:87:27:9A:B5:B7] 43558, battery 3.02v, active, Iola Exhaust
  [D7:D8:18:FE:01:E9] 17040, battery 2.39v, active, Shed Outside
  [D0:3E:FC:46:1C:80] 74151, battery 2.94v, active, Chicken Run
  [D5:39:3E:73:4D:9E] 31452, battery 2.83v, active, Shop
Last sample:
Iola Intake, 16965: observed=2019-06-15T17:33:04.000Z, temperature=65.12, humidity=70.29
Chicken Roost, 26084: observed=2019-06-15T17:33:49.000Z, temperature=72.34, humidity=73.35
Iola Basement, 43298: observed=2019-06-15T17:33:20.000Z, temperature=105.7, humidity=18.08
Bee Room, 26056: observed=2019-06-15T17:33:03.000Z, temperature=57.15, humidity=68.95
Iola Exhaust, 43558: observed=2019-06-15T17:33:39.000Z, temperature=104.78, humidity=19.27
Shed Outside, 17040: observed=2019-06-15T17:33:03.000Z, temperature=62.52, humidity=83.51
Chicken Run, 74151: observed=2019-06-15T17:32:53.000Z, temperature=57.54, humidity=68.4
Shop, 31452: observed=2019-06-15T17:33:36.000Z, temperature=57.13, humidity=68.77
```


## Important
[SensorPush API docs](http://www.sensorpush.com/api/docs)

Authorization is required from support@sensorpush.com before API access is allowed.


## Acknowledgments
- [SensorPush JavaScript API](https://github.com/malgorithms/sensorpush) written by Chris Coyne <ccoyne77@gmail.com>
