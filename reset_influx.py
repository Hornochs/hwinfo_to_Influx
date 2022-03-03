#!/usr/bin/python3
import os
import json
import time
from datetime import datetime
from influxdb import InfluxDBClient
INFLUXUSER = 'user'
INFLUXPASS = 'pass'
INFLUXDB = 'db'
CLIENT = InfluxDBClient("grafanaadress", "8086", INFLUXUSER, INFLUXPASS, INFLUXDB)
CHECKS = [
    {
        'system' : 'Arbeitspc',
        'address' : '10.0.5.4',
        'perfdata' : 'arbeitspc'
}, {
        'system' : 'Gamingpc',
        'address' : '10.0.5.1',
        'perfdata' : 'gamingpc'
}]

for check in CHECKS:
    NOW = datetime.now()
    test = os.popen("ping -c 1 {}".format(check["address"])).read()
    packetloss = test.splitlines()
    packetloss = packetloss[4].split(", ")
    if packetloss[1][0] == "0":
        fields = os.popen("influx -username '{}' -password '{}' -execute 'SHOW FIELD KEYS on {} FROM {}' -format json".format(INFLUXUSER, INFLUXPASS, INFLUXDB, check['perfdata'])).read()
        jsons = json.loads(fields)
        summarized = {}
        for field in jsons['results'][0]['series'][0]['values']:
            summarized[field[0]] = float(0)
        json_body=[
        {
            "measurement": check['perfdata'],
            "time": NOW,
            "fields" : summarized
        }
        ]
        CLIENT.write_points(json_body)
        pass
