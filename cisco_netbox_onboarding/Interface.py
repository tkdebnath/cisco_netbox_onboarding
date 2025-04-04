import re
from .Netbox_Connector import netbox_api
from .CustomExceptions import InvalidInputError

class FixInterfacesName:
    def __init__(self, device, position) -> None:
        self.device_id = netbox_api.dcim.devices.get(name__ie=device).id
        self.position = int(position)
        self.name_fixed = False

        obj_interfaces = netbox_api.dcim.interfaces.filter(device_id=self.device_id)
        if not obj_interfaces:
            raise ValueError(f"device: {device} has no interfaces")
        
        if not self.position:
            raise ValueError(f"Switch position value empty")
        
        for interface in obj_interfaces:
            new_name = name_fix(text=interface.name, position=self.position)
            if new_name:
                interface.name = new_name
                interface.save()
                self.name_fixed = True

class MissingInterfaces:
    def __init__(self, all_interfaces: dict) -> None:
        """
        all_interfaces structure: {'device': [interface]}
        """
        self.all_interfaces = all_interfaces
        self.interface_created = None

        if not isinstance(self.all_interfaces, dict):
            raise InvalidInputError("all_interfaces is invalid")
        
        self.fix_missing_interface()
    
    def fix_missing_interface(self) -> None:
        result_dict = {}
        for device in self.all_interfaces:
            loop_list = []
            # Fetch all interfaces of current device
            current_device_interfaces = {}
            device_id = netbox_api.dcim.devices.get(name__ie=device).id
            obj_interfaces = netbox_api.dcim.interfaces.filter(device_id=device_id)
            if obj_interfaces:
                for i in obj_interfaces:
                    current_device_interfaces[i.name] = i.id
            
            # Checking interfaces of input data
            interfaces = self.all_interfaces[device]
            if isinstance(interfaces, list) and len(interfaces) > 0:
                #Checking for missing interface
                for interface in interfaces:
                    if not current_device_interfaces.get(interface, None):
                        obj_interface = netbox_api.dcim.interfaces.create(
                            device = device_id,
                            name = interface,
                            type = "virtual" if interface.lower().startswith("loopback") or interface.lower().startswith("vlan") or "." in interface else "10gbase-x-x2",
                            enabled = True
                        )
                        if obj_interface:
                            loop_list.append({interface: obj_interface.id})
            if len(loop_list) > 0:
                result_dict[device] = loop_list
        if len(result_dict) > 0:
            self.interface_created = result_dict
                    

def name_fix(text, position):
    if position > 1:
        regex = r"(\D*)(\d+)/(\d+)/(\d+)"
        match = re.match(pattern=regex, string=text)
        if match:
            if int(position) != int(match.group(2)):
                return f"{match.group(1)}{position}/{match.group(3)}/{match.group(4)}"
    return None

def switch_number_interface(interface):
    regex = r"(\D*)(\d+)/(\d+)/(\d+)"
    match = re.match(pattern=regex, string=interface)
    if match:
        return int(match.group(2))
    
    if not match:
        regex = r"(\D*)(\d+)/(\d+)"
        match = re.match(pattern=regex, string=interface)
        if match:
            return int(match.group(2))
    
    return None
        
            

