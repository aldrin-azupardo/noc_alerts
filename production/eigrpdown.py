from triage import NetworkTriage

class EIGRPTriage(NetworkTriage):
    def __init__(self, networkDevice):
        super().__init__(networkDevice)

    def operate(self) -> dict:
        eigrp_log = self.networkDevice.get_eigrp_log(self.networkDevice.neighbor_ip)
        eigrp_neighbor = self.networkDevice.get_eigrp_neighbors()
        interface_detail = self.networkDevice.get_interface_detail_with_neighbor_ip(self.networkDevice.neighbor_ip)
        # print(eigrp_log + '\n')
        # print(eigrp_neighbor + '\n')
        print(interface_detail + '\n')
        if self.networkDevice.good_ssh_connection:
            result = {
                'IP address' : self.networkDevice.ip,
                'Is Alive' : self.networkDevice.is_alive,
                'Good SSH Connection' : self.networkDevice.good_ssh_connection,
                '#show log | inc <neighbor_ip>': '\n' + eigrp_log,
                '#show ip eigrp neighbor' : '\n' + eigrp_neighbor,
                '#show interface' : '\n' + interface_detail 
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
             singularString = singularString + (key + " : " + str(result)) + "\n\n"
        print('Updating SNOW ticket')
        self.networkDevice.put_incident(singularString)
        return result