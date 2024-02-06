import argparse, json, os, textfsm
from multiprocessing import connection
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from jinja2 import Environment, FileSystemLoader
from napalm import get_network_driver
from numpy import var
from pysnmp.hlapi import *
from functools import partial
from email.message import EmailMessage
from email.utils import make_msgid
from netmiko import ConnectHandler 
import pandas as pd
import re
from datetime import datetime
result_list = []
        
def parseArgs():
    parser = argparse.ArgumentParser(
        description="passwords from ADO library")
    parser.add_argument('--device_list', dest='device_list', action='store', nargs='+',
                        help="List of devices ")
    parser.add_argument('--username', dest='username', action='store',
                        help="Username")
    parser.add_argument('--password', dest='password', action='store',
                        help="Password")
    args, unknown = parser.parse_known_args()
    return args


def get_tacacs(nd):
    try:
        output = nd.sendcommand('show runn | section tacacs')
        return output
    except Exception as e:
        return 'Error'

def hou_hou2(str_in):    
    if '139.65.136.58' in str_in and '139.65.143.4' in str_in:
        return True
    else:
        return False

def nadc_(str_in):
    if '139.65.137.160' in str_in:
        return True
    else:
        return False




def single_device_operations(username, password,  device):
    print(device['ip_address'])
    import networkdevice
    nd = networkdevice.IOS_device(device['ip_address'],username,password)
    if nd.good_ssh_connection:
        tacacs = get_tacacs(nd)
        nd.get_version()
        houston = 'NA'
        nadc = 'NA'
        if type(tacacs) == str:
            houston = hou_hou2(tacacs)
            nadc = nadc_(tacacs)        
        result = {
            'Hostname' : device['hostname'],
            'IP address' : nd.ip,
            'Is Alive' : nd.is_alive,
            'Major Version' : nd.sw_version_major,
            'Minor Version' : nd.sw_version_minor,
            'Good SSH Connection' : nd.good_ssh_connection,
            'Current tacacs' : tacacs,
            'HOU_ACS & HOU2_ACS': houston,
            'NADC found': nadc
        }
    else:
        result = {
            'Hostname' : device['hostname'],
            'IP address' : device['ip_address'],
            'Is Alive' : False,
            'Major Version' : 'NA',
            'Minor Version' : 'NA',
            'Good SSH Connection' : False,
            'Current tacacs' : 'NA',
            'HOU_ACS & HOU2_ACS': 'NA',
            'NADC found': 'NA'
        }
    return result
    

def Main():
    args = parseArgs()

    username = args.username
    password = args.password


    with open('devices.json') as file:
        device_list=json.load(file)
    print(f'Total Devices : {len(device_list)}')
    testing = False
    if not testing:
        single_device_operations_map = partial(single_device_operations, username, password, )
        with ThreadPoolExecutor(max_workers=50) as executor:
            for result in executor.map(single_device_operations_map, device_list):
                result_list.append(result)
    else:
        for one_device in device_list:
            result = single_device_operations(username, password, one_device)     
            result_list.append(result)
    df = pd.DataFrame(result_list)
    df.index +=1
    df.to_csv(f'NADC_APAC_ios_Fetch_tacacs_Report-{datetime.today().strftime("%Y-%m-%d %H_%M_%S")}.csv')

if __name__ == "__main__":
    Main()