# Cisco NetBox Onboarding

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![NetBox](https://img.shields.io/badge/NetBox-API-green.svg)
![License](https://img.shields.io/badge/License-GNU-yellow.svg)

A Python script to streamline the onboarding of Cisco devices into [NetBox](https://netbox.dev/), a popular IP address management (IPAM) and data center infrastructure management (DCIM) tool. This tool leverages the NetBox API to automate the creation of sites, devices, interfaces, and IP addresses based on a YAML configuration file.

---

## Overview

The `cisco_netbox_onboarding` script simplifies the process of adding Cisco network devices to NetBox. By defining device details in a YAML file, users can efficiently populate NetBox with accurate inventory data, reducing manual entry and potential errors. This is particularly useful for network engineers managing Cisco-powered infrastructures.

---

## Features

- **Automated Onboarding**: Creates NetBox objects (sites, devices, interfaces, IPs) from a YAML config.
- **Cisco-Focused**: Tailored for Cisco devices with platform support (e.g., `cisco_ios`).
- **Flexible Configuration**: Define multiple devices, interfaces, and IP assignments in a single YAML file.
- **API Integration**: Utilizes the NetBox REST API for seamless data insertion.
- **Error Handling**: Basic validation and feedback for API interactions.

---

## Prerequisites

Before using this script, ensure you have:

- **Python 3.x** installed on your system.
- A running **NetBox instance** with API access enabled.
- A valid **NetBox API token** (generated from the NetBox UI under your user profile).
- Access to the repository’s required Python packages (listed in `requirements.txt`).

---

## Installation

To install Cisco NetBox Onboarding, simply use pip:

```
$ pip install cisco_netbox_onboarding
```

or

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/tkdebnath/cisco_netbox_onboarding.git
   cd cisco_netbox_onboarding
   ```

2. **Set Up a Virtual Environment (optional but recommended)**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   ```plaintext
   URL=http://<your-netbox>/
   API_KEY=<your-api-token>
   NETMIKO_USERNAME=
   NETMIKO_PASSWORD=
   ```



## Usage/Examples

   ```python
   from cisco_netbox_onboarding import new_onboard
   import os

   if __name__=="__main__":

      # By default multithreading is enabled with 10 threads 

      ip_list = []

      """ Either set environment values for below variables"""

      os.environ["URL"] = "http://<your-netbox>"
      os.environ["API_KEY"] = "<your-api-token>"
      os.environ["NETMIKO_USERNAME"] = "username"
      os.environ["NETMIKO_PASSWORD"] = "password"

      results = new_onboard(ip_list=ip_list)

      
      """ or pass values with arguments """

      URL="http://<your-netbox>"
      API_KEY="<your-api-token>"
      NETMIKO_USERNAME="username"
      NETMIKO_PASSWORD="passord"

      results = new_onboard(ip_list=ip_list,
                           username=NETMIKO_USERNAME,
                           password=NETMIKO_PASSWORD,
                           url=URL,
                           api_key=API_KEY)
      

      # Result type is None or List of dictionary

      if results:
         for result in results:
               print(result)

               # if success {'ip': ip, 'hostname': hostname, 'msg': 'success'}

               # if failed : {'ip': ip, 'msg': msg}
   ```
