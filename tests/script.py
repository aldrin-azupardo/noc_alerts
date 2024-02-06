import argparse, json, textfsm
# from multiprocessing import connection
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import os
# from jinja2 import Environment, FileSystemLoader
# import re
# from datetime import datetime


username = "svc-voy-ansible"
password = "K1oz(q_4sjqAIl=zia"
ip_address = "136.171.179.52"
# def get_tacacs(nd):
#     try:
#         output = nd.sendcommand('show runn | section tacacs')
#         return output
#     except Exception as e:
#         return 'Error'

def parse_environment(nd):
    output = nd.get_env_details()
    template = open('./parser/show_env_all.textfsm')
    results_template = textfsm.TextFSM(template)
    # header = results_template.header
    parsed_results = results_template.ParseText(output)
    # print(parsed_results)
    return parsed_results


def single_device_operations(username, password, ip_address):
    import networkdevice
    nd = networkdevice.IOS_device(ip_address, username, password)
    if nd.good_ssh_connection:
        # tacacs = get_tacacs(nd)
        # nd.get_version() 
        parsed_results = parse_environment(nd)
        result = {
            # 'Hostname' : hostname,
            'IP address' : nd.ip,
            'Is Alive' : nd.is_alive,
            'Good SSH Connection' : nd.good_ssh_connection,
            'Environment_details' : parsed_results
            # 'Current tacacs' : tacacs,
        }
    else:
        result = {
            'IP address' : ip_address,
            'Is Alive' : False,
            'Good SSH Connection' : False,
            'Environment_details' : []
        }
    return result

def Main():
    a = single_device_operations(username, password, ip_address)
    print(a)

if __name__ == "__main__":
    Main()