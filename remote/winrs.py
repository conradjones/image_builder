from pypsrp.client import Client
import socket
import os
import urllib3
from util import util
import requests

class WinRsRemote:
    def __init__(self, host, user, auth):
        self._host = host
        self._user = user
        self._auth = auth

    def connect(self):
        self._client = Client(self._host, username=self._user, password=self._auth, ssl=False, connection_timeout=10)
        try:
            self._client.execute_cmd("ipconfig")
        except BaseException as e:
            return False

        return True

    def _get_powershell_script(self, name):
        script_dir = os.path.dirname(__file__)
        rel_path = "ps_scripts/%s" % name
        file_path = os.path.join(script_dir, rel_path)
        file = open(file_path, "r")
        return file.read()

    def remoteCreateWinstallRoot(self):
        ps_script = self._get_powershell_script('create_winstall_root.ps1')
        output, streams, had_errors = self._client.execute_ps(ps_script)
        print(output)

    def remoteInstallWinstall(self):
        ps_script = self._get_powershell_script('install_winstall.ps1')
        output, streams, had_errors = self._client.execute_ps(ps_script)
        print(output)

    def remoteInstallPackage(self, package_name):
        output, streams, had_errors = self._client.execute_ps("c:\\.winstall\\winstall-master\\installer.ps1 %s" % package_name)
        print(output)

    def remoteWaitDeviceIsAwake(self):
        return util.wait_for(lambda: self.connect(), "remoteDeviceIsAwake", "Ping %s" % self._host)