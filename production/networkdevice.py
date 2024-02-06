from asyncio.subprocess import DEVNULL
from multiprocessing import connection
import re
import os
from netmiko import ConnectHandler
import logging
from incidentrepo import IncidentRepository
logging.basicConfig(filename='network_device.log', level=logging.ERROR, format='%(asctime)s %(message)s')
import commandparser

class Network_device(object):
    """Class to represent network switches and routers"""
    print("networkdevice.py")
    def __init__(self, repository, credential_params, secret, device_os):
        self.username = credential_params['username']
        self.password = credential_params['password']
        self.secret = secret
        self.repository = repository
        self.incident = repository.get_incident({"number": credential_params['number']})
        self.ip = self.incident.ip_address
        self.neighbor_ip = self.incident.neighbor_ip
        self.interface = self.incident.interface
        self.device_os = device_os
        self.is_alive = False
        self.good_ssh_connection = False
        self.connection = None
        self.is_alive = self.ping_device()
        self.createconnection()
   
    def ping_device(self):
        """
        Returns True if host responds to a ping request
        """ 
        import subprocess, platform
        try:
            x =  subprocess.call(f"ping -c 1 {self.ip}", shell=True, stdout=DEVNULL) == 0  
            return x 
        except:
            return False

    def createconnection(self):
        """Creates a new SSH / Netmiko connection to the network device
        at ip using username and password to login. Returns the new connection object."""
        connection_dict = {
                "ip": self.ip,
                "username": self.username,
                "password": self.password,
                "secret": self.secret,
                "device_type": self.device_os,
                "global_delay_factor": 5,
                "banner_timeout" : 20,
                "auth_timeout" : 60 
            }
        try:
            self.connection = ConnectHandler(**connection_dict)
            self.good_ssh_connection = True
            # self.connection.enable()
        except:
            self.connection = None
            self.good_ssh_connection = False

    def sendcommand(self, x_command_string:str, x_expect_string = '#', x_strip_prompt = False, x_strip_command = True):
        """Formats and sends a Netmiko 'send_command()' using the connection and command passed in. The return
        is the output from the device after executing the command. Command is passed as x_command. If the expected 
        response is something other than the standard prompt then you can specify a unique string in the argument x_expect_string. x_strip_prompt controls if
        the device prompts are included in what is returned. """
        try:
            output = self.connection.send_command(
            command_string = x_command_string,
            # expect_string = x_expect_string,
            # strip_prompt = x_strip_prompt,
            # strip_command = x_strip_command
            )
            return output
        except:
            return False

    def get_env_details(self):
        pass

    def get_inventory(self):
        pass

    def power_failure_details(self):
        pass

    def get_eigrp_log(self, neighbor_ip):
        pass

    def get_eigrp_neighbors(self):
        pass

    def get_interface_detail(self, interface): 
        pass

    def get_interface_detail_with_neighbor_ip(self, neighbor_ip): 
        pass 

    def get_bgp_summary(self, neighbor_ip):
        pass
    
    def get_bgp_neighbor(self, neighbor_ip):
        pass
    
    def get_interface_connection(self, neighbor_ip):
        pass

    def get_clock(self):
        pass

    def head(self, text, n):
        output = text.split('\n')
        first = output[:n]
        my_str = '\n'.join(first)
        return my_str

    def tail(self,text, n):
        output = text.split('\n')
        last = output[len(output)-n:]
        my_str = '\n'.join(last)
        return my_str

    def percentage(self, frac_str):
        num, denom = frac_str.split('/')
        frac = (float(num) / float(denom))*100
        if frac < 1:
            frac = 1
        else:
            frac = int(round(frac,0))
        return str(frac) + "%"

    def put_incident(self, params):
        self.repository.put_incident(params=params)
        
