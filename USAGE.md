# Cisco NetBox Onboarding

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![NetBox](https://img.shields.io/badge/NetBox-API-green.svg)
![License](https://img.shields.io/badge/License-GNU-yellow.svg)

A Python script to streamline the onboarding of Cisco devices into [NetBox](https://netbox.dev/), a popular IP address management (IPAM) and data center infrastructure management (DCIM) tool. This tool leverages the NetBox API to automate the creation of sites, devices, interfaces, and IP addresses based on a YAML configuration file.

## Usage/Examples

#### Importing module
   ```python
   from cisco_netbox_onboarding import new_onboard
   import os
   ```

#### Execute 
   ```python
   # By default multithreading is enabled with 10 threads 
   ip_list = []
   *** Set environment values for below variables ***

   os.environ["URL"] = "http://<your-netbox>"
   os.environ["API_KEY"] = "<your-api-token>"
   os.environ["NETMIKO_USERNAME"] = "username"
   os.environ["NETMIKO_PASSWORD"] = "password"
   results = new_onboard(ip_list=ip_list)
   ```
   ```python
   *** OR pass values with arguments ***

   URL="http://<your-netbox>"
   API_KEY="<your-api-token>"
   NETMIKO_USERNAME="username"
   NETMIKO_PASSWORD="passord"

   results = new_onboard(ip_list=ip_list,
                        username=NETMIKO_USERNAME,
                        password=NETMIKO_PASSWORD,
                        url=URL,
                        api_key=API_KEY)
   ```
   ```python
      # Result type is None or List of dictionary

      if results:
         for result in results:
               print(result)

               # if success {'ip': ip, 'hostname': hostname, 'msg': 'success'}

               # if failed : {'ip': ip, 'msg': msg}
   ```
