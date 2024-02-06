from incidentrepo import IncidentRepository

class NetworkTriage(object):
    """Class to represent network switches and routers"""
    
    def __init__(self, netWorkDevice):
        print("Init triage.py")
        self.networkDevice =  netWorkDevice

    def operate(self) -> dict:
        pass

    def put_incident(self, params):
        self.networkDevice.put_incident(params=params)

        