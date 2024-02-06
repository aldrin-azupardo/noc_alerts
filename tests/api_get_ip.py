from requests.auth import HTTPBasicAuth
import requests
import re, json

snow_username = 'prod-powerautomate'
snow_password = '0t$aSfJ2*^l6y!(V'
# snow_username = 'svc-naservicenow'
# snow_password = 'BFup8@0k02Wm$6y4'
# incident = 'INC02137751'
incident = 'INC01930663'

url = f'https://chevronbox.service-now.com/api/now/table/incident?number={incident}'
headers = {"Content-Type":"application/json","Accept":"application/json"}
response = requests.get(url, auth=HTTPBasicAuth(snow_username, snow_password), headers=headers)
files = response.json()
myresult = files['result']
## convert response into json and output to a file
# json_string = json.dumps(files,indent=2)
# with open('output_api_file.txt', 'w')as f:
#     f.write(json_string)

result = myresult[0]
print(result['description'])
incident_description = result['description']
ip_address_pattern = re.compile(r'IP\sAddress\:\s.*')
ip_address = re.findall(ip_address_pattern, incident_description)
ip_address = ip_address[0].split()
ip_address = ip_address[2]


# for result in myresult:
#     # print(result['number'])
#     incident_description = result['description']
#     ip_address_pattern = re.compile(r'IP\sAddress\:\s.*')
#     ip_address = re.findall(ip_address_pattern, incident_description)
#     ip_address = ip_address[0].split()
#     ip_address = ip_address[2]