if __name__=='__main__':
    # obj_interface = Interfaces(device="SSK-7-SWI-01_1", position=1)
    # print(obj_interface.name_fixed)
    # obj_interfaces = MissingInterfaces(device="SSK-7-SWI-01_1", interfaces=["Vlan202", "Vlan102", "Loopback10"])
    # print(obj_interfaces.interface_created)
    all_interfaces = {'AAI-MFG-MDF-EDG-SWI-01_1': ['Vlan1',
                              'Vlan201',
                              'GigabitEthernet0/0',
                              'TwoGigabitEthernet1/0/1',
                              'TwoGigabitEthernet1/0/2',
                              'TwoGigabitEthernet1/0/3',
                              'TwoGigabitEthernet1/0/4',
                              'TwoGigabitEthernet1/0/5',
                              'TwoGigabitEthernet1/0/6',
                              'TwoGigabitEthernet1/0/7',
                              'TwoGigabitEthernet1/0/8',
                              'TwoGigabitEthernet1/0/9',
                              'TwoGigabitEthernet1/0/10',
                              'TwoGigabitEthernet1/0/11',
                              'TwoGigabitEthernet1/0/12',
                              'TwoGigabitEthernet1/0/13',
                              'TwoGigabitEthernet1/0/14',
                              'TwoGigabitEthernet1/0/15',
                              'TwoGigabitEthernet1/0/16',
                              'TwoGigabitEthernet1/0/17',
                              'TwoGigabitEthernet1/0/18',
                              'TwoGigabitEthernet1/0/19',
                              'TwoGigabitEthernet1/0/20',
                              'TwoGigabitEthernet1/0/21',
                              'TwoGigabitEthernet1/0/22',
                              'TwoGigabitEthernet1/0/23',
                              'TwoGigabitEthernet1/0/24',
                              'TwoGigabitEthernet1/0/25',
                              'TwoGigabitEthernet1/0/26',
                              'TwoGigabitEthernet1/0/27',
                              'TwoGigabitEthernet1/0/28',
                              'TwoGigabitEthernet1/0/29',
                              'TwoGigabitEthernet1/0/30',
                              'TwoGigabitEthernet1/0/31',
                              'TwoGigabitEthernet1/0/32',
                              'TwoGigabitEthernet1/0/33',
                              'TwoGigabitEthernet1/0/34',
                              'TwoGigabitEthernet1/0/35',
                              'TwoGigabitEthernet1/0/36',
                              'TenGigabitEthernet1/0/37',
                              'TenGigabitEthernet1/0/38',
                              'TenGigabitEthernet1/0/39',
                              'TenGigabitEthernet1/0/40',
                              'TenGigabitEthernet1/0/41',
                              'TenGigabitEthernet1/0/42',
                              'TenGigabitEthernet1/0/43',
                              'TenGigabitEthernet1/0/44',
                              'TenGigabitEthernet1/0/45',
                              'TenGigabitEthernet1/0/46',
                              'TenGigabitEthernet1/0/47',
                              'TenGigabitEthernet1/0/48',
                              'GigabitEthernet1/1/1',
                              'GigabitEthernet1/1/2',
                              'GigabitEthernet1/1/3',
                              'GigabitEthernet1/1/4',
                              'TenGigabitEthernet1/1/1',
                              'TenGigabitEthernet1/1/2',
                              'TenGigabitEthernet1/1/3',
                              'TenGigabitEthernet1/1/4',
                              'TenGigabitEthernet1/1/5',
                              'TenGigabitEthernet1/1/6',
                              'TenGigabitEthernet1/1/7',
                              'TenGigabitEthernet1/1/8',
                              'TwentyFiveGigE1/1/1',
                              'TwentyFiveGigE1/1/2'],
 'AAI-MFG-MDF-EDG-SWI-01_2': ['TwoGigabitEthernet2/0/1',
                              'TwoGigabitEthernet2/0/2',
                              'TwoGigabitEthernet2/0/3',
                              'TwoGigabitEthernet2/0/4',
                              'TwoGigabitEthernet2/0/5',
                              'TwoGigabitEthernet2/0/6',
                              'TwoGigabitEthernet2/0/7',
                              'TwoGigabitEthernet2/0/8',
                              'TwoGigabitEthernet2/0/9',
                              'TwoGigabitEthernet2/0/10',
                              'TwoGigabitEthernet2/0/11',
                              'TwoGigabitEthernet2/0/12',
                              'TwoGigabitEthernet2/0/13',
                              'TwoGigabitEthernet2/0/14',
                              'TwoGigabitEthernet2/0/15',
                              'TwoGigabitEthernet2/0/16',
                              'TwoGigabitEthernet2/0/17',
                              'TwoGigabitEthernet2/0/18',
                              'TwoGigabitEthernet2/0/19',
                              'TwoGigabitEthernet2/0/20',
                              'TwoGigabitEthernet2/0/21',
                              'TwoGigabitEthernet2/0/22',
                              'TwoGigabitEthernet2/0/23',
                              'TwoGigabitEthernet2/0/24',
                              'TwoGigabitEthernet2/0/25',
                              'TwoGigabitEthernet2/0/26',
                              'TwoGigabitEthernet2/0/27',
                              'TwoGigabitEthernet2/0/28',
                              'TwoGigabitEthernet2/0/29',
                              'TwoGigabitEthernet2/0/30',
                              'TwoGigabitEthernet2/0/31',
                              'TwoGigabitEthernet2/0/32',
                              'TwoGigabitEthernet2/0/33',
                              'TwoGigabitEthernet2/0/34',
                              'TwoGigabitEthernet2/0/35',
                              'TwoGigabitEthernet2/0/36',
                              'TenGigabitEthernet2/0/37',
                              'TenGigabitEthernet2/0/38',
                              'TenGigabitEthernet2/0/39',
                              'TenGigabitEthernet2/0/40',
                              'TenGigabitEthernet2/0/41',
                              'TenGigabitEthernet2/0/42',
                              'TenGigabitEthernet2/0/43',
                              'TenGigabitEthernet2/0/44',
                              'TenGigabitEthernet2/0/45',
                              'TenGigabitEthernet2/0/46',
                              'TenGigabitEthernet2/0/47',
                              'TenGigabitEthernet2/0/48',
                              'GigabitEthernet2/1/1',
                              'GigabitEthernet2/1/2',
                              'GigabitEthernet2/1/3',
                              'GigabitEthernet2/1/4',
                              'TenGigabitEthernet2/1/1',
                              'TenGigabitEthernet2/1/2',
                              'TenGigabitEthernet2/1/3',
                              'TenGigabitEthernet2/1/4',
                              'TenGigabitEthernet2/1/5',
                              'TenGigabitEthernet2/1/6',
                              'TenGigabitEthernet2/1/7',
                              'TenGigabitEthernet2/1/8',
                              'TwentyFiveGigE2/1/1',
                              'TwentyFiveGigE2/1/2']}
    
    obj_missing_intf = MissingInterfaces(all_interfaces=all_interfaces)