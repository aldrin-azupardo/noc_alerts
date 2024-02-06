from triage import NetworkTriage

class PowerSupplyTriage(NetworkTriage):
    def __init__(self, networkDevice):
        super().__init__(networkDevice)

    def operate(self) -> dict:
        power_failure_details = self.networkDevice.power_failure_details()
        print(power_failure_details)
        if self.networkDevice.good_ssh_connection:
            try:
                result = {
                    'IP address' : self.networkDevice.ip,
                    'Is Alive' : self.networkDevice.is_alive,
                    'Good SSH Connection' : self.networkDevice.good_ssh_connection,
                    '#show environment' : '\n' + power_failure_details['environment_details'],
                    '#show inventory': '\n' + power_failure_details['inventory_details']
                } 
            except:
                result = {
                    'IP address' : self.networkDevice.ip,
                    'Is Alive' : self.networkDevice.is_alive,
                    'Good SSH Connection' : self.networkDevice.good_ssh_connection,
                    '#show environment' : '\n' + power_failure_details['environment_details']
                }
        else:
            result = {
                'IP address' : self.networkDevice.ip,
                'Is Alive' : False,
                'Good SSH Connection' : False,
                'Environment_details' : []
            }
        
        singularString = ""
        for key, result in result.items():
             singularString = singularString + (key + " : " + str(result)) + "\n\n"
        print('Updating SNOW ticket')
        self.networkDevice.put_incident(singularString)
        return result