class NXOS_device(Network_device):
    already_got_running_config = False
    already_got_version = False
    running_config = ''
    startup_config = ''
    version_config = ''
    def __init__(self,ip, username, password, secret =''):
        super().__init__(ip, username, password, secret, 'cisco_nxos')

    def get_running_config(self):
        try:
            output = self.sendcommand('show running-config')
            self.running_config = output
            self.already_got_running_config = True
        except BaseException as e:
            logging.exception(f'NXOS_device - get_running_config failed for device {self.ip} Error: {e}')        
            self.running_config = f'show running-config Exception Occured: {e}'

    def get_startup_config(self):
        try:
            output = self.sendcommand('show startup-config')
            self.startup_config = output
        except BaseException as e:
            logging.exception(f'NXOS_device - get_startup_config failed for device {self.ip} Error: {e}')        

    def get_version(self):
        if self.already_got_version == False:
            output = self.sendcommand('show version')
            self.version_config = output
        try:
            version_pattern = re.compile(r'NXOS:\s+version\s+(\d+)\D?(\d*)\D?(\d*)')
            x = re.search(version_pattern, self.version_config)
            if x == None:
                version_pattern = re.compile(r'system:\s+version\s+(\d+)\D?(\d*)\D?(\d*)')
                x = re.search(version_pattern, self.version_config)
            self.sw_version_major = x.group(1)
            self.sw_version_minor = x.group(2)
            self.sw_version_patch = x.group(3)
        except BaseException as e:
            logging.exception(f'NXOS_device - get_version failed for device {self.ip} Error: {e}')        

    def get_BIOS_version(self):
        if self.already_got_version == False:
            output = self.sendcommand('show version')
            self.version_config = output
        try:
            version_pattern = re.compile(r'BIOS:\s+version\s+(\d+)\D?(\d*)\D?(\d*)')
            x = re.search(version_pattern, self.version_config)
            self.BIOS_version_major = x.group(1)
            self.BIOS_version_minor = x.group(2)
            self.BIOS_version_patch = x.group(3)
        except BaseException as e:
            logging.exception(f'NXOS_device - get_BIOS_version failed for device {self.ip} Error: {e}')        

    def good_checkpoint(self):
        try:
            output = self.sendcommand('clear checkpoint database')
            output += self.sendcommand('checkpoint kctl')
            return True
        except BaseException as e:
            logging.exception(f'NXOS_device - good_checkpoint failed for device {self.ip} Error: {e}')        
            return False

    def sw_version_is_good(self):
        if int(self.sw_version_major) >= 9 and int(self.sw_version_minor) >= 3:
            return True
        else:
            logging.error(f'NXOS_device - sw_version_is_good Error sw version is {self.version} but requires 9.3 or higher for rollback. Device:{self.ip}')
            return False

    def set_rollback_nxos(self,sleeptime:str):
        """Saves the running config and configures a scheduler job to 
        revert to the saved configuration after sleeptime (minutes). Success returns 
        screen output. """
        self.get_version()
        if self.sw_version_is_good(): # Rollback using Scheduler requires 9.3 or higher os.
            if self.good_checkpoint():
                output = self.connection.send_config_set([ 
                    "clear scheduler logfile",
                    "no feature scheduler",
                    "feature scheduler",
                    "scheduler logfile size 512",
                    "no scheduler job name kctl",
                    "no scheduler schedule name ROLLBACK",
                    "scheduler job name kctl", 
                    "rollback running-config checkpoint kctl",
                    "exit",
                    "scheduler schedule name ROLLBACK",
                    "job name kctl",
                    "time start +" + sleeptime,
                    "end"])
                self.rollback_succeeded()
            else:
                logging.error(f'NXOS_device - good_checkpoint Error in set_rollback_nxos Device:{self.ip}')
        else:
            logging.error(f'NXOS_device - sw_version_is_good Error in set_rollback_nxos Device: {self.ip}')

    def rollback_succeeded(self):
        output = self.sendcommand('show scheduler schedule')
        rollback_pattern = re.compile(r'^Schedule Name       : ROLLBACK\s\S+\sUser Name\s+: \S+\sSchedule Type\s+: Run once on [A-Z,a-z,0-9,:, ]+\sLast Execution Time : Yet to be executed\s\S+\s+Job Name\s+Last Execution Status\s\S+\skctl')
        if re.search(rollback_pattern, output):
            self.good_rollback = True
        else:
            logging.error(f'NXOS_device - rollback_succeeded Error. Success Pattern not found. Device {self.ip}')

