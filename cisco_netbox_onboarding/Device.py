from .Netbox_Connector import netbox_api
from .VirtualChassis import VirtualChassis
from .CustomExceptions import InvalidInputError

class Device:
    def __init__(self, role, device, site, device_type) -> None:
        self.role = role
        self.device = device
        self.site = netbox_api.dcim.sites.get(name__ie=site)
        self.device_type = netbox_api.dcim.device_types.get(part_number__ie=device_type)
        self.serial = None
        self.mac_address = None
        self.software = None
        self.vc_name = None
        self.vc_master = False
        self.stack_swi_num = None
        self.uuid_device = None
        self.flag_device_present = False

        if not self.site:
            raise ValueError(f"Site: {site}, is not present")
        
        if not self.device_type:
            raise ValueError(f"Device type: {device_type}, is not present")
    
    def update_db(self) -> dict:
        if self.role in ["Router", "Access Switch", "Access Point", "Wireless Controller", "Firewall", "Meraki MX", "Meraki MS", "Meraki MR"]:
            obj_device = netbox_api.dcim.devices.get(name__ie=self.device)
            if not obj_device:
                obj_device = netbox_api.dcim.devices.create(
                    name = self.device.upper(),
                    device_type = self.device_type.id,
                    role = netbox_api.dcim.device_roles.get(name__ie=self.role).id,
                    site = self.site.id,
                    status = "active"
                )
            if obj_device:
                if self.serial:
                    obj_device.serial = self.serial
                if self.software:
                    obj_device.custom_fields = {'software': self.software}
                    obj_device.save()
                if self.mac_address:
                    obj_device.custom_fields = {'mac': self.mac_address}
                obj_device.save()

                device_record = {obj_device.name: obj_device.id}
                if len(device_record) > 0:
                    self.uuid_device = device_record
                    return self.uuid_device

        if self.role in ["Multi Switch"]:
            if self.stack_swi_num and self.vc_name:
                #Check virtual chassis
                obj_vc = VirtualChassis(self.vc_name)
                obj_vc.update_db()
                obj_device = netbox_api.dcim.devices.get(name__ie=self.device)
                if not obj_device:
                    obj_device = netbox_api.dcim.devices.create(
                        name = self.device,
                        device_type = self.device_type.id,
                        role = netbox_api.dcim.device_roles.get(name__ie=self.role).id,
                        site = self.site.id,
                        status = "active",
                        virtual_chassis = obj_vc.id,
                        vc_position = self.stack_swi_num,
                        vc_priority = 16 - int(self.stack_swi_num)
                    )

                if obj_device:
                    if self.serial:
                        obj_device.serial = self.serial
                    if self.software:
                        obj_device.custom_fields = {'software': self.software}
                        obj_device.save()
                    if self.mac_address:
                        obj_device.custom_fields = {'mac': self.mac_address}
                        
                    obj_device.save()

                    # set vc master
                    if self.vc_master:
                        obj_vc.master = self.device
                        obj_vc.update_db()


                    device_record = {obj_device.name: obj_device.id}
                    if len(device_record) > 0:
                        self.uuid_device = device_record
                        return self.uuid_device
        raise ValueError(f"{self.device}, can't be created")
    
class Router(Device):
    def __init__(self, device, site, device_type) -> None:
        super().__init__("Router" , device, site, device_type)

class SwitchNonStack(Device):
    def __init__(self, device, site, device_type) -> None:
        super().__init__("Access Switch" , device, site, device_type)

class SwitchStack(Device):
    def __init__(self, device, site, device_type) -> None:
        super().__init__("Multi Switch" , device, site, device_type)

class AccessPoint(Device):
    def __init__(self, device, site, device_type) -> None:
        super().__init__("Access Point" , device, site, device_type)

class WirelessController(Device):
    def __init__(self, device, site, device_type) -> None:
        super().__init__("Wireless Controller" , device, site, device_type)

class Firewall(Device):
    def __init__(self, device, site, device_type) -> None:
        super().__init__("Firewall" , device, site, device_type)

class MerakiMX(Device):
    def __init__(self, device, site, device_type) -> None:
        super().__init__("Meraki MX" , device, site, device_type)

class MerakiMS(Device):
    def __init__(self, device, site, device_type) -> None:
        super().__init__("Meraki MS" , device, site, device_type)

class MerakiMR(Device):
    def __init__(self, device, site, device_type) -> None:
        super().__init__("Meraki MR" , device, site, device_type)


