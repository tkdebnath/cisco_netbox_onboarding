import os
import pynetbox

netbox_api = pynetbox.api(
url=os.environ.get("URL"),
token=os.environ.get("API_KEY"),
threading=True
)

#disable ssl verification
netbox_api.http_session.verify = False

    

