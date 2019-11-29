from pypsrp.client import Client
import os
import zipfile
from util import util
import tempfile
from pypsrp.powershell import PowerShell, RunspacePool
from pypsrp.wsman import WSMan


def winRsGetWinstallFolder():
    script_dir = os.path.dirname(__file__)
    folder_path = os.path.join(script_dir, "winstall")
    return folder_path


def _print_stream(stream):
    for item in stream:
        print(str(item))

def _print_error_stream(stream):
    for item in stream:
        print(str(item))
        print(item.script_stacktrace)

def _output_powershell_streams(ps):
    _print_stream(ps.streams.verbose)
    _print_error_stream(ps.streams.error)


class WinRsRemote:

    def __init__(self, *, host=None, user, auth):
        self._host = host
        self._user = user
        self._auth = auth
        with open(os.path.join(winRsGetWinstallFolder(), 'installer.ps1'), "r") as file:
            self._installer_script = file.read()

    def set_host(self, host):
        self._host = host

    def connect(self):
        if self._host is None:
            raise Exception('WinRsRemote host not set')

        try:
            self._client = WSMan(self._host, auth="basic", username=self._user, password=self._auth,
                                 ssl=False, connection_timeout=10, encryption='never')
            with RunspacePool(self._client) as pool:
                ps = PowerShell(pool)
                ps.add_cmdlet("Get-Process")
                ps.invoke()
        except BaseException as e:
            return False

        return True

    def _zip_dir(self, path, zip_handle):
        for root, dirs, files in os.walk(path):
            for file in files:
                zip_handle.write(os.path.join(root, file))

    def _get_powershell_script(self, name):
        script_dir = os.path.dirname(__file__)
        rel_path = "ps_scripts/%s" % name
        file_path = os.path.join(script_dir, rel_path)
        file = open(file_path, "r")
        return file.read()

    def _copy_package_to_remote(self, package_name):
        client = Client(self._host, username=self._user, password=self._auth, ssl=False, connection_timeout=10)
        with util.cleanup() as copy_package_cleanup:
            local_temp_folder = tempfile.mkdtemp()
            copy_package_cleanup.add(lambda: os.rmdir(local_temp_folder))

            local_temp_zip = os.path.join(local_temp_folder, package_name + '.zip')

            with zipfile.ZipFile(local_temp_zip, 'w', zipfile.ZIP_DEFLATED) as zip_handle:
                copy_package_cleanup.add(lambda: os.unlink(local_temp_zip))

                with util.chdir(winRsGetWinstallFolder()):
                    self._zip_dir(package_name, zip_handle)
                zip_handle.close()

                remote_zip = "c:\\.winstall\\transfer\\%s.zip" % package_name
                client.copy(local_temp_zip, remote_zip)
                return remote_zip

    def _unzip_remote_package(self, remote_zip):
        with RunspacePool(self._client) as pool:
            ps = PowerShell(pool)
            ps.add_cmdlet("Expand-Archive").add_parameter("Path", remote_zip).add_parameter("Destination", "c:\\.winstall\\packages")
            ps.add_cmdlet("Remove-Item").add_parameter("Path", remote_zip).add_parameter("Force")
            ps.invoke()

    def remoteCreateWinstallRoot(self):
        ps_script = self._get_powershell_script('create_winstall_root.ps1')
        with RunspacePool(self._client) as pool:
            ps = PowerShell(pool)
            ps.add_script(ps_script)
            ps.invoke()

    def remoteInstallWinstall(self):
        self.remoteCreateWinstallRoot()

    def remoteInstallPackage(self, package_name):
        print("remoteInstallPackage:%s" % package_name)
        remote_zip = self._copy_package_to_remote(package_name)
        self._unzip_remote_package(remote_zip)

        remote_path = "c:\\.winstall\\packages\\%s" % package_name

        with RunspacePool(self._client) as pool:
            ps = PowerShell(pool)
            ps.add_script(self._installer_script).add_parameter("ComponentPath", remote_path)
            ps.invoke()
            _output_powershell_streams(ps)
            if ps.had_errors:
                raise Exception("remoteInstallPackage:error installing: %s" % package_name)


    def remoteWaitDeviceIsAwake(self):
        return util.wait_for(lambda: self.connect(), operation_name="remoteDeviceIsAwake",
                             wait_name="Ping %s" % self._host)
