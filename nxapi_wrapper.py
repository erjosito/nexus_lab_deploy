import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from pyntc import ntc_device
from datetime import datetime
import os
from time import sleep
import socket

class nxapi_wrapper(object):

    def __init__(self, host, username, password):

        self.host = host
        self.username = username
        self.password = password

        self.device = ntc_device(host=host, username=username, password=password, device_type='cisco_nxos_nxapi')

        # Disable HTTPS warnings
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def backup_running_config(self, file):
        self.device.backup_running_config(file)

    def set_running_config(self, file):
        self.device.config("feature scp-server")
        self.device.config("feature sftp-server")
        self.device.file_copy(src=file, dest=None, file_system='bootflash:')
        self.device.config("copy bootflash:%s startup-config" % os.path.basename(file))
        self.device.config("terminal dont-ask")

        try:
            self.device.config("reload")
        except Exception:
            pass

        while(not self._reachable()):
            print("Device %s still reloading [%s]" % (self.host, datetime.now().strftime("%X")))
            sleep(20)
        print("Device %s reachable again" % self.host)
        print("Start cleanup bootflash")
        self.device.config("terminal dont-ask")
        self.device.config("delete bootflash:%s" % os.path.basename(file))
        print("Finished cleanup bootflash")

    def _reachable(self):
        try:
            s = socket.socket()
            s.settimeout(2)
            s.connect((self.host, 80))
            return True
        except Exception:
            return False