class IOS_device(Network_device):

    def __init__(self, repository, credential_params, secret=''):
        super().__init__(repository, credential_params, secret, 'cisco_ios')

    def get_env_details(self):
        try:
            output = self.sendcommand('show environment all')
            return output
        except Exception as e:
            return 'Error'
            
    def get_inventory(self):
        try:
            output = self.sendcommand('show inventory')
            return output
        except BaseException as e:
            logging.exception(f'IOS_device - get_inventory failed for device {self.ip} Error: {e}')

    def power_failure_details(self) -> dict:
        try:
            environment_details = self.get_env_details()
            bad_power = re.findall(r'.*Bad.*|.*No Input Power.*|.*Not Present.*', environment_details)
            if len(bad_power):
                    for item in bad_power:
                        print(item)
                        check_for_serial = re.search(r'(?=.*[A-Z])(?=.*[0-9])[A-Z0-9]{11}', item)
                        if check_for_serial != None:
                            print('SERIAL IS AVAILABLE')
                            print("Full match: % s" % (check_for_serial.group(0)))
                            return {"environment_details" : environment_details}
                        else:
                            inventory_details = self.get_inventory()
                            print('NO AVAILABLE SERIAL')
                            print(environment_details)
                            print(inventory_details)
                            return {"inventory_details" : inventory_details, "environment_details" : environment_details}
            else:
                return {"environment_details" : environment_details} 
        except Exception as e:
            return 'Error'

    def get_eigrp_log(self, neighbor_ip):
        try:
            command = 'show log | inc ' + neighbor_ip
            output = self.sendcommand(command)
            output = self.tail(output, 10)
            return output
        except Exception as e:
            return 'Error'

    def get_eigrp_neighbors(self):
        try:
            output = self.sendcommand('show ip eigrp neighbors')
            return output
        except Exception as e:
            return 'Error'
            
    def get_interface_detail(self, interface): 
        try:
            command = 'show interface ' + interface
            output = self.sendcommand(command)
            output = self.head(output, 6)
            return output
        except Exception as e:
            return 'Error'

    def get_interface_detail_with_neighbor_ip(self, neighbor_ip): 
        try:
            output = self.get_eigrp_log(neighbor_ip)
            current_status = self.tail(output, 1)
            interface = commandparser.CommandParser(r'Neighbor.*', current_status).get_interface()
            output = self.get_interface_detail(interface)
            return output
        except Exception as e:
            return 'Error'
    
    def get_interface_detail_txrx(self, interface):
        try:
            interface_detail = self.get_interface_detail(interface)
            txload = commandparser.CommandParser(r'reliability\s.*', interface_detail).get_txload()
            txload = self.percentage(txload)
            rxload = commandparser.CommandParser(r'reliability\s.*', interface_detail).get_rxload()
            rxload = self.percentage(rxload)
            return {'txload': txload, 'rxload': rxload}
        except Exception as e:
            return 'Error'

    def get_bgp_summary(self, neighbor_ip):
        try:
            command = 'show ip bgp summary | include ' + neighbor_ip
            output = self.sendcommand(command)
            return output
        except Exception as e:
            return 'Error'

    def get_bgp_neighbor(self, neighbor_ip):
        try:
            command = 'show ip bgp neighbor ' + neighbor_ip
            output = self.sendcommand(command)
            return output
        except Exception as e:
            return 'Error'
    
    def get_bgp_connection(self, neighbor_ip):
        try:
            bgp_neighbor = self.get_bgp_neighbor(neighbor_ip)
            local_host = commandparser.CommandParser('./parser/show_ip_bgp_neighbor.textfsm', bgp_neighbor).get_first_index()[0]
            command = 'sh ip int br | inc ' + local_host
            output = self.sendcommand(command)
            return output
        except Exception as e:
            return 'Error'    

    def get_interface_description(self, neighbor_ip) -> dict:
        try:
            bgp_connection = self.get_bgp_connection(neighbor_ip)
            interface = commandparser.CommandParser('./parser/show_ip_int_br.textfsm', bgp_connection).get_first_index()[0]
            command = 'show int ' + interface
            interface_description = self.sendcommand(command)
            return {"interface_description" : interface_description}
        except Exception as e:
            return 'Error'

