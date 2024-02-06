import json

parsed_results = [['host1', '32.65%', '97%'], ['host2', '93.30%', '70%'], ['host3', '92.42%', '71%']]

print(parsed_results)
 
cpu_idle = [cidle[1] for cidle in parsed_results]
for a in cpu_idle:
    cpu_float = float((a).strip('%'))
    cpu_util = (10000-(cpu_float*100))/100
    print(str(float(cpu_util))+ '%')  
 
class Node(object):
    def __init__(self, hostname, cpu_util, disk_util):
        self.hostname = hostname
        self.cpu_util = cpu_util
        self.disk_util = disk_util
         
my_list = []

for nodes in parsed_results:
    my_list.append(Node(nodes[0], nodes[1],nodes[2]))       

my_list2 = [obj.__dict__ for obj in my_list]
print(my_list2)
json_string = json.dumps(my_list2,indent=2)
#print(json_string)
with open('test.json', 'w') as file1:
    file1.write(json_string)