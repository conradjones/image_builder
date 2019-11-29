from pypsrp.client import Client
import os, shutil
import zipfile
from util import util
import tempfile


def winRsGetWinstallFolder():
    script_dir = os.path.dirname(__file__)
    folder_path = os.path.join(script_dir, "winstall")
    return folder_path


class WinRsRemote:

    def __init__(self, *, host=None, user, auth):
        self._host = host
        self._user = user
        self._auth = auth

    def set_host(self, host):
        self._host = host

    def connect(self):
        if self._host is None:
            raise Exception('WinRsRemote host not set')

        self._client = Client(self._host, username=self._user, password=self._auth, ssl=False, connection_timeout=10)
        try:
            self._client.execute_cmd("ipconfig")
            self._client.execute_ps("Get-Process")
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
                self._client.copy(local_temp_zip, remote_zip)
                return remote_zip

    def _unzip_remote_package(self, remote_zip):
        self._client.execute_ps(
            "Expand-Archive -Path %s -Destination c:\\.winstall\\packages" % remote_zip)
        self._client.execute_ps("Remove-Item -Path %s -Force" % remote_zip)


    def remoteCreateWinstallRoot(self):
        ps_script = self._get_powershell_script('create_winstall_root.ps1')
        output, streams, had_errors = self._client.execute_ps(ps_script)
        print(output)

    def remoteInstallWinstall(self):
        self.remoteCreateWinstallRoot()
        self._client.copy(os.path.join(winRsGetWinstallFolder(), 'installer.ps1'), 'c:\\.winstall\\installer.ps1')

    def remoteInstallPackage(self, package_name):

        remote_zip = self._copy_package_to_remote(package_name)
        self._unzip_remote_package(remote_zip)

        output, streams, had_errors = self._client.execute_ps(
            "c:\\.winstall\\installer.ps1 -ComponentPath c:\\.winstall\\packages\\%s" % package_name)
        if had_errors:
            error_str = ""
            for error in streams.error:
                error_str += str(error) + "\n"
            raise Exception("Error installing: %s \n%s" % (package_name, error_str))
        print(output)

    def remoteWaitDeviceIsAwake(self):
        return util.wait_for(lambda: self.connect(), operation_name="remoteDeviceIsAwake", wait_name="Ping %s" % self._host)
