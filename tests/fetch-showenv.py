import textfsm
import production.incidentrepo as incidentrepo

#password goes here
ssh_username = "svc-voy-ansible"
ssh_password = "K1oz(q_4sjqAIl=zia"
snow_username = 'prod-powerautomate'
snow_password = '0t$aSfJ2*^l6y!(V'
   
# ip_address = "146.40.173.7"
url = 'https://chevronbox.service-now.com'

repository = incidentrepo.Incident_repository(baseurl=url, user_name=snow_username, password=snow_password)
  
def display_environment(nd):
    output = nd.get_env_details()
    return parse_text('./parser/show_env_all.textfsm', output)

def display_inv_sn(nd):
    output = nd.get_inventory()
    return parse_text('./parser/show_inventory.textfsm', output)

def parse_text(url,output):
    template = open(url)
    results_template = textfsm.TextFSM(template)
    parsed_results = results_template.ParseText(output)
    return parsed_results

def find_bad_serial():
    ps1 = "Power Supply 1"
    PS2 = Power Supply 2
    1A = Power Supply A
    1B = Power Supply B
    return serial


def parse_text(url,output):
    template = open(url)
    results_template = textfsm.TextFSM(template)
    parsed_results = results_template.ParseText(output)
    return parsed_results
   
def single_device_operations(username, password, ip_address):
    import networkdevice
    nd = networkdevice.IOS_device(ip_address, username, password)
    if nd.good_ssh_connection:
        parsed_results = display_environment(nd)
        for items in parsed_results:
            if any([('Bad' in items & items[2] is None), ('Not Present' in items & items[2] is None) , ('No Input Power' in items & items[2] is None)]):
                
                
                serial_nums = display_inv_sn(nd)
                result = {
                    'IP address' : nd.ip,
                    'Is Alive' : nd.is_alive,
                    'Good SSH Connection' : nd.good_ssh_connection,
                    'Environment_details' : parsed_results,
                    'Serial_nums' : find_bad_serial(serial_nums)
                }
                return result
        result = {
            'IP address' : nd.ip,
            'Is Alive' : nd.is_alive,
            'Good SSH Connection' : nd.good_ssh_connection,
            'Environment_details' : parsed_results,
        }
    else:
        result = {
            'IP address' : ip_address,
            'Is Alive' : False,
            'Good SSH Connection' : False,
            'Environment_details' : []
        }
    return result

def get_incident():
    params = {
        'number': 'INC01634588',
    }
    incident = repository.get_incident(params=params)
    return incident

# def post_incident():
#     params = {
#         'number': '123213',
#     }
#     incident = repository.update_ticket(params=params)
#     return incident

def Main():
    print(incident.incident_num)
    print(incident.ip_address)
    a = single_device_operations(ssh_username, ssh_password, incident.ip_address)
    print(a)
    repository.post_incident(params=a):

if __name__ == "__main__":
    Main()