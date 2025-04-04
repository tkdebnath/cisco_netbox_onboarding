from .Netbox_Connector import netbox_api

class Connection:
    def __init__(self, a_device, a_port, b_device, b_port) -> None:
        self.a_device = a_device
        self.a_port = a_port
        self.b_device = b_device
        self.b_port = b_port
        self.a_obj_port = None
        self.b_obj_port = None
        self.cable = None
        self.a_terminations = None
        self.b_terminations = None
        self.cabling_required = True

        a_obj_port = netbox_api.dcim.interfaces.get(device=self.a_device, name__ie=self.a_port)
        b_obj_port = netbox_api.dcim.interfaces.get(device=self.b_device, name__ie=self.b_port)

        if not a_obj_port:
            raise ValueError(f"{self.a_device} has no port: {self.a_port}")
        
        if not b_obj_port:
            raise ValueError(f"{self.b_device} has no port: {self.b_port}")
        
        
        self.a_terminations = a_obj_port.id
        self.b_terminations = b_obj_port.id
        self.a_obj_port = a_obj_port
        self.b_obj_port = b_obj_port
    
        #Check if cabling required or not
        if self.a_obj_port.cable and self.b_obj_port.cable:
            if self.a_obj_port.cable.id == self.b_obj_port.cable.id:
                self.cable = a_obj_port.cable.id
                self.cabling_required = False
        
        #Delete existing cable if any cable found connected on any end
        if self.cabling_required:
            if self.a_obj_port.cable:
                self.a_obj_port.cable.delete()
            if self.b_obj_port.cable:
                self.b_obj_port.cable.delete()


    def make_connection(self):
        if not self.cabling_required:
            return self.cable

        if self.a_terminations and self.b_terminations:
            obj_cable = netbox_api.dcim.cables.create(
                a_terminations = [{"object_type": "dcim.interface", "object_id": self.a_terminations}],
                b_terminations = [{"object_type": "dcim.interface", "object_id": self.b_terminations}],
            )
            if obj_cable:
                self.cable = obj_cable.id
                return self.cable
            if not obj_cable:
                return None
        
        raise ValueError(f"Cable can't be connected")
            

if __name__=='__main__':
    obj_connections = Connection("SSK-7-SWI-01_1", "TwentyFiveGigE1/1/1", "dmi01-albany-sw01", "GigabitEthernet1/0/3")
    print(obj_connections.make_connection())