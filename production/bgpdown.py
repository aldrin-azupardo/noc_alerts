from triage import NetworkTriage

class BGPTriage(NetworkTriage):
    def __init__(self, networkDevice):
        super().__init__(networkDevice)

    def operate(self) -> dict:
        bgp_summary = self.networkDevice.get_bgp_summary(self.networkDevice.neighbor_ip)
        bgp_neighbor = self.networkDevice.get_bgp_neighbor(self.networkDevice.neighbor_ip)
        bgp_connection = self.networkDevice.get_bgp_connection(self.networkDevice.neighbor_ip)
        interface_description = self.networkDevice.get_interface_description(self.networkDevice.neighbor_ip)
        if self.networkDevice.good_ssh_connection:
            try:
                result = {
                    'IP address' : self.networkDevice.ip,
                    'Is Alive' : self.networkDevice.is_alive,
                    'Good SSH Connection' : self.networkDevice.good_ssh_connection,
                    '\n#show bgp summary | match <neighbor_ip>': '\n' + bgp_summary  + '\n',
                    '#show bgp neighbor' : '\n' + bgp_neighbor + '\n',
                    '#show interfaces terse | match <local_ip>' : '\n' + bgp_connection + '\n',
                    '#show configuration interfaces' : '\n' + interface_description['interface_description'],
                    '#show interfaces' :  '\n' + interface_description['validate_interface']
                }
            except:
                result = {
                    'IP address' : self.networkDevice.ip,
                    'Is Alive' : self.networkDevice.is_alive,
                    'Good SSH Connection' : self.networkDevice.good_ssh_connection,
                    '\n#sh bgp summary | include <neighbor_ip>': '\n' + bgp_summary  + '\n',
                    '#show ip bgp neighbor <neighbor_ip>' : '\n' + bgp_neighbor + '\n',
                    '#sh ip int br | inc <local_host>' : '\n' + bgp_connection + '\n',
                    '#sh int <interface>' : '\n' + interface_description['interface_description']
                }
        else:
            result = {
                'IP address' : self.networkDevice.ip,
                'Is Alive' : False,
                'Good SSH Connection' : False,
                'Log': None,
                'Result': None
            }

        singularString = ""
        for key, result in result.items():
             singularString = singularString + (key + " : " + str(result)) + "\n"
        print('Updating SNOW ticket')
        self.networkDevice.put_incident(singularString)
        return result