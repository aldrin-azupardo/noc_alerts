import commandparser
from triage import NetworkTriage
from incidentrepo import IncidentRepository

class PowerSupplyTriage(NetworkTriage):
    def __init__(self, connection_params, repository: IncidentRepository):
        super().__init__(connection_params, repository)

    def operate(self) -> dict:
        if self.networkDevice.good_ssh_connection:
            output = self.networkDevice.get_env_details()
            parsed_results = commandparser.CommandParser('./parser/show_env_all.textfsm', output).parse_text()
        
            for items in parsed_results:
                if any([('Bad' in items and items[2] is None), ('Not Present' in items and items[2] is None) , ('No Input Power' in items and items[2] is None)]):
                    output = self.networkDevice.get_inventory()
                    serial_nums = commandparser.CommandParser('./parser/show_inventory.textfsm', output).parse_text()
                    result = {
                        'IP address' : self.networkDevice.ip,
                        'Is Alive' : self.networkDevice.is_alive,
                        'Good SSH Connection' : self.networkDevice.good_ssh_connection,
                        'Environment_details' : parsed_results,
                        'Serial_nums' : self.find_bad_serial(serial_nums)
                    }
                    return result
            result = {
                'IP address' : self.networkDevice.ip,
                'Is Alive' : self.networkDevice.is_alive,
                'Good SSH Connection' : self.networkDevice.good_ssh_connection,
                'Environment_details' : parsed_results,
                'Serial_nums': None
            }
        else:
            result = {
                'IP address' : self.networkDevice.ip_address,
                'Is Alive' : False,
                'Good SSH Connection' : False,
                'Environment_details' : [],
                'Serial_nums': None
            }
        return result