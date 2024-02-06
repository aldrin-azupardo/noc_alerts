import requests
import json
from requests.auth import HTTPBasicAuth
import re

class Snow_rest:
    def __init__(self, base_url='https://chevronbox.service-now.com/api/now/table',snow_username='prod-powerautomate', snow_password='0t$aSfJ2*^l6y!(V'):
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
        print(the_url)
        get_incident_description = requests.get(the_url, verify=False, auth=HTTPBasicAuth(self.snow_username, self.snow_password)).json()
        self.myresult = get_incident_description['result']
        print(self.myresult)
       
    def get_ip_address(self):
        result = self.myresult
        for d in result:
            incident_number = d['number']
            incident_description = d['description']
            Ip_address = re.compile(r'\bIP\sAddress\:\s.*')
            Ip_address = re.findall(Ip_address, incident_description)
            Ip_address = Ip_address[0].split()
            self.Ip_address = Ip_address[2]
  
    def get_sys_id(self):
        result = self.myresult
        for d in result:
            inc_sys_id = d['sys_id']
            self.inc_sys_id = inc_sys_id
            print(self.inc_sys_id)

    def add_comment(self):
        the_url = self.base_url+'/incident/'+self.inc_sys_id
        add_comment = requests.put(the_url, verify=False, auth=HTTPBasicAuth(self.snow_username, self.snow_password), json={"work_notes":"test3"})


def main():
    get_incident1 = Snow_rest()
    get_incident1.get_incident_description('INC02113305')
    get_incident1.get_sys_id()
    get_incident1.add_comment()    


if __name__ == '__main__':

        main()

