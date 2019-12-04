import os
import fabric
from util import util


def winGetBootFloppyFolder():
    script_dir = os.path.dirname(__file__)
    folder_path = os.path.join(script_dir, "boot_floppy")
    return folder_path


def winGetBootFloppyFileName(name):
    return os.path.join(winGetBootFloppyFolder(), name)


class WindowsAutoInst:

    def __init__(self, *, shell, location, admin_password="APassword1_", group=None, perms=None):
        self._admin_password = admin_password
        self._shell = shell
        self._perms = perms
        self._group = group
        self._location = location
        if self._shell is None:
            raise Exception('Require a shell')

    def _mkfs(self, floppy_image_name):
        result, stdout, stderr = self._shell.execute_process(['uname'])

        stdout = stdout.strip()

        if stdout == 'Linux':
            self._shell.execute_process(['mkfs.msdos', floppy_image_name])
            return

        if stdout == 'Darwin':
            result, stdout, stderr = self._shell.execute_process(
                ['hdiutil', 'attach', '-imagekey', 'diskimage-class=CRawDiskImage', '-nomount', floppy_image_name])
            disk = stdout.strip()
            self._shell.execute_process(['newfs_msdos', '-v' 'UNATTENDED', disk])
            self._shell.execute_process(['sync'])
            self._shell.execute_process(['hdiutil', 'detach', disk])
            return

        raise Exception("Shell remote or local does not support mkfs.msdos or newfs_msdos")

    def _prepareFile(self,  temp_location, source_file_name, key_vals):
        file = open(winGetBootFloppyFileName(source_file_name), "r")
        boostrap_text = file.read()
        for key, val in key_vals.items():
            boostrap_text = boostrap_text.replace(key, val)
        file_name = os.path.join(temp_location, source_file_name)
        file = open(file_name, "w+")
        file.write(boostrap_text)
        return file_name

    def _prepareBootstrap(self, name, host_ip):
        temp_location = os.path.join(winGetBootFloppyFolder(), "%s-temp" % name)
        os.mkdir(temp_location)
        self._prepareFile(temp_location, "boostrap.ps1", {"${PINGBACK_URL}": "http://%s:5000" % host_ip })
        self._prepareFile(temp_location, "autounattend.xml", {"${ADMIN_PASSWORD}": self._admin_password})
        return temp_location

    def _prepareBootstrap2(self, name, host_ip):
        file = open(winGetBootFloppyFileName("bootstrap.ps1"), "r")
        boostrap_text = file.read()
        boostrap_text = boostrap_text.replace("${PINGBACK_URL}", "http://%s:5000" % host_ip)
        temp_location = os.path.join(winGetBootFloppyFolder(), "%s-temp" % name)
        os.mkdir(temp_location)
        file = open(os.path.join(temp_location, "bootstrap.ps1"), "w+")
        file.write(boostrap_text)
        return os.path.join(temp_location, "bootstrap.ps1")

    def winCreateFloppy(self, *, name, pingback_ip):
        with util.cleanup() as create_floppy_cleanup:
            floppy_image_name = os.path.join(self._location, name + 'floppy.img')
            remote_temp_location = os.path.join(self._location, name + '-temp')

            temp_location = os.path.join(winGetBootFloppyFolder(), "%s-temp" % name)
            os.mkdir(temp_location)
            create_floppy_cleanup.add(lambda: os.rmdir(temp_location))

            bootstrap_filename = self._prepareFile(temp_location, "bootstrap.ps1", {"${PINGBACK_URL}": "http://%s:5000" % pingback_ip})
            create_floppy_cleanup.add(lambda: os.unlink(bootstrap_filename))

            auto_unattend_filename = self._prepareFile(temp_location, "autounattend.xml", {"${ADMIN_PASSWORD}": self._admin_password})
            create_floppy_cleanup.add(lambda: os.unlink(auto_unattend_filename))

            self._shell.execute_process(['mkdir', remote_temp_location])
            create_floppy_cleanup.add(lambda: self._shell.execute_process(['rm', '-rf', remote_temp_location]))

            self._shell.put(bootstrap_filename, remote_temp_location)
            self._shell.put(auto_unattend_filename, remote_temp_location)
            self._shell.put(winGetBootFloppyFileName('bootstrap.cmd'), remote_temp_location)
            self._shell.put(bootstrap_filename, remote_temp_location)
            self._shell.execute_process(['dd', 'if=/dev/zero', 'of=%s' % floppy_image_name, 'count=1440', 'bs=1k'])
            self._mkfs(floppy_image_name)
            self._shell.execute_process(
                ['mcopy', '-i', floppy_image_name, "%s/autounattend.xml" % remote_temp_location, '::/'])
            self._shell.execute_process(
                ['mcopy', '-i', floppy_image_name, "%s/bootstrap.cmd" % remote_temp_location, '::/'])
            self._shell.execute_process(
                ['mcopy', '-i', floppy_image_name, "%s/bootstrap.ps1" % remote_temp_location, '::/'])

            if self._group:
                self._shell.execute_process(['chgrp', self._group, floppy_image_name])

            if self._perms:
                self._shell.execute_process(['chmod', self._perms, floppy_image_name])

            return floppy_image_name

    def winDeleteFloppy(self, *, name):
        floppy_image_name = os.path.join(self._location, name + 'floppy.img')
        print("winDeleteFloppy:%s" % floppy_image_name)
        self._shell.execute_process(['rm', floppy_image_name])
