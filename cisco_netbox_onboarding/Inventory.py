from .Netbox_Connector import netbox_api

class Inventory:
    def __init__(self, module_bay, device, module_type) -> None:
        self.module_bay = module_bay
        self.module_bay_id = None
        self.device_id = netbox_api.dcim.devices.get(name__ie=device).id
        self.module_type_id = netbox_api.dcim.module_types.get(part_number__ie=module_type).id
        self.serial = None
        self.description = None
        self.uuid_module = None

        # update bay
        self.locate_bay()
    
    def locate_bay(self) -> None:
        if self.device_id:
            if self.module_bay == "Network Module":
                obj_module_bay = netbox_api.dcim.module_bays.get(device_id=self.device_id, name__ic="Network Module")
                if not obj_module_bay:
                    raise ValueError(f"Device id: {self.device_id}, no module bay exist")
                if obj_module_bay:
                    self.module_bay_id = obj_module_bay.id

            if self.module_bay == "Fan":
                pass
    
    def attach_module(self) -> None:
        if self.device_id and self.module_bay_id and self.module_type_id:
            obj_module = netbox_api.dcim.modules.get(device_id=self.device_id, module_bay_id=self.module_bay_id)
            if not obj_module:
                obj_module = netbox_api.dcim.modules.create(
                    device = self.device_id,
                    module_bay = self.module_bay_id,
                    module_type = self.module_type_id,
                    status = "active"
                )
            
            if obj_module:
                # update serial and description
                if self.serial:
                    obj_module.serial = self.serial
                if self.description:
                    obj_module.description = self.description
                obj_module.save()
                self.uuid_module = obj_module.id
                

class NetworkModule(Inventory):
    def __init__(self, device, module_type) -> None:
        super().__init__("Network Module", device, module_type)
    