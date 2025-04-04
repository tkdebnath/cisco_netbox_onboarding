from .Netbox_Connector import netbox_api
from .VirtualChassis import VirtualChassis
from .Interface import switch_number_interface

class Adjacency:
    def __init__(self, connection_type, hostname, adjacency_table) -> None:
        self.connection_type = connection_type
        self.hostname = hostname
        self.adjacency_table = adjacency_table
        self.connection_records = None

        self.connection_table()

    def connection_table(self):
        if self.connection_type in ["Stack"]:
            pass

        if self.connection_type in ["Normal"]:
            """
            cdp neighbor table
            """
            if isinstance(self.adjacency_table, dict) and self.adjacency_table.get('index', None) and len(self.adjacency_table['index']) > 0:
                con_record = []
                neighbors = self.adjacency_table['index']
                for index in neighbors:
                    if neighbors[index].get('device_id', None) and neighbors[index].get('local_interface', None) and neighbors[index].get('port_id', None):
                        remote_device_name = neighbors[index]['device_id'].split('.')[0].split('(')[0].upper()
                        remote_port = neighbors[index]['port_id'].split('.')[0] # fix issue where cdp adjacency show subinterface
                        local_device_name = self.hostname
                        local_port = neighbors[index]['local_interface'].split('.')[0]# fix issue where cdp adjacency show subinterface
                        
                        # finding actual local device name
                        obj_vc = VirtualChassis(hostname=self.hostname)
                        if not obj_vc.flag_vc_presence:
                            # single device
                            pass
                        
                        if obj_vc.flag_vc_presence:
                            # stack found
                            if local_port == "GigabitEthernet0/0" or local_port == "FastEthernet0" or local_port == "FastEthernet1":
                                if obj_vc.master:
                                    local_device_name = obj_vc.master
                                
                                if not obj_vc.master:
                                    local_device_name = f"{local_device_name}_1"
                                    
                            if local_port != "GigabitEthernet0/0" and local_port != "FastEthernet0" and local_port != "FastEthernet1":
                                swi_num = switch_number_interface(interface=local_port)
                                if swi_num:
                                    local_device_name = f"{local_device_name}_{swi_num}"
                        
                        # finding actual remote device name
                        obj_vc = VirtualChassis(hostname=remote_device_name)
                        if not obj_vc.flag_vc_presence:
                            # single device found
                            pass
                        
                        if obj_vc.flag_vc_presence:
                            # stack found
                            if remote_port == "GigabitEthernet0/0" or remote_port == "FastEthernet0" or remote_port == "FastEthernet1":
                                if obj_vc.master:
                                    remote_device_name = obj_vc.master
                                
                                if not obj_vc.master:
                                    remote_device_name = f"{remote_device_name}_1"
                                    
                            if remote_port != "GigabitEthernet0/0" and remote_port != "FastEthernet0" and remote_port != "FastEthernet1":
                                swi_num = switch_number_interface(interface=remote_port)
                                if swi_num:
                                    remote_device_name = f"{remote_device_name}_{swi_num}"
                        
                        # final validate presense of remove device
                        obj_remote_device = netbox_api.dcim.devices.get(name__ie=remote_device_name)
                        if obj_remote_device:
                            loop_connection = {'a_device': local_device_name, 'a_port': local_port,
                                            'b_device': remote_device_name, 'b_port': remote_port}
                            con_record.append(loop_connection)

                if len(con_record) > 0:
                    self.connection_records = con_record

class AdjacencyStackPorts(Adjacency):
    def __init__(self, hostname, adjacency_table) -> None:
        super().__init__("Stack", hostname, adjacency_table)

class AdjacencyNormal(Adjacency):
    def __init__(self, hostname, adjacency_table) -> None:
        super().__init__("Normal", hostname, adjacency_table)
