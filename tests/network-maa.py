import requests
import json
from requests.auth import HTTPBasicAuth
import re
import time
import timeit
from netmiko import Netmiko
from getpass import getpass
from netmiko import ConnectHandler
from ntc_templates.parse import parse_output
import os
import sys
import subprocess
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#inprogress
#url ='https://chevron.service-now.com/api/now/table/incident?sysparm_query=assignment_group=a27a5fc6dbb33f002b53ab92ca9619ba^state=2^descriptionLIKEGNOC - NA - Fault - Node Down'

#NewFault-unassigned
url ='https://chevron.service-now.com/api/now/table/incident?sysparm_query=assignment_group=a27a5fc6dbb33f002b53ab92ca9619ba^state=1^descriptionLIKEGNOC - NA - Fault^assigned_toISEMPTY'


#USE for email module
sender_email = "no-reply@chevron.com"
receiver_email = "gnoc1@chevron.com"

#function to send email
def send_email():
# Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email

    # Add body to email
    message.attach(MIMEText(body, "plain"))
     
    text = message.as_string()
     
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP('hou150.mox-mx.chevron.net', 25) as server:
        #server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

#USE username on YML file
snow_username = str(sys.argv[3])
snow_password = str(sys.argv[4])
username = str(sys.argv[1])
password = str(sys.argv[2])
secret = str(sys.argv[2])

def access_device(device_type, command1, command2, command3):
    cisco1 = {
            "device_type": device_type, #cisco_nxos for nexus and cisco_ios for cisco
            "host": Ip_address,
            "username": username,
            "password": password,
            "secret" : secret,
    }
    net_connect = ConnectHandler(**cisco1)
    time.sleep(8)
    net_connect.enable()
    
    time.sleep(8)		
    print(net_connect.find_prompt())
    time.sleep(8)
    output = net_connect.send_command(command1)
    time.sleep(8)
    output1 = net_connect.send_command(command2)
    time.sleep(8)
    output2 = net_connect.send_command(command3)
    net_connect.disconnect()
    print()
    return output, output1, output2

#Request list of incident to ServiceNow(API)
res = requests.get(url, verify=False, auth=HTTPBasicAuth(snow_username, snow_password))

#Convert file to JSON
files = res.json()

#Convert JSON dict to List
myresult = files['result']

#Count number of incident
print(len(myresult))

#get details of incindent on Description - Pharse information needed
for d in myresult:
    incident_number = d['number']
    incident_description = d['description']
    #Parse info needed on Incident description
    Ip_address = re.compile(r'\bIP\sAddress\:\s.*')
    Ip_address = re.findall(Ip_address, incident_description)
    Ip_address = Ip_address[0].split()
    Ip_address = Ip_address[2]
    Device_Name = re.compile(r'\bDevice\sName\:\s.*')
    Device_Name = re.findall(Device_Name, incident_description)
    Device_Name = Device_Name[0].split()
    Device_Name = Device_Name[2]
    Location = re.compile(r'\bLocation\:\s.*')
    Location= re.findall(Location, incident_description)
    Site_Code= Location[0].split()
    Site_Code= Site_Code[1]
    Location = ",".join(Location)
    Device_Model = re.compile(r'\bModel\:\s.*')
    Device_Model = re.findall(Device_Model, incident_description)
    Device_Model = ",".join(Device_Model)
    Device_Details = re.compile(r'\bDevice\sDetails\:\s.*')
    Device_Details = re.findall(Device_Details, incident_description)
    Device_Details = ",".join(Device_Details)
    Alert_Details = re.compile(r'\bAlert\sDetails\:\s.*')
    Alert_Details = re.findall(Alert_Details, incident_description)
    Alert_Details = ",".join(Alert_Details)

    #GET POC list on ServiceNow based from SiteCode
    POC_url = f'https://chevron.service-now.com/api/now/table/u_cvx_na_contacts?u_active=true&u_location_guid.u_locationlegacycode={Site_Code}'
    res_poc = requests.get(POC_url, verify=False, auth=HTTPBasicAuth(snow_username, snow_password))
    files_poc = res_poc.json()
    myresult_poc = files_poc['result']

    url_POC_list = []
    POC_list = []
    contact_type_list = []
    new_contact_type_list = []
    Final_POC_List = []

    for i in myresult_poc:
        url_POC_list.append(i['u_group_contact'])
        url_POC_list.append(i['u_user_contact'])
        POC_list.append(i['u_other'])
    url_POC_list = [x for x in url_POC_list if x] #remove blank space on the list

    for j in myresult_poc:
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
            my_res_poc = requests.get(my_url, verify=False, auth=HTTPBasicAuth(snow_username, snow_password))
            my_files_poc = my_res_poc.json()
            my2_file_poc = my_files_poc['result']
            for i, j in my2_file_poc.items():
                if i == 'name':
                    POC_list.append(j)
    POC_list = [e for e in POC_list if len(e.strip())!=0]
    #POC_list = ",".join(POC_list )
    for i in range(len(new_contact_type_list)):
        Final_POC_List.append(POC_list[i] + ' = ' +  new_contact_type_list[i])
    POC_list = Final_POC_List 




