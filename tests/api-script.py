#Need to install requests package for python
#easy_install requests
import requests
import json
import csv


# Set the request parameters -- with IP Address
url = 'https://chevronbox.service-now.com/api/now/table/incident'
# Eg. User name="admin", Password="admin" for this code sample.
user = 'svc-naservicenow'
pwd = 'BFup8@0k02Wm$6y4'
# INC01930663
# Set proper headers
headers = {"Content-Type":"application/json","Accept":"application/json"}

# Do the HTTP request
response = requests.get(url, auth=(user, pwd), headers=headers )

# Check for HTTP codes other than 200
if response.status_code != 200: 
    print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
    exit()

# # Decode the JSON response into a dictionary and use the data

data = response.json()
# print(data)
with open('data.json', 'w') as fp:
    json.dump(data, fp, indent =4)

# #Extract specific data and conver to CSV file

# with open("inventory.csv", "w") as file:
#     csv_file = csv.writer(file,lineterminator='\n')
#     csv_file.writerow(["Name", "ip_address", "serial_number"])
#     for item in data["result"]:
#         csv_file.writerow([item['u_ci_id'],item['ip_address'],item['serial_number']])