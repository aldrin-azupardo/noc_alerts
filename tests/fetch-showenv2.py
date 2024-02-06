import argparse, json, textfsm

username = "svc-voy-ansible"
password = "K1oz(q_4sjqAIl=zia"
ip_address = "146.40.173.7"
# ip_address = "146.36.4.106"

def parse_environment(nd):
    output = nd.get_env_details()
    template = open('./parser/show_env_all.textfsm')
    results_template = textfsm.TextFSM(template)
    # header = results_template.header
    parsed_results = results_template.ParseText(output)
    # print(parsed_results)
    return parsed_results

def display_inv_sn(nd):
    output = nd.get_inventory()
    template = open('./parser/show_inventory.textfsm')
    results_template = textfsm.TextFSM(template)
    parsed_results = results_template.ParseText(output)
    # print(parsed_results)
    return parsed_results

def single_device_operations(username, password, ip_address):
    import networkdevice
    nd = networkdevice.IOS_device(ip_address, username, password)
    parsed_results = parse_environment(nd)
    print(parsed_results)
    # if any(['Bad' in parsed_results[1], 'Not Present' in parsed_results[1], 'No Input Power' in parsed_results[1]]):
    #     serial_nums = display_inv_sn(nd)
    # else:
    #     print('Do nothing')
    if nd.good_ssh_connection:
        # tacacs = get_tacacs(nd)
        var1 = display_inv_sn(nd) 
        
        print(parsed_results)
        result = {
            # 'Hostname' : hostname,
            'IP address' : nd.ip,
            'Is Alive' : nd.is_alive,
            'Good SSH Connection' : nd.good_ssh_connection,
            'Environment_details' : parsed_results
            # 'Current tacacs' : tacacs,
        }
    else:
        result = {
            'IP address' : ip_address,
            'Is Alive' : False,
            'Good SSH Connection' : False,
            'Environment_details' : []
        }
    return result

def Main():
    a = single_device_operations(username, password, ip_address)
    print(a)

if __name__ == "__main__":
    Main()