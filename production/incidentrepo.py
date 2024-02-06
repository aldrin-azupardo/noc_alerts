from requests.auth import HTTPBasicAuth
import requests
import re
import json

"""Class Usage
def call():
    params = {
        'sysparm_query': '',
        'assignment_group': 'a27a5fc6dbb33f002b53ab92ca9619ba',
        'state':'1^descriptionLIKEGNOC - NA - Fault^assigned_toISEMPTY'
    }

    # url = 'https://chevron.service-now.com'
    # url = 'https://chevronbox.service-now.com'
    repository = IncidentRepository(baseurl=url)
    incident = repository.get_incident(params=params)
    incident.incident_num
    incident.ip_address
"""

class Incident(object):
    def __init__(self, incident_num, ip_address, neighbor_ip, interface, device_vendor):
        self.incident_num = incident_num
        self.ip_address = ip_address
        self.neighbor_ip = neighbor_ip
        self.interface = interface
        self.device_vendor = device_vendor

class IncidentRepository(object):
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    def __init__(self, baseurl, user_name, password):
        print("Init incidentrepo.py")
        self.baseurl = baseurl
        self.user_name = user_name
        self.password = password
        self.sys_id = None

    def get_incident(self, params):
        url = self.baseurl + '/api/now/table/incident'
        response = requests.get(url, auth=HTTPBasicAuth(self.user_name, self.password), params=params, headers=self.headers)
        files = response.json()
        myresult = files['result']
        result = myresult[0]
        incident_num = result['number']
        incident_description = result['description']
        ip_address = self.parse_description(r'IP\sAddress\:\s.*', incident_description)
        neighbor_ip = self.parse_description(r'Neighbor\sIP\:\s.*', incident_description)
        interface = self.get_int_from_api(r'Node\:\s.*', incident_description)
        device_vendor = self.device_vendor(r'Vendor\:\s.*', incident_description)
        self.sys_id = result['sys_id']
        return Incident(incident_num, ip_address, neighbor_ip, interface, device_vendor)

    def put_incident(self, params):
        url = self.baseurl + '/api/now/table/incident/'+ self.sys_id
        requests.put(url, verify=False, auth=HTTPBasicAuth(self.user_name, self.password), json={"work_notes": params})
   
    def parse_description(self, pattern, description):
        pattern = re.compile(pattern)
        parsed_result = re.findall(pattern, description)
        if not parsed_result:
            return None
        parsed_result = parsed_result[0].split(':')[1].lstrip()
        parsed_result = parsed_result.split()[0] 
        return parsed_result

    def get_int_from_api(self, pattern, description):
        pattern = re.compile(pattern)
        parsed_result = re.findall(pattern, description)
        parsed_result = parsed_result[0].split()
        parsed_result = parsed_result[-1]
        return parsed_result

    def device_vendor(self, pattern, description):
        pattern = re.compile(pattern)
        parsed_result = re.findall(pattern, description)
        parsed_result = parsed_result[0].split()
        parsed_result = parsed_result[1]
        return parsed_result