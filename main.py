# -*- coding: utf-8 -*-
"""
Created on Wed Dec 06 08:47:28 2017

@author: ehigh
@email : ehigh2014@163.com
"""
import os
import requests
import json
from datetime import datetime
import time
import Config
import logging 

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='client.log',
                filemode='w')

def getStorjStatusLocal(file_name):
    '''
        Get the Local Status
    '''
    result = {}
    result['name'] = Config.SERVER_NAME
    result['status'] = 'shutdown'
    result['timestamp'] = str(datetime.now())
    with open(file_name, 'r') as f:
        lines = f.readlines()
        if len(lines) < 5:
            return False
        title = lines[2]
        status = lines[4]
        # get node id
        idx = title.find('Share')
        ndx = title.find('Status')
        result['node_id'] = status[idx: ndx - 4].replace(' ', '')
        # get status
        idx = title.find('Status')
        ndx = title.find('Uptime')
        result['status'] = status[idx: ndx - 4]
        # get allocs, diff version
        idx = title.find('Allocs')
        if idx < 0:
            # Storjshare daemon < 5.2.0
            idx = title.find('Offers')
        ndx = title.find('Delta')
        # do not +1, unreadable code, ???
        result['allocs'] = int(status[idx+1 : ndx -4].replace(' ', ''))
        # get shared
        idx = title.find('Shared')
        ndx = title.find('Bridges')
        result['shared'] = status[idx+1 : ndx -4].replace(' ', '')
        return result
    return False

def getStorjStatusOnline(node_id):
    '''
        Get the Online Status
    '''
    url = Config.STORJ_IO_URL + node_id
    r = requests.get(url)
    if r.reason == 'OK':
        resp = json.loads(r.text)
        return resp
    else:
        return False

def getStorjStatus():
    os.system("storjshare status > cache.log")
    status = {}
    local_status = getStorjStatusLocal("cache.log")
    os.remove("cache.log")
    if local_status and ('node_id' in local_status):
        online_status = getStorjStatusOnline(local_status['node_id'])
        if online_status:
            status = dict(local_status.items() + online_status.items())
            return status
        else:
            return False
    return False
            
def sendStorjStatServer(status):
    try:
        url = 'http://' + Config.SERVER_IP +":" + str(Config.SERVER_PORT) + "/hb"
        r = requests.post(url, data = status)
        logging.debug(r.text)
    except Exception, e:
        logging.error(e)
        return False

def client_run():
    logging.info("PyStorjStatClient running...")
    while True:
        status = getStorjStatus()
        if status:
            sendStorjStatServer(status)
        time.sleep(Config.SLEEP_TIME)

if __name__ == "__main__":
    client_run()
