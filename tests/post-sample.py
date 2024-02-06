import textfsm
import requests
import json
from datetime import datetime

class Node(object):
    def __init__(self, hostname, cpu_util, mem_util, disk_util):
        self.hostname = hostname
        self.cpu_util = computed_cpu_util(cpu_util)
        self.mem_util = mem_util
        self.disk_util = str(disk_util.strip('%'))

def computed_cpu_util(cpu_util):
    cpu_float = float(cpu_util.replace("%",""))
    return (10000-(cpu_float*100))/100
    #return str((10000-(cpu_float*100))/100)+'%'

template = open('./parser/cucm_show_status.textfsm')
results_template = textfsm.TextFSM(template)
content2parse = open('Commandlogs.txt')
content = content2parse.read()
parsed_results = results_template.ParseText(content)
print(parsed_results)
my_list = []

# Maps attribute to items in parsed_resutls list
for attri in parsed_results:
    mem_util = round(float(attri[3])/float(attri[2])*100,2)
    hostname = attri[0]
    cpu_util = attri[1]
    disk_util = attri[4]
    my_list.append(Node(hostname,cpu_util,mem_util,disk_util))       
      
my_list2 = [obj.__dict__ for obj in my_list]
print(my_list2)
for a in my_list2:
    payload = []
    body = {
        'hostname' : a['hostname'],
        'cpu_util' : int(a['cpu_util']),
        'disk_util' : int(a['disk_util']),
        'mem_util' : int(a['mem_util']),
        'datetime' : datetime.now().strftime("%H:%M:%S")
    }    
    print(body)
    payload.append(body)
    pbi_url=R'https://api.powerbi.com/beta/fd799da1-bfc1-4234-a91c-72b3a1cb9e26/datasets/3a43aaee-8776-4623-9897-21bcffed7f06/rows?ctid=fd799da1-bfc1-4234-a91c-72b3a1cb9e26&redirectedFromSignup=1&key=rI3NYNc5zyCpbPfZmK%2F%2F1bGISMPkmnGnSykQMRDzgJB81xMvyMA%2BmK3ajmbKFvhvGVzvJQZ2Vzj%2F%2B1QCs6Gmuw%3D%3D'
    print(requests.post(url=pbi_url, data=json.dumps(payload)))