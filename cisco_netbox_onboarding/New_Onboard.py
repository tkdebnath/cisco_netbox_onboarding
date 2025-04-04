import os
from netmiko import ConnectHandler
from multiprocessing.dummy import Pool as ThreadPool
from .Tasks import Onboarding
from .Netbox_Connector import netbox_api
import genie

def check_host(ip):

    host = {
        'host': ip,
        'device_type': 'cisco_xe',
        'fast_cli': False,
        'username': os.getenv("NETMIKO_USERNAME"),
        'password': os.getenv("NETMIKO_PASSWORD"),
        'secret': os.getenv("NETMIKO_SECRET"),
    }
    
    try:
        net_connect = ConnectHandler(**host)
        
        #without enable mode
        if ">" in net_connect.find_prompt():
            pass
        hostname = net_connect.find_prompt().replace(">", "").replace("#", "").upper()
        
        site = hostname[0:3].upper()
        # check if site already present in netbox or not
        obj_site = netbox_api.dcim.sites.get(name__ie=site)
        if not obj_site:
            site = "XXX"
        
        show_version = net_connect.send_command(command_string="show version", use_genie=True, read_timeout=300)
        show_interface = net_connect.send_command(command_string="show interface", use_genie=True, read_timeout=300)
        # show_inventory = net_connect.send_command(command_string="show inventory", use_genie=True, read_timeout=300)
        show_inventory = "{'dummy': True}"
        show_cdp = net_connect.send_command(command_string="show cdp neighbors detail", use_genie=True, read_timeout=300)
        
        
        if isinstance(show_version, genie.conf.base.utils.QDict):
            show_version = dict(show_version)
        if isinstance(show_interface, genie.conf.base.utils.QDict):
            show_interface = dict(show_interface)
        if isinstance(show_inventory, genie.conf.base.utils.QDict):
            show_inventory = dict(show_inventory)
        if isinstance(show_cdp, genie.conf.base.utils.QDict):
            show_cdp = dict(show_cdp)
        
        
        obj_onboard = Onboarding(hostname=hostname, site=site, version=show_version, interfaces=show_interface, inventory=show_inventory)
        obj_onboard.cdp_neighbors_detail = show_cdp
        obj_onboard.automatic()
        net_connect.disconnect()
        
        return {'ip': ip, 'hostname': hostname, 'msg': 'success'}
    except Exception as msg:
        print(f"{ip}: Conn failed {msg}")
        return {'ip': ip, 'msg': msg}

def new_onboard(ip_list: list):
    threads = ThreadPool(10)
    results = threads.map(check_host, ip_list)
    threads.close()
    threads.join()
    
    return results
    