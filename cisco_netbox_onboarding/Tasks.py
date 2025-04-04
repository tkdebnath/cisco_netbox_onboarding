"""
Tasks:
- Create IP Prefixes
- Create Virtual Chassis (if stack switch)
- Create Devices
- Attach Network Module and FAN
- Create Logical interfaces
- Fix interface names (if stack switch or single switch with non 1 switch num)
- Map interface with IP address
- Update Primary IP
- Connect Stack Cables
- Connect cables for neighbors

"""

from .CustomExceptions import DeviceCreateError, InvalidInputError
from .Device import DeviceDetect, Router, SwitchNonStack, SwitchStack
from .Interface import FixInterfacesName, MissingInterfaces, switch_number_interface
from .inventory_helper import find_network_module
from .IPAM import IPAM
from .Inventory import NetworkModule
from .Adjacency import AdjacencyNormal
from .Connections import Connection
from .VirtualChassis import VirtualChassis


class Onboarding:
    def __init__(self, hostname, site, version, interfaces, inventory) -> None:
        self.hostname = hostname
        self.site = site
        self.version = version
        self.interfaces = interfaces
        self.inventory = inventory
        self.stack_ports_summary = None
        self.stack_ports_connection = None
        self.cdp_neighbors_detail = None
        self.cdp_neighbors_connection = None
        self.tacacs_ip = None
        self.tacacs_device = None
        self.flag_primary_ip = False
        self.os = None
        self.role = None
        self.devices = None
        self.ip_addr_interface = None
        self.all_interfaces = None
        self.all_modules = None
        self.onboard_complete = None

        if not self.hostname:
            raise InvalidInputError("hostname value missing")
        if not self.site:
            raise InvalidInputError("site value missing")
        if not self.version:
            raise InvalidInputError("site value missing")
        if not self.interfaces:
            raise InvalidInputError("interfaces value missing")
        if not self.inventory:
            raise InvalidInputError("inventory value missing")

    def identify_device(self) -> None:    
        #Finding OS and device category
        obj_detect = DeviceDetect(hostname=self.hostname, site=self.site, version=self.version)
        if obj_detect:
            self.os = obj_detect.os
            self.role = obj_detect.role
            self.devices = obj_detect.devices
    
    def identify_ip_prefix(self) -> None:
        # build list of ip address and ip with interfaces
        """
        required format: [{'device': 'device_name', 'interface': 'interface_name', 'ip_addr': 'x.x.x.x/xx'}]
        """
        if self.role in ['Router', 'Access Switch']:
            loop_ip_intf = []
            for interface in self.interfaces:
                
                if interface.startswith("Mgm") or interface.startswith("mgm") or interface.startswith("Gig") or interface.startswith("Eth") or interface.startswith("Fa") or interface.startswith("Tw") or interface.startswith("Te") or interface.startswith("Serial") or interface.startswith("Hu") or interface.startswith("Loop") or interface.startswith("loop") or interface.startswith("Vlan") or interface.startswith("Fo"):

                    tmp_data = {
                                'device': self.devices[1]['device'],
                                'interface': interface,
                                'oper_status': self.interfaces[interface].get('oper_status', 'down'),
                                }
                    
                    ipv4 = self.interfaces[interface].get('ipv4', None)
                    if ipv4:
                        for ip in ipv4:
                            if not ip.startswith("192.168.") and not ip.startswith("169."):
                                tmp_data['ip_addr'] = ip

                    loop_ip_intf.append(tmp_data)

                    # set tacacs device
                    self.tacacs_device = self.devices[1]['device']

            # assign loop_ip_intf to ip_addr_interface if list is not blank
            if len(loop_ip_intf) > 0:
                self.ip_addr_interface = loop_ip_intf

        if self.role in ['Multi Switch']:
            # set master switch for all logical ports
            stack_master = None
            for switch in self.devices:
                if self.devices[switch].get('vc_master'):
                    stack_master = f"{self.devices[switch]['device']}"
                    # set tacacs device
                    self.tacacs_device = stack_master
            
            #raise error if stack master is None
            if not stack_master:
                raise ValueError(f"{self.hostname}: don't have any stack master")

            loop_ip_intf = []
            for interface in self.interfaces:
                
                # Physical interfaces
                if interface.startswith("Mgm") or interface.startswith("mgm") or interface.startswith("Gig") or interface.startswith("Eth") or interface.startswith("Fa") or interface.startswith("Tw") or interface.startswith("Te") or interface.startswith("Serial") or interface.startswith("Hu") or interface.startswith("Fo"):

                    swi_num = switch_number_interface(interface)
                    ipv4 = self.interfaces[interface].get('ipv4', None)

                    tmp_data = {
                            'interface': interface,
                            'oper_status': self.interfaces[interface].get('oper_status', 'down'),
                            }
                    
                    if ipv4:
                        for ip in ipv4:
                            if not ip.startswith("192.168.") and not ip.startswith("169."):
                                tmp_data['ip_addr'] = ip

                    if swi_num and self.devices.get(swi_num, None) and self.devices[swi_num]['device']:
                        tmp_data['device'] = self.devices[swi_num]['device']
                        loop_ip_intf.append(tmp_data)
                    
                    if not swi_num:
                        tmp_data['device'] = stack_master
                
                # Logical interfaces
                if interface.startswith("Vlan") or interface.startswith("Loop") or interface.startswith("loop"):
                    ipv4 = self.interfaces[interface].get('ipv4', None)

                    tmp_data = {
                            'device': stack_master,
                            'interface': interface,
                            'oper_status': self.interfaces[interface].get('oper_status', 'down'),
                            }
                    
                    if ipv4:
                        for ip in ipv4:
                            for ip in ipv4:
                                if not ip.startswith("192.168.") and not ip.startswith("169."):
                                    tmp_data['ip_addr'] = ip
                        
                    loop_ip_intf.append(tmp_data)

            # assign loop_ip_intf to ip_addr_interface if list is not blank
            if len(loop_ip_intf) > 0:
                self.ip_addr_interface = loop_ip_intf
    
    def identify_interfaces(self) -> None:
        if not self.ip_addr_interface:
            raise ValueError("ip_addr_interface is missing")
        
        all_interfaces = {}
        for device in self.devices:
            current_intf = []
            current_device = self.devices[device]['device']

            for interface in self.ip_addr_interface:
                if interface['device'] == current_device:
                    current_intf.append(interface['interface'])
            
            if len(current_intf) > 0:
                all_interfaces[current_device] = current_intf
        
        if len(all_interfaces) > 0:
            self.all_interfaces = all_interfaces

    def identify_inventory(self) -> None:
        """
        output format: {'device': 'SSK-7-SWI-01_1','module_type': 'C9300-NM-2Y', 'serial': 'ABCD-EFGH-IJKL-GHJK', 'description': '2x25G Uplink Module'}
        """
        uplink_module = find_network_module(data=self.inventory, keyword="Uplink Module")
        if isinstance(uplink_module, dict):
            if self.role in ['Router', 'Access Switch']:
                all_modules = []
                slots = uplink_module.get('slot', None)
                if slots:
                    for slot in slots:
                        modules = slots[slot].get('rp', None)
                        if modules:
                            for module in modules:
                                dict_loop = {
                                    'device': self.devices[1]['device'],
                                    'module_type': module,
                                    'serial': modules[module].get('sn', None),
                                    'description': modules[module].get('descr', None)
                                }
                                all_modules.append(dict_loop)
                    if len(all_modules) > 0:
                        self.all_modules = all_modules
            
            if self.role in ['Multi Switch']:
                all_modules = []
                slots = uplink_module.get('slot', None)
                if slots:
                    for slot in slots:
                        modules = slots[slot].get('rp', None)
                        if modules:
                            for module in modules:
                                dict_loop = {
                                    'device': self.devices[int(slot)]['device'],
                                    'module_type': module,
                                    'serial': modules[module].get('sn', None),
                                    'description': modules[module].get('descr', None)
                                }
                                all_modules.append(dict_loop)
                    if len(all_modules) > 0:
                        self.all_modules = all_modules

    def identify_tacacs_ip(self):
        if self.tacacs_device:
            if self.tacacs_ip:
                #check for device in self.ip_addr_interface
                for interface in self.ip_addr_interface:
                    if interface.get('ip_addr', None) and interface.get('oper_status', 'down') == 'up':
                        ip = interface['ip_addr'].split('/')[0]
                        if ip == self.tacacs:
                            #call funct update_primary_ip
                            print(f'{self.tacacs_ip}: tacacs ip matched, device: {self.tacacs_device}')
                            self.flag_primary_ip = True
                            return

            if not self.tacacs_ip:
                #priority: loopback interface
                for interface in self.ip_addr_interface:
                    if interface['interface'].startswith('Loopback') or interface['interface'].startswith('loopback'):
                        if interface.get('ip_addr', None) and interface.get('oper_status', 'down') == 'up':
                            #call funct update_primary_ip
                            self.tacacs_ip = interface['ip_addr']
                            print(f'{self.tacacs_ip}: tacacs ip matched, device: {self.tacacs_device}')
                            self.flag_primary_ip = True
                            return
                
                #priority: Mgmt interface
                for interface in self.ip_addr_interface:
                    if interface['interface'].startswith('Mgmt') or interface['interface'].startswith('mgmt'):
                        if interface.get('ip_addr', None) and interface.get('oper_status', 'down') == 'up':
                            #call funct update_primary_ip
                            self.tacacs_ip = interface['ip_addr']
                            print(f'{self.tacacs_ip}: tacacs ip matched, device: {self.tacacs_device}')
                            self.flag_primary_ip = True
                            return
                
                #priority: Vlan interface
                for interface in self.ip_addr_interface:
                    if interface['interface'].startswith('Vlan') or interface['interface'].startswith('vlan'):
                        if interface.get('ip_addr', None) and interface.get('oper_status', 'down') == 'up':
                            #call funct update_primary_ip
                            self.tacacs_ip = interface['ip_addr']
                            print(f'{self.tacacs_ip}: tacacs ip matched, device: {self.tacacs_device}')
                            self.flag_primary_ip = True
                            return
                
                #priority: Physical interface
                for interface in self.ip_addr_interface:
                    if (interface['interface'].startswith('Eth') or interface['interface'].startswith('Fa') or interface['interface'].startswith('Gi')
                        or interface['interface'].startswith('Tw') or interface['interface'].startswith('Te') or interface['interface'].startswith('Hu')):

                        if interface.get('ip_addr', None) and interface.get('oper_status', 'down') == 'up':
                            #call funct update_primary_ip
                            self.tacacs_ip = interface['ip_addr']
                            print(f'{self.tacacs_ip}: tacacs ip matched, device: {self.tacacs_device}')
                            self.flag_primary_ip = True
                            return

    def identify_adjacency(self) -> None:
        if self.stack_ports_summary:
            """
            furure implementation
            """
            pass

        if self.cdp_neighbors_detail:
            obj_adjacency = AdjacencyNormal(hostname=self.hostname, adjacency_table=self.cdp_neighbors_detail)
            if obj_adjacency.connection_records:
                self.cdp_neighbors_connection = obj_adjacency.connection_records


    def execute_task1(self):
        """
        Add/Update Device
        """
        if not self.devices:
            raise ValueError(f"{self.hostname}: failed to gather basic details")
        
        # Task 1 : add or update device
        if self.role == "Router":
            obj_router = Router(device=self.devices[1]['device'], site=self.devices[1]['site'], device_type=self.devices[1]['device_type'])
            obj_router.serial = self.devices[1].get('serial', None)
            obj_router.software = self.devices[1].get('software', None)
            result = obj_router.update_db()
            if result:
                print(f"{self.devices[1]['device']}, created")
            if not result:
                raise DeviceCreateError(f"{self.devices[1]['device']}, creation failed")
        
        if self.role == "Access Switch":
            obj_switch = SwitchNonStack(device=self.devices[1]['device'], site=self.devices[1]['site'], device_type=self.devices[1]['device_type'])
            obj_switch.serial = self.devices[1].get('serial', None)
            obj_switch.mac_address = self.devices[1].get('mac_address', None)
            obj_switch.software = self.devices[1].get('software', None)
            result = obj_switch.update_db()
            if result:
                print(f"{self.devices[1]['device']}, created")
            if not result:
                raise DeviceCreateError(f"{self.devices[1]['device']}, creation failed")
        
        if self.role == "Multi Switch":

            for item in self.devices:
                obj_switch = SwitchStack(device=self.devices[item]['device'], site=self.devices[item]['site'], device_type=self.devices[item]['device_type'])
                obj_switch.serial = self.devices[item].get('serial', None)
                obj_switch.mac_address = self.devices[item].get('mac_address', None)
                obj_switch.software = self.devices[item].get('software', None)
                obj_switch.vc_master = self.devices[item].get('vc_master', None)
                obj_switch.vc_name = self.devices[item].get('vc_name', None)
                obj_switch.stack_swi_num = self.devices[item].get('swi_num', None)
                
                if not obj_switch.vc_name or not obj_switch.stack_swi_num:
                    raise DeviceCreateError(f"{self.devices[1]['device']}, creation failed, reason: vc_name or swi_num missing")
                result = obj_switch.update_db()
                if result:
                    print(f"{self.devices[item]['device']}: record updated")
                if not result:
                    raise DeviceCreateError(f"{self.devices[item]['device']}: record failed")
    
    def execute_task1_1(self):
        """
        Enable master switch in stack
        """
        if self.role == "Multi Switch":
           for switch in self.devices:
               if self.devices[switch].get('vc_master', False) and self.devices[switch].get('vc_name', None):
                   obj_vc = VirtualChassis(hostname=self.hostname)
                   obj_vc.master = self.devices[switch]['device']
                   obj_vc.update_db()
                   if obj_vc.id:
                       print(f"{self.devices[switch]['device']} is now master in stack")
                

    def execute_task2(self):
        """
        Uplink module
        """
        if not self.all_modules:
            print(f"{self.hostname}: no uplink module found")
        
        if self.all_modules:
            for module in self.all_modules:
                obj_nm_module = NetworkModule(device=module['device'], module_type=module['module_type'])
                obj_nm_module.serial = module['serial']
                obj_nm_module.description = module['description']
                obj_nm_module.attach_module()
                if obj_nm_module.uuid_module:
                    print(f"{module['device']}: uplink module:{module['module_type']} attached")
                
                if not obj_nm_module.uuid_module:
                    print(f"{module['device']}: uplink module:{module['module_type']} failed to attach")
    
    def execute_task3(self):
        """
        Interface name fix
        """
        if self.role in ["Access Switch", "Multi Switch"]:
            for item in self.devices:
                try:
                    obj_switch = FixInterfacesName(device=self.devices[item]['device'], position=self.devices[item]['swi_num'])
                    if obj_switch.name_fixed:
                        print(f"{self.devices[item]['device']}: interface name fixed")
                except ValueError:
                    print(f"{self.devices[item]['device']} has no interfaces")

    def execute_task4(self):
        """
        create all missing interfaces
        """
        if not self.all_interfaces:
            raise ValueError(f"{self.hostname}: all_interfaces is missing")
        
        obj_missing_intf = MissingInterfaces(all_interfaces=self.all_interfaces)
        if obj_missing_intf.interface_created:
            print(f"{self.hostname}: missing interface created")
        if not obj_missing_intf.interface_created:
            print(f"{self.hostname}: interface not created")
    
    def execute_task5(self):
        """
        IP address create and IP interface mapping, set primary ip
        """
        if not self.ip_addr_interface:
            raise ValueError(f"{self.hostname}: no ip addresses found")
        
        obj_ipam = IPAM(ip_addr_interface=self.ip_addr_interface)
        obj_ipam.create_ip_address()
        if obj_ipam.uuid_ip_address:
            print(f"{self.hostname}: ip addresses created")
            obj_ipam.map_ip_interface()
            if obj_ipam.uuid_interfaces:
                print(f"{self.hostname}: ip addresses mapped with interfaces")
        
        # set primary ip
        if self.flag_primary_ip and self.tacacs_device and self.tacacs_ip:
            obj_ipam.update_primary_ip(device=self.tacacs_device, primary_ip=self.tacacs_ip)
        if self.flag_primary_ip:
            print(f"{self.hostname}: primary ip enabled")
        if not self.flag_primary_ip:
            print(f"{self.hostname}: primary ip failed to enable")
    
    def execute_task6(self):
        """
        Cable connection
        """
        if self.stack_ports_connection:
            """
            Future feature
            """
            pass

        if self.cdp_neighbors_connection:
            for conn in self.cdp_neighbors_connection:
                try:
                    obj_connection = Connection(a_device=conn['a_device'], a_port=conn['a_port'],
                                            b_device=conn['b_device'], b_port=conn['b_port'])
                
                    conn_status = obj_connection.make_connection()
                    if conn_status:
                        print(f"{conn['a_device']}:{conn['a_port']} --> {conn['b_device']}:{conn['b_port']} cable connected ")
                except ValueError:
                    print(f"remote device: {conn['b_device']} has no port {conn['b_port']}")
                    
    
    def automatic(self):

        # Collecting data
        """ tacacs ip can be defined """
        self.identify_device()
        self.identify_ip_prefix()
        self.identify_interfaces()
        self.identify_inventory()
        self.identify_tacacs_ip()
        self.identify_adjacency()

        # execution
        self.execute_task1()
        self.execute_task1_1()
        self.execute_task2()
        self.execute_task3()
        self.execute_task4()
        self.execute_task5()
        self.execute_task6()

        print(f"{self.hostname}: onboard complete")
        
