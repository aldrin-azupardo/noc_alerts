import requests
import json
from requests.auth import HTTPBasicAuth
import re
import time
import timeit
import netmiko
from netmiko import Netmiko
from getpass import getpass
from ntc_templates.parse import parse_output
import os
import sys
import subprocess
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)

#variable from ADO
snow_username = str(sys.argv[3])
snow_password = str(sys.argv[4])
spec_username = str(sys.argv[1])
spec_password = str(sys.argv[2])
secret = str(sys.argv[2])
PreIncident= str(sys.argv[5])
print(PreIncident)

#USE for email module
sender_email = "no-reply@chevron.com"
receiver_email = ["paulomiloescano@chevron.com", "GFulgencio@chevron.com"]

#function to send email
def send_email(subject,body):
# Create a multipart message and set headers
    for x in receiver_email:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = x
        message["Subject"] = subject
        message["Bcc"] = x
    # Add body to email
        message.attach(MIMEText(body, "plain"))
   
        text = message.as_string()
    
    # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP('hou150.mox-mx.chevron.net', 25) as server:
        #server.login(sender_email, password)
            server.sendmail(sender_email, x, text)

def ping_device(Ip_address):
    output = (os.system(f'ping {Ip_address} -c 1'))
    ping_count = 4
    process = subprocess.Popen(['ping', Ip_address, '-c', str(ping_count)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = process.stdout.read()
    email_text = result.decode()
    return output, email_text

class CVXNetwork:
    def __init__(self, ip=None, device_type=None,username=None, password=None):
        self.conn_data = {
            'ip': ip,
            'username': username,
            'password': password,
            'device_type': device_type
            }
    def login(self):
        return netmiko.ConnectHandler(**self.conn_data)
                
class CiscoIOSShipping(CVXNetwork):
    def __init__(self, username=None, password=None):
        super().__init__(ip='146.46.130.138', device_type='cisco_ios',
        username=spec_username, password=spec_password)

    def ping_shipping(self,device_ip):
        conn = self.login()
        ping_from_source = conn.send_command(f'ping {device_ip} source 146.46.130.138', expect_string=r"#",read_timeout=90, use_textfsm = False)
        self.ping_from_source =  ping_from_source
    
class Snow_rest:
    def __init__(self, base_url='https://chevronbox.service-now.com/api/now/table',snow_username=snow_username, snow_password=snow_password):
        self.snow_username = snow_username
        self.snow_password = snow_password
        self.base_url = base_url
        self.headers = {
            "Accept": "application/json",
            "Content-type": "application/json"
        }

    def get_incident_description(self, Incident):
        self.Incident = Incident
        the_url = self.base_url+'/incident?number='+self.Incident
        get_incident_description = requests.get(the_url, verify=False, auth=HTTPBasicAuth(self.snow_username, self.snow_password), headers = self.headers).json()
        self.get_incident_description = get_incident_description['result'][0]
    
    def get_incident_info(self):
        result = self.get_incident_description
        inc_sys_id = result['sys_id']
        self.inc_sys_id = inc_sys_id
        incident_number = result['number']
        self.incident_number = incident_number
        incident_description = result['description']
        self.incident_description = incident_description
        Ip_address = re.compile(r'\bIP\sAddress\:\s.*')
        Ip_address = re.findall(Ip_address, incident_description)
        Ip_address = Ip_address[0].split()
        self.Ip_address = Ip_address[2]
        Device_Name = re.compile(r'\bDevice\sName\:\s.*')
        Device_Name = re.findall(Device_Name, incident_description)
        Device_Name = Device_Name[0].split()
        self.Device_Name = Device_Name[2]
        Location = re.compile(r'\bLocation\:\s.*')
        Location= re.findall(Location, incident_description)
        Site_Code= Location[0].split()
        self.Site_Code= Site_Code[1]
        self.Location = ",".join(Location)
        Device_Model = re.compile(r'\bModel\:\s.*')
        Device_Model = re.findall(Device_Model, incident_description)
        self.Device_Model = ",".join(Device_Model)
        Device_Details = re.compile(r'\bDevice\sDetails\:\s.*')
        Device_Details = re.findall(Device_Details, incident_description)
        self.Device_Details = ",".join(Device_Details)
        Alert_Details = re.compile(r'\bAlert\sDetails\:\s.*')
        Alert_Details = re.findall(Alert_Details, incident_description)
        self.Alert_Details = ",".join(Alert_Details)
    
    def get_site_contact(self, SiteCode):
        self.SiteCode = SiteCode
        the_url = self.base_url+'/u_cvx_na_contacts?u_active=true&u_location_guid.u_locationlegacycode='+self.SiteCode
        get_site_contact = requests.get(the_url, verify=False, auth=HTTPBasicAuth(self.snow_username, self.snow_password), headers = self.headers).json()
        get_site_contact  = get_site_contact['result']
        url_POC_list = []
        POC_list = []
        contact_type_list = []
        new_contact_type_list = []
        Final_POC_List = []
        for i in get_site_contact:
            url_POC_list.append(i['u_group_contact'])
            url_POC_list.append(i['u_user_contact'])
            POC_list.append(i['u_other'])
        url_POC_list = [x for x in url_POC_list if x]
        for j in get_site_contact:
            contact_type_list.append(j['u_contact_type'])
        for i in contact_type_list:
            if i == '1':
                new_contact_type_list.append('On-Site Smart Hand Contact')
            elif i == '2':
                new_contact_type_list.append('IT Support Contact')
            elif i == '3':
                new_contact_type_list.append('BU IT Management')
            elif i == '10':
                new_contact_type_list.append('I&E Lead')
            elif i == '11':
                new_contact_type_list.append('ServiceNow Assignment Group')
            else:
                new_contact_type_list.append('Not defined')
        if len(url_POC_list) != 0:
            new_list = []
            for j in url_POC_list:
                new_list.append(j['link'])
        
            for my_url in new_list:
                my_res_poc = requests.get(my_url, verify=False, auth=HTTPBasicAuth(self.snow_username, self.snow_password),headers = self.headers).json()
                my2_file_poc = my_res_poc['result']
                for i, j in my2_file_poc.items():
                    if i == 'name':
                        POC_list.append(j)
        self.site_contact = [e for e in POC_list if len(e.strip())!=0]
    
    def get_circuit(self, DeviceName):
        self.DeviceName = DeviceName
        circuit_list = []
        the_url = self.base_url+'/u_cvx_na_data_circuit?sysparm_query=u_source_routerLIKE'+self.DeviceName+'%5EORu_terminating_device_aLIKE'+self.DeviceName
        get_circuit = requests.get(the_url, verify=False, auth=HTTPBasicAuth(self.snow_username, self.snow_password), headers = self.headers).json()
        myresult_data = get_circuit['result']
        k = 1
        for i in myresult_data:
            circuit_list.append(f'*****{k} DATA_CIRCUIT_INFO*****')
            circuit_list.append('Carrier: ' + i['asset_tag'])
            circuit_list.append('Name: ' + i['name'])
            circuit_list.append('Circuit id: ' + i['u_circuit_id'])
            circuit_list.append('Remote_router: ' + i['u_remote_router'])
            k += 1
        self.circuit_list = circuit_list
    
    
    def add_work_notes(self, work_notes, SysId):
        self.work_notes = work_notes
        self.SysId = SysId
        the_url = self.base_url+'/incident/'+self.SysId
        add_comment = requests.put(the_url, verify=False, auth=HTTPBasicAuth(self.snow_username, self.snow_password), json={"work_notes":work_notes})


def main():
    get_incident = Snow_rest()
    get_incident.get_incident_description(PreIncident)
    get_incident.get_incident_info()
    get_incident.get_site_contact(get_incident.Site_Code)

    if "IsManaged: BU" in get_incident.incident_description and "http://HOMCBUSWCLI:80/" in get_incident.incident_description:
        print('This can be routed to industrial ops')
        subject = (f'ITOC pre-email RE: {get_incident.incident_number} MCBU-PCN incident {get_incident.Device_Name}')
        body = (f'Hi Team\n\nOur team recieved a MCBU-PCN incident\n\nDevice_Name:{get_incident.Device_Name}\nIp_Address:{get_incident.Ip_address}\n{get_incident.Location}\n{get_incident.Device_Details}\n{get_incident.Alert_Details}\nServiceNow contacts: {get_incident.site_contact}\n\nPlease manually route this to NETWORK – Industrial Ops\n\nRegards\nIT Operations Center (ITOC)')           
        send_email(subject,body)
    elif "Is_PCN: True" in get_incident.incident_description and "http://HOMCBUSWCLI:80/" in get_incident.incident_description:
        print('This can be routed to industrial ops')
        subject = (f'ITOC pre-email RE: {get_incident.incident_number} MCBU-PCN incident {get_incident.Device_Name}')
        body = (f'Hi Team\n\nOur team recieved a MCBU-PCN incident\n\nDevice_Name:{get_incident.Device_Name}\nIp_Address:{get_incident.Ip_address}\n{get_incident.Location}\n{get_incident.Device_Details}\n{get_incident.Alert_Details}\nServiceNow contacts: {get_incident.site_contact}\n\nPlease manually route this to NETWORK – Industrial Ops\n\nRegards\nIT Operations Center (ITOC)')
        send_email(subject,body)
    elif "F09132 / 2315 West Dexter, Pecos, TX / USA / Americas /US-Noble-NA-Utility-PCN" in get_incident.incident_description:
        print('This can be routed to industrial ops - PERMIAN MCBU_PCN')
        subject = (f'ITOC pre-email RE: {get_incident.incident_number} Permian MCBU-PCN incident {get_incident.Device_Name}')
        body = (f'Hi Team\n\nOur team recieved a Permian MCBU-PCN incident\n\nDevice_Name:{get_incident.Device_Name}\nIp_Address:{get_incident.Ip_address}\n{get_incident.Location}\n{get_incident.Device_Details}\n{get_incident.Alert_Details}\nServiceNow contacts: {get_incident.site_contact}\n\nPlease manually route this to NETWORK – Industrial Ops\n\nRegards\nIT Operations Center (ITOC)')           
        send_email(subject,body)
    elif "Shipping" in get_incident.incident_description:
        print('This is a shipping incident')
        output, email_text = ping_device(get_incident.Ip_address)
        if output == 0:
            print('kindly check it seems device is already up')
            subject = (f'ITOC pre-email RE: {get_incident.incident_number} Node down alert on device {get_incident.Device_Name}')
            body = (f'Hi Team\n\nOur team recieved a Node DOWN Alert\n\nDevice_Name:{get_incident.Device_Name}\nIp_Address:{get_incident.Ip_address}\n{get_incident.Location}\n{get_incident.Device_Details}\n{get_incident.Alert_Details}\nServiceNow contacts: {get_incident.site_contact}\n\nPing Result:\n\n********************\n{email_text}********************\nIP:{get_incident.Ip_address} IS NOW REACHABLE\n\nKindly check and advice\n\nRegards\nIT Operations Center (ITOC)')             
            send_email(subject,body)
        else:
            device_test1 = CiscoIOSShipping(spec_username, spec_password)
            device_test1.ping_shipping(get_incident.Ip_address)
            subject = (f'ITOC pre-email RE: {get_incident.incident_number} Node down alert on device {get_incident.Device_Name}')
            body = (f'Hi Team\n\nOur team recieved a Node DOWN Alert\n\nDevice_Name:{get_incident.Device_Name}\nIp_Address:{get_incident.Ip_address}\n{get_incident.Location}\n{get_incident.Device_Details}\n{get_incident.Alert_Details}\nServiceNow contacts: {get_incident.site_contact}\n\nPing Result:\n\n********************\n{email_text}********************\n FleetBroadband connection status:\nCHVPKRE35-SAN520#ping {get_incident.Ip_address} source 146.46.130.138\n\n{device_test1.ping_from_source}\n\nKindly check and advice\n\nRegards\nIT Operations Center (ITOC)')           
            send_email(subject,body)
    elif "Node Down" in get_incident.incident_description:
        print('This is a Node down')
        output, email_text = ping_device(get_incident.Ip_address)
        if output == 0:
            print('kindly check it seems device is already up')
            subject = (f'ITOC pre-email RE: {get_incident.incident_number} Node down alert on device {get_incident.Device_Name}')
            body = (f'Hi Team\n\nOur team recieved a Node DOWN Alert\n\nDevice_Name:{get_incident.Device_Name}\nIp_Address:{get_incident.Ip_address}\n{get_incident.Location}\n{get_incident.Device_Details}\n{get_incident.Alert_Details}\nServiceNow contacts: {get_incident.site_contact}\n\nPing Result:\n\n********************\n{email_text}********************\nIP:{get_incident.Ip_address} IS NOW REACHABLE\n\nKindly check and advice\n\nRegards\nIT Operations Center (ITOC)')             
            send_email(subject,body)
            get_incident.add_work_notes(body, get_incident.inc_sys_id)     
        else:
            print('device still down')
            if "RA" in get_incident.Device_Name or "ra" in get_incident.Device_Name or "CE" in get_incident.Device_Name or "ce" in get_incident.Device_Name or "RL" in get_incident.Device_Name or "rl" in get_incident.Device_Name or "PE" in get_incident.Device_Name or "pe" in get_incident.Device_Name or "RD" in get_incident.Device_Name or "rd" in get_incident.Device_Name or "RM" in get_incident.Device_Name or "rm" in get_incident.Device_Name or "RT" in get_incident.Device_Name or "rt" in get_incident.Device_Name or "RS" in get_incident.Device_Name or "rs" in get_incident.Device_Name or "RB" in get_incident.Device_Name or "rb" in get_incident.Device_Name or "RG" in get_incident.Device_Name  or "RE" in get_incident.Device_Name or "re" in get_incident.Device_Name:
                get_incident.get_circuit(get_incident.Device_Name)
                subject = (f'ITOC pre-email RE: {get_incident.incident_number} Node down alert on device {get_incident.Device_Name}')
                body = (f'Hi Team\n\nOur team recieved a Node DOWN Alert\n\nDevice_Name:{get_incident.Device_Name}\nIp_Address:{get_incident.Ip_address}\n{get_incident.Location}\n{get_incident.Device_Details}\n{get_incident.Alert_Details}\nServiceNow contacts: {get_incident.site_contact}\nCircuit_details: {get_incident.circuit_list}\n\nPing Result:\n\n********************\n{email_text}********************\nIP:{get_incident.Ip_address} IS STILL UNREACHABLE\n\nKindly check and advice\n\nRegards\nIT Operations Center (ITOC)')           
                send_email(subject,body)
                get_incident.add_work_notes(body, get_incident.inc_sys_id)   
            else:
                subject = (f'ITOC pre-email RE: {get_incident.incident_number} Node down alert on device {get_incident.Device_Name}')
                body = (f'Hi Team\n\nOur team recieved a Node DOWN Alert\n\nDevice_Name:{get_incident.Device_Name}\nIp_Address:{get_incident.Ip_address}\n{get_incident.Location}\n{get_incident.Device_Details}\n{get_incident.Alert_Details}\nServiceNow contacts: {get_incident.site_contact}\n\nPing Result:\n\n********************\n{email_text}********************\nIP:{get_incident.Ip_address} IS STILL UNREACHABLE\n\nKindly check and advice\n\nRegards\nIT Operations Center (ITOC)')           
                send_email(subject,body)
                get_incident.add_work_notes(body, get_incident.inc_sys_id)             
    else:
        print("what is this alert")

if __name__ == '__main__':
    main()
