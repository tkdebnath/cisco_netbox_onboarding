from .Netbox_Connector import netbox_api

class VirtualChassis:
    def __init__(self, hostname) -> None:
        self.vc_name = hostname.upper()
        self.master = None
        self.id = None
        self.flag_vc_presence = None

        # Checking if VC exist or not
        obj_vc = netbox_api.dcim.virtual_chassis.get(name__ie=self.vc_name)
        if obj_vc:
            self.flag_vc_presence = True
            if obj_vc.master:
                self.master = obj_vc.master.name
    
    def update_db(self):
        obj_vc = netbox_api.dcim.virtual_chassis.get(name__ie=self.vc_name)
        if not obj_vc:
            obj_vc = netbox_api.dcim.virtual_chassis.create(
                name = self.vc_name.upper()
            )
        
        if obj_vc:
            if self.master:
                obj_vc.master = netbox_api.dcim.devices.get(name__ie=self.master).id
                obj_vc.save()
            self.id = obj_vc.id

    


