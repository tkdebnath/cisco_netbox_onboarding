from traitlets import Bool
from .Netbox_Connector import netbox_api
from .CustomExceptions import InvalidInputError


class IPAM:
    def __init__(self, ip_addr_interface) -> None:
        self.ip_addr_interface = ip_addr_interface
        self.uuid_ip_address = None
        self.uuid_interfaces = None
        self.stop_process = False
    
    def create_ip_address(self) -> None:
        if not isinstance(self.ip_addr_interface, list) or len(self.ip_addr_interface) < 0:
            raise InvalidInputError("ip_address list value not provided")

        loop_ip = {}
        for ip in self.ip_addr_interface:
            if ip.get('oper_status', 'down') == 'up' and ip.get('ip_addr', None):
                obj_ip_addr = netbox_api.ipam.ip_addresses.get(address=ip['ip_addr'])
                if obj_ip_addr:
                    loop_ip[ip['ip_addr']] = obj_ip_addr.id
                
                if not obj_ip_addr:
                    try:
                        netbox_ip = netbox_api.ipam.ip_addresses.create(
                            address = ip['ip_addr'],
                            status = "active"
                        )
                        if netbox_ip:
                            loop_ip[ip['ip_addr']] = netbox_ip.id
                    except:
                        print(f"{ip['ip_addr']} - Duplicate IP address found in global table")
            
        # assign loop_ip to uuid_ip_address if there is some data in it
        if len(loop_ip) > 0:
            self.uuid_ip_address = loop_ip
    
    def map_ip_interface(self) -> None:
        """
        input [{'device': 'device_name', 'interface': 'interface_name', 'ip_addr': 'x.x.x.x/xx'}]
        """
        if not isinstance(self.ip_addr_interface, list) or not len(self.ip_addr_interface) > 0:
            raise InvalidInputError("ip_address list value not provided")
        
        loop_interfaces = {}
        for item in self.ip_addr_interface:
            if item.get('oper_status', 'down') == 'up' and item.get('ip_addr', None):
                obj_port = netbox_api.dcim.interfaces.get(device=item['device'], name__ie=item['interface'])
                obj_ip_addr = netbox_api.ipam.ip_addresses.get(address=item['ip_addr'])
                if not obj_port:
                    obj_device = netbox_api.dcim.devices.get(name__ie=item['device'])
                    if obj_device:
                        obj_port = netbox_api.dcim.interfaces.create(
                            device = obj_device.id,
                            name = item['interface'],
                            type = "virtual",
                            enabled = True
                        )
                if not obj_ip_addr:
                    try:
                        obj_ip_addr = netbox_api.ipam.ip_addresses.create(
                            address = item['ip_addr'],
                            status = "active"
                            )
                    except:
                        print(f"{item['ip_addr']} - Duplicate IP address, assign to port failed")
                if obj_port and obj_ip_addr:
                # mapping interface to ip address
                    obj_ip_addr.assigned_object = obj_port
                    obj_ip_addr.assigned_object_id = obj_port.id
                    obj_ip_addr.assigned_object_type = 'dcim.interface'
                    obj_ip_addr.save()
                            
                    loop_interfaces[item['ip_addr']] = obj_port.id
        
        # assign loop_interface to uuid_interfaces if there is some data in it
        if len(loop_interfaces) > 0:
            self.uuid_interfaces = loop_interfaces
    
    def update_primary_ip(self, device, primary_ip) -> Bool:
        obj_ip_addr = netbox_api.ipam.ip_addresses.get(address=primary_ip, assigned=True, device=device)
        obj_device = netbox_api.dcim.devices.get(name__ie=device)
        if obj_ip_addr and obj_device:
            obj_device.primary_ip4 = obj_ip_addr.id
            obj_device.save()
            return True
        return False