class DeviceDetect:
    def __init__(self, hostname, site, version) -> None:
        self.hostname = hostname.replace('>', '').replace('#', '').replace('(', '').replace(')', '').upper()
        self.site = site.upper()
        self.version = dict(version)
        self.role = None
        self.os = None
        self.devices = None

        if not isinstance(self.version, dict):
            raise InvalidInputError("version is invalid")
        
        if not isinstance(self.hostname, str):
            raise InvalidInputError("hostname is invalid")
        
        if not isinstance(self.site, str) or len(self.site) != 3:
            raise InvalidInputError("hostname is invalid")
        
        self.detect()

    def detect(self):
        if self.version and self.hostname:
            # Cisco IOS and IOS-XE
            if self.version.get('version', None):
                # router
                if not self.version['version'].get('switch_num', None):
                    self.role = "Router"
                    self.os = self.version['version'].get('os', None)
                    device_detail = {}
                    device_detail[1] = {
                        "device": self.hostname,
                        "site": self.site,
                        "device_type": self.version['version'].get('chassis', self.version['version'].get('rtr_type', 'invalid')),
                        "serial": self.version['version'].get('chassis_sn', None),
                        "software": self.version['version'].get('version', None)
                    }

                    if len(device_detail) > 0:
                        self.devices = device_detail
                
                # Switch 
                if self.version['version'].get('switch_num', None):
                    switches = self.version['version']['switch_num']
                    # Single
                    if len(switches) == 1:
                        self.role = "Access Switch"
                        self.os = self.version['version'].get('os', None)
                        device_detail = {}
                        for switch in switches:
                            loop_data = {
                                "device": self.hostname,
                                "site": self.site,
                                "device_type": switches[switch].get('model_num', switches[switch].get('model', 'invalid')),
                                "mac_address": switches[switch].get('mac_address', None),
                                "serial": switches[switch].get('system_sn', None),
                                "software": self.version['version'].get('version', None),
                                "swi_num": int(switch)
                            }
                            device_detail[1] = loop_data

                        if len(device_detail) > 0:
                            self.devices = device_detail
                    # Stacked Switch
                    if len(switches) >= 2:
                        self.role = "Multi Switch"
                        self.os = self.version['version'].get('os', None)
                        switch_num = list(switches)
                        switch_num = [int(i) for i in switch_num]
                        switch_num.sort()
                        master_swi = switch_num[0]

                        device_detail = {}
                        for switch in switches:
                            # for switches without any model information
                            if not switches[switch].get('model_num', None) and not switches[switch].get('model', None):
                                loop_data = {
                                    "device": f"{self.hostname}_{switch}",
                                    "site": self.site,
                                    "device_type": self.version['version'].get('chassis', self.version['version'].get('rtr_type', 'Invalid')),
                                    "mac_address": None,
                                    "serial": None,
                                    "software": self.version['version'].get('version', None),
                                    "swi_num": int(switch),
                                    "vc_master": True if master_swi == int(switch) else False,
                                    "vc_name": self.hostname
                                }
                            if switches[switch].get('model_num', None) or switches[switch].get('model', None):
                                loop_data = {
                                    "device": f"{self.hostname}_{switch}",
                                    "site": self.site,
                                    "device_type": switches[switch].get('model_num', switches[switch].get('model', 'invalid')),
                                    "mac_address": switches[switch].get('mac_address', None),
                                    "serial": switches[switch].get('system_sn', None),
                                    "software": self.version['version'].get('version', None),
                                    "swi_num": int(switch),
                                    "vc_master": True if master_swi == int(switch) else False,
                                    "vc_name": self.hostname
                                }
                            device_detail[int(switch)] = loop_data
                        
                        if len(device_detail) > 0:
                            self.devices = device_detail
            
            # Cisco Nexus
            if self.version.get('platform', None):
                pass
        

if __name__=='__main__':
    devices = [{'hostname': 'AAI-MFG-MDF-EDG-SWI-01_1', 'site':'AAI', 'device_type': 'C9300-48UXM', 'serial': 'ABCD-EFGH-IJKL-GHJK', 'software': '17.6.5', 'vc_master': True, 'swi_num': 1, 'vc_name': 'AAI-MFG-MDF-EDG-SWI-01'},
               ]
    
    for device in devices:
        obj = SwitchStack(device['hostname'], device['site'], device['device_type'])
        obj.serial = device.get('serial', None)
        obj.software = device.get('software', None)
        obj.vc_master = device.get('vc_master', None)
        obj.stack_swi_num = device.get('swi_num', None)
        obj.vc_name = device.get('vc_name', None)

        obj.update_db()
        print(obj.uuid_device)
