import psutil
import time
import subprocess
import json
import requests
from datetime import datetime
from influxdb import InfluxDBClient

CLIENT = InfluxDBClient("grafana.i.3fu.de", "8086", "user", "pass", "db")
MEASUREMENT = "arbeitspc"
REMOTE_EXE = "C:\\Users\\Gamienator\\AppData\\Roaming\\RemoteSensorMonitoring\\Remote Sensor Monitor.exe"

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def findProcessIdByName(processName):
    '''
    Get a list of all the PIDs of a all the running process whose name contains
    the given string processName
    '''

    listOfProcessObjects = []

    #Iterate over the all the running process
    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
           # Check if process name contains the given name string.
           if processName.lower() in pinfo['name'].lower() :
               listOfProcessObjects.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
           pass

    return listOfProcessObjects

def startProgram():
    SW_HIDE = 0
    info = subprocess.STARTUPINFO()
    info.dwFlags = subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = SW_HIDE
    exe = [REMOTE_EXE, "--gpuz=0", "--aida64=0", "--ohm=0"]
    subprocess.Popen(exe, startupinfo=info)
    #exe = subprocess.Popen(REMOTE_EXE, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)

def sendToInflux():
    NOW = datetime.now()
    hwinfodata = requests.get('http://localhost:55555')
    data = hwinfodata.json()
    summarized = {}
    for d in data:
        name = "{}__{}".format(d['SensorClass'], d['SensorName']).replace(" ", "_")
        summarized[name]=d['SensorValue'].replace(",", ".")

    json_body=[
        {
            "measurement": MEASUREMENT,
            "time": NOW,
            "fields" : summarized
        }
    ]
    CLIENT.write_points(json_body)


def main():
    startProgram()
    time.sleep(10)

    # Find PIDs od all the running instances of process that contains 'chrome' in it's name
    listOfProcessIds = findProcessIdByName('Remote Sensor Monitor.exe')

    if len(listOfProcessIds) > 0:
       #print('Process Exists | PID and other details are')
       for elem in listOfProcessIds:
           processID = elem['pid']
           sendToInflux()
           #print((processID ,processName,processCreationTime ))
           process = psutil.Process(processID)
           process.terminate()
    else :
       print('No Running Process found with given text')

if __name__ == '__main__':
   main()
