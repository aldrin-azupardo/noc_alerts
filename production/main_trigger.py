import incidentrepo
from powersupplyfailure import PowerSupplyTriage
from eigrpdown import EIGRPTriage
from interfaceoututilization import InterfaceUtilizationTriage
from bgpdown import BGPTriage
from device_factory import Device_Factory
import sys

ssh_username = str(sys.argv[1])
ssh_password = str(sys.argv[2])
snow_username = str(sys.argv[3])
snow_password = str(sys.argv[4])
number = str(sys.argv[5])
url = 'https://chevronbox.service-now.com'

def Main():
    credential_params = {
        'username': ssh_username,
        'password': ssh_password,
        'number' : number 
    }
    repository = incidentrepo.IncidentRepository(baseurl=url, user_name=snow_username, password=snow_password)
    vendor = repository.get_incident({'number': credential_params['number']}).device_vendor
    incident_description = repository.get_incident({'number': credential_params['number']}).incident_description
    networkDevice = Device_Factory.get_device(vendor, repository=repository, credential_params=credential_params)
    if "Power Supply Failure" in incident_description:
        powersupply = PowerSupplyTriage(networkDevice=networkDevice)
        result = powersupply.operate()
        print("PowerSupplyTriage Result ====>")
        print(result)
    elif "EIGRP Down" in incident_description:
        eigrp = EIGRPTriage(networkDevice=networkDevice)
        result = eigrp.operate()
        print("EIGRPTriage Result ====>")
        print(result)
    elif "Perf-Interface-In-Util" or "Perf-Campus" in  incident_description:
        interfaceutilization = InterfaceUtilizationTriage(networkDevice=networkDevice)
        result = interfaceutilization.operate()
        print("Interface Utilization Result ====>")
        print(result)
    elif "BGP Down" in incident_description:
        bgpdown = BGPTriage(networkDevice=networkDevice)
        result = bgpdown.operate()
        print("BGP Down Result ====>")
        print(result)

if __name__ == "__main__":
    Main()