class JUNOS_device(Network_device):
    already_got_running_config = False
    already_got_version = False
    running_config = ''
    startup_config = ''
    version_config = '' 

    def __init__(self, repository, credential_params, secret=''):
        super().__init__(repository, credential_params, secret, 'juniper_junos')

    def get_env_details(self):
        try:
            output = self.sendcommand('show chassis environment')
            return output
        except BaseException as e:
            return 'Error' 

    def get_inventory(self):
        try:
            output = self.sendcommand('show chassis hardware')
            return output
        except BaseException as e:
            return 'Error'  

    def power_failure_details(self) -> dict:
        try:
            environment_details = self.get_env_details()
            bad_power = re.findall(r'.*Bad.*', environment_details)
            if len(bad_power):
                inventory_details = self.get_inventory()
                return {"inventory_details" : inventory_details, "environment_details" : environment_details}
            else:
                pass #is this allowed?
            return {"environment_details" : environment_details} 
        except Exception as e:
            return 'Error'

    def get_eigrp_log(self, neighbor_ip):
        pass

    def get_eigrp_neighbors(self):
        pass

    def get_interface_detail(self, neighbor_ip): 
        pass

    def get_interface_detail_with_neighbor_ip(self, neighbor_ip):
        pass
   
    def get_bgp_summary(self, neighbor_ip):
        try:
            command = 'show bgp summary | match ' + neighbor_ip
            output = self.sendcommand(command)
            output = self.head(output, 1)
            return output
        except Exception as e:
            return 'Error'

    def get_bgp_neighbor(self, neighbor_ip):
        try:
            command = 'show bgp neighbor ' + neighbor_ip
            output = self.sendcommand(command)
            output = self.head(output, 20)
            # output = output.split('\n')
            # first = output[:20]
            # output = '\n'.join(first)
            return output
        except Exception as e:
            return 'Error'

    def get_bgp_connection(self, neighbor_ip):
        try:
            bgp_neighbor = self.get_bgp_neighbor(neighbor_ip)
            local_ip = commandparser.CommandParser('./parser/show_bgp_neighbor.textfsm', bgp_neighbor).get_first_index()[0]
            command = 'show interfaces terse | match ' + local_ip
            output = self.sendcommand(command)
            output = self.head(output, 1)
            return output
        except Exception as e:
            return 'Error'   

    def get_interface_description(self, neighbor_ip) -> dict:
        try: 
            interface_connection = self.get_bgp_connection(neighbor_ip)
            interface = commandparser.CommandParser('./parser/show_int_terse.textfsm', interface_connection).get_first_index()[0]
            command = 'show configuration interfaces ' + interface + ' | display set'
            interface_description = self.sendcommand(command)
            command2 = 'show interfaces ' + interface
            validate_interface = self.sendcommand(command2)
            return {"interface_description" : interface_description, "validate_interface" : validate_interface}
        except Exception as e:
            return 'Error'

if __name__ == "__main__":
    print('This should only print during testing of this class ***********************************************************************')
