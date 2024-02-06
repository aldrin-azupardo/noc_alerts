from networkdevice import Network_device
from networkdevice import JUNOS_device
from networkdevice import IOS_device


class Device_Factory(object):

    @classmethod
    def get_device(cls, vendor, repository, credential_params) -> Network_device:
        if vendor == "Juniper":
            return JUNOS_device(repository, credential_params=credential_params)
        else:
            return IOS_device(repository, credential_params=credential_params)
       