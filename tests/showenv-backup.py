import argparse, json, textfsm
import re

username = "user"
password = "password"
ip_address = "12"
neighbor_ip = "138"

#function to display last n lines of show cmd output
def tail(text, n):
	output = text.split('\n')
	last = output[len(output)-n:]
	my_str = '\n'.join(last)
	return my_str

def get_eigrp_log(neighbor_ip):
    try:
        command = 'show log | inc ' + neighbor_ip
        output = self.sendcommand(command)
        return output
    except Exception as e:
        return 'Error'

# WORK ON THIS
def check_eigrp_status(pattern, current_status): # for code review
    pattern = re.compile(pattern)
    parsed_result = re.findall(pattern, current_status)
    parsed_result = parsed_result[0].split() #only difference
    status = parsed_result[4].strip(':')
    return status


def check_interface(pattern, current_status): # for code review
    pattern = re.compile(pattern)
    parsed_result = re.findall(pattern, current_status)
    parsed_result = parsed_result[0].split()
    interface = parsed_result[2].strip('()') #only difference
    return interface

def get_eigrp_neighbors(nd):
    try:
        output = nd.sendcommand('show ip eigrp neighbors')
        return output
    except Exception as e:
        return 'Error'

def get_interface_neighbor(nd): 
    try:
        command = 'show interface ' + interface
        output = nd.sendcommand(command)
        return output
    except Exception as e:
        return 'Error'

# def get_tacacs(nd):
#     try:
#         output = nd.sendcommand('show runn | section tacacs')
#         return output
#     except Exception as e:
#         return 'Error'

def single_device_operations(username, password, ip_address):
    import networkdevice
    nd = networkdevice.IOS_device(ip_address, username, password)
    current_status = tail(get_eigrp_log(nd),1)
    # print(current_status)
    interface = check_interface(r'Neighbor.*', current_status)
    eigrp_status = check_eigrp_status(r'Neighbor.*', current_status)
    if nd.good_ssh_connection:
        eigrp_log = tail(get_eigrp_log(nd),10)
        eigrp_neighbor = get_eigrp_neighbors(nd)
        if eigrp_status == 'up':
            result = eigrp_log +'\n\n'+ eigrp_neighbor
        else:
            command = 'show interface ' + interface
            interface_info = nd.sendcommand(command)
            result = eigrp_log +'\n\n'+ interface_info
            # result = eigrp_log  #delete after testing
        # result = eigrp_log + '\n\n'+ eigrp_neighbor
        # {
        #     'IP address' : nd.ip,
        #     'Is Alive' : nd.is_alive,
        #     'Good SSH Connection' : nd.good_ssh_connection,
        #     'EIGRP log' : eigrp_log
        # }
    else:
        result = {
            'IP address' : ip_address,
            'Is Alive' : False,
            'Good SSH Connection' : False
        }
    return result

def Main():
    a = single_device_operations(username, password, ip_address)
    print(a)

if __name__ == "__main__":
    Main()