####################################################################NODE DOWN####################################################################################
    if "Node Down" in incident_description:
        print('This is a Node down')
        #test if IP is reachable
        output = (os.system(f'ping {Ip_address} -c 1'))

        #show output of ping result
        ping_count = 4
        process = subprocess.Popen(['ping', Ip_address, '-c', str(ping_count)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        returncode = process.wait()
        result = process.stdout.read()
        email_text = result.decode()
        circuit_list = []


        if output == 0:
            print('kindly check it seems device is already up')
            subject = (f'pre-email RE: {incident_number} Node down alert on device {Device_Name}')
            body = (f'Hi Team\n\nOur team recieved a Node DOWN Alert\n\nDevice_Name:{Device_Name}\nIp_Address:{Ip_address}\n{Location}\n{Device_Details}\n{Alert_Details}\nServiceNow contacts: {POC_list}\n\nPing Result:\n\n********************\n{email_text}********************\nIP:{Ip_address} IS NOW REACHABLE\n\nKindly check and advice\n\nRegards\nMonitoring Automation and Assurance team')             
            send_email()

        else:
            print('device still down')
            if "RA" in Device_Name or "ra" in Device_Name or "CE" in Device_Name or "ce" in Device_Name or "RL" in Device_Name or "rl" in Device_Name or "PE" in Device_Name or "pe" in Device_Name or "RD" in Device_Name or "rd" in Device_Name or "RM" in Device_Name or "rm" in Device_Name or "RT" in Device_Name or "rt" in Device_Name or "RS" in Device_Name or "rs" in Device_Name or "RB" in Device_Name or "rb" in Device_Name or "RG" in Device_Name  or "RE" in Device_Name or "re" in Device_Name:
                data_url = f'https://chevron.service-now.com/api/now/table/u_cvx_na_data_circuit?sysparm_query=u_source_routerLIKE{Device_Name}%5EORu_terminating_device_aLIKE{Device_Name}'
                res_data = requests.get(data_url, verify=False, auth=HTTPBasicAuth(snow_username, snow_password))
                my_files_data = res_data.json()
                myresult_data = my_files_data['result']


                k = 1
                for i in myresult_data:
                    circuit_list.append(f'*****{k} DATA_CIRCUIT_INFO*****')
                    circuit_list.append('Carrier: ' + i['asset_tag'])
                    circuit_list.append('Name: ' + i['name'])
                    circuit_list.append('Circuit id: ' + i['u_circuit_id'])
                    circuit_list.append('Remote_router: ' + i['u_remote_router'])
                    k += 1
                subject = (f'pre-email RE: {incident_number} Node down alert on device {Device_Name}')
                body = (f'Hi Team\n\nOur team recieved a Node DOWN Alert\n\nDevice_Name:{Device_Name}\nIp_Address:{Ip_address}\n{Location}\n{Device_Details}\n{Alert_Details}\nServiceNow contacts: {POC_list}\nCircuit_details: {circuit_list}\n\nPing Result:\n\n********************\n{email_text}********************\nIP:{Ip_address} IS STILL UNREACHABLE\n\nKindly check and advice\n\nRegards\nMonitoring Automation and Assurance team')           
                send_email() 

            else:
                subject = (f'pre-email RE: {incident_number} Node down alert on device {Device_Name}')
                body = (f'Hi Team\n\nOur team recieved a Node DOWN Alert\n\nDevice_Name:{Device_Name}\nIp_Address:{Ip_address}\n{Location}\n{Device_Details}\n{Alert_Details}\nServiceNow contacts: {POC_list}\n\nPing Result:\n\n********************\n{email_text}********************\nIP:{Ip_address} IS STILL UNREACHABLE\n\nKindly check and advice\n\nRegards\nMonitoring Automation and Assurance team')           
                send_email()            
        print('===========================')


####################################################################BGP DOWN####################################################################################
    elif "BGP" in incident_description:
        Neighbor_IP = re.compile(r'\bNeighbor\sIP\:\s.*')
        Neighbor_IP = re.findall(Neighbor_IP, incident_description)
        Neighbor_IP = Neighbor_IP[0].split()
        Neighbor_IP = Neighbor_IP[2]
        print(Neighbor_IP)
        print('This is a BGP down')
        try:
            if "Juniper" in Device_Model or "juniper" in Device_Model:
                command1= f'show bgp summary | match {Neighbor_IP}'
                command2= f'show configuration | match {Neighbor_IP} | display set | except key'
                command3= 'show system uptime'
                output, output1, output2 = access_device('juniper', command1, command2, command3)

                if "Establ" in output:
                    output3 = (f'{Neighbor_IP} BGP is up')
                else:
                    output3 = (f'{Neighbor_IP} BGP is down')
                

            else:
                output, output1, output2 = access_device('cisco_ios', 'show ip bgp summary', 'show interface description', 'show version | inc uptime')
                output_parsed = parse_output(platform="cisco_ios", command="show ip bgp summary", data=output)
                output3='BGP not defined'

                for item in output_parsed:
                    if Neighbor_IP in item['bgp_neigh']:

                        if (item['state_pfxrcd'] == "Idle" or item['state_pfxrcd'] == "Active" or item['state_pfxrcd'] == "Connect" or item['state_pfxrcd'] == "OpenSent" or item['state_pfxrcd'] == "OpenConfirm" ):
                            output3 = (f"{item['bgp_neigh']} neighbor BGP is down")
                        else:
                            output3 = (f"{item['bgp_neigh']} neighbor BGP is up")
               
        except:
            subject = (f'pre-email RE: {incident_number} BGP Down alert on device {Device_Name} Neigbor {Neighbor_IP}')
            body = (f'Hi Team\n\nOur team recieved a BGP Down Alert\n\nDevice_Name:{Device_Name}\nIp_Address:{Ip_address}\nBGP Neighbor:{Neighbor_IP}\n{Location}\n{Device_Details}\n{Alert_Details}\nServiceNow contacts: {POC_list}\n\nResult:\n Unable to access device\nKindly check and advice\n\n\nRegards\n\nMonitoring Automation and Assurance team')             
            send_email()
        
        else:
            subject = (f'pre-email RE: {incident_number} BGP Down alert on device {Device_Name} Neigbor {Neighbor_IP}')
            body = (f'Hi Team\n\nOur team recieved a BGP Down Alert\n\nDevice_Name:{Device_Name}\nIp_Address:{Ip_address}\nBGP Neighbor:{Neighbor_IP}\n{Location}\n{Device_Details}\n{Alert_Details}\nServiceNow contacts: {POC_list}\n\nResult:\n{output}\n\n{output1}\n\n{output3}\n\nKindly check and advice\n\n\nRegards\n\nMonitoring Automation and Assurance team')
            send_email() 
            
        print('===========================')


####################################################################LINK DOWN####################################################################################
    elif "Link Down" in incident_description:
        Interface_Name = re.compile(r'\bInterface\sName\:\s.*')
        Interface_Name = re.findall(Interface_Name, incident_description)
        Interface_Name = Interface_Name[0].split()
        Interface_Name = Interface_Name[2]
        print('This is link down')
        try:
            if "Juniper" in Device_Model or "juniper" in Device_Model:
                command1= f'show interface {Interface_Name}'
                command2= f'show configuration | match {Interface_Name} | display set'
                command3= 'show interfaces descriptions | match nni'
                output, output1, output2 = access_device('juniper', command1, command2, command3)

            elif "Nexus" in Device_Model or "nexus" in Device_Model:
                command1= f'show interface {Interface_Name}'
                command2= f'show run interface {Interface_Name}'
                command3= 'show version | inc uptime'
                output, output1, output2 = access_device('cisco_nxos', command1, command2, command3)
                
            else:
                command1= f'show interface {Interface_Name}'
                command2= f'show run interface {Interface_Name}'
                command3= 'show version | inc uptime'
                output, output1, output2 = access_device('cisco_ios', command1, command2, command3) 
              
        except:
            subject = (f'pre-email RE: {incident_number} Link Down alert on device {Device_Name} Interface {Interface_Name}')
            body = (f'Hi Team\n\nOur team recieved a LinkDown Alert\n\nDevice_Name:{Device_Name}\nIp_Address:{Ip_address}\nInterface:{Interface_Name}\n{Location}\n{Device_Details}\n{Alert_Details}\nServiceNow contacts: {POC_list}\n\nResult:\nUnable to access device\nKindly check and advice\n\n\nRegards\nMonitoring Automation and Assurance team')
            send_email()
            
        
        else:
            subject = (f'pre-email RE: {incident_number} Link Down alert on device {Device_Name} Interface {Interface_Name}')
            body = (f'Hi Team\n\nOur team recieved a LinkDown Alert\n\nDevice_Name:{Device_Name}\nIp_Address:{Ip_address}\nInterface:{Interface_Name}\n{Location}\n{Device_Details}\n{Alert_Details}\nServiceNow contacts: {POC_list}\n\nResult:\n{output}\n{output1}\n{output2}\nKindly check and advice\n\n\nRegards\nMonitoring Automation and Assurance team')
            send_email()

        print('===========================')

####################################################################ISIS DOWN####################################################################################
    elif "ISIS" in incident_description:
        Event_Message = re.compile(r'\bEvent\sMessage\:\s.*')
        Event_Message = re.findall(Event_Message, incident_description)
        ISIS_interface = Event_Message[0].split()
        ISIS_interface = ISIS_interface[19]
        ISIS_interface = ISIS_interface.replace(",", "")
        try:

            command1 = 'show isis adjacency'
            command2 = f'show isis adjacency detail | find {ISIS_interface}'
            command3 = 'show interfaces descriptions | match nni'
            output, output1, output2 = access_device('juniper', command1, command2, command3)
            output_parsed = parse_output(platform="juniper_junos", command="show isis adjacency", data=output)
            print(output_parsed)
            if 'Pattern' in output1:
                command1 = 'show isis adjacency'
                command2 = f'show interface {ISIS_interface}'
                command3 = 'show interfaces descriptions | match nni'
                output, output1, output2 = access_device('juniper', command1, command2, command3)
    
            output3 = f"{ISIS_interface} is down"
    
            for item in output_parsed:
                if (ISIS_interface in item['interface']) and item['state'] == 'Up':
                    output3 = (f"interface {item['interface']} connecting {item['system_id']} ISIS is up")
        except:
            subject = (f'pre-email RE: {incident_number} ISIS Down alert on device {Device_Name}')
            body = (f'Hi Team\n\nOur team recieved a ISIS Down Alert\n\nDevice_Name:{Device_Name}\nIp_Address:{Ip_address}\nInterface_Down:{ISIS_interface}\n{Event_Message}\n{Location}\n{Device_Details}\n{Alert_Details}\nServiceNow contacts: {POC_list}\n\nResult:\n\nUnable to access device\n\nKindly check and advice\n\n\nRegards\nMonitoring Automation and Assurance team')
            send_email()


        else:
            subject = (f'pre-email RE: {incident_number} ISIS Down alert on device {Device_Name}')
            body = (f'Hi Team\n\nOur team recieved a ISIS Down Alert\n\nDevice_Name:{Device_Name}\nIp_Address:{Ip_address}\nInterface_Down:{ISIS_interface}\n{Event_Message}\n{Location}\n{Device_Details}\n{Alert_Details}\nServiceNow contacts: {POC_list}\n\nResult:\n\n{output}\n\n{output1}\n\n{output2}\n\n{output3}\n\nKindly check and advice\n\n\nRegards\nMonitoring Automation and Assurance team')
            send_email()
            print('===========================')

#################################################################POWER-SUPPLY DOWN###############################################################################
    elif "Power Supply" in incident_description:
        print('This is Power supply down')

        try:
            if "Juniper" in Device_Model or "juniper" in Device_Model:
                command1= 'show system alarms'
                command2= 'show chassis alarms'
                command3= 'show chassis hardware'
                output, output1, output2 = access_device('juniper', command1, command2, command3)

            elif "Nexus" in Device_Model or "nexus" in Device_Model:
                command1= 'show environment'
                command2= 'show inventory'
                command3= 'show version | inc uptime'
                output, output1, output2 = access_device('cisco_nxos', command1, command2, command3)
                
            else:
                command1= 'show environment'
                command2= 'show inventory'
                command3= 'show version | inc uptime'
                output, output1, output2 = access_device('cisco_ios', command1, command2, command3) 
              
        except:
            subject = (f'pre-email RE: {incident_number} Power Supply Down alert on device {Device_Name}')
            body = (f'Hi Team\n\nOur team recieved a Power Supply Alert\n\nDevice_Name:{Device_Name}\nIp_Address:{Ip_address}\n{Location}\n{Device_Details}\n{Alert_Details}\nServiceNow contacts: {POC_list}\n\nResult:\nUnable to access device\nKindly check and advice\n\n\nRegards\nMonitoring Automation and Assurance team')
            send_email()
            
        
        else:
            subject = (f'pre-email RE: {incident_number} Power Supply Down alert on device {Device_Name}')
            body = (f'Hi Team\n\nOur team recieved a Power Supply Alert\n\nDevice_Name:{Device_Name}\nIp_Address:{Ip_address}\n{Location}\n{Device_Details}\n{Alert_Details}\nServiceNow contacts: {POC_list}\n\nResult:\n{output}\n{output1}\n{output2}\nKindly check and advice\n\n\nRegards\nMonitoring Automation and Assurance team')
            send_email()

        print('===========================')

######################################################################################################################################################################

    else:
        print("what is this alert")
        print('===========================')