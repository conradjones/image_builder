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

    def __init__(self,  *, shell, group=None, perms=None):
        self._shell = shell
        self._perms = perms
        self._group = group
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

    def _prepareBootstrap(self, name, host_ip):
        file = open(winGetBootFloppyFileName("bootstrap.ps1"), "r")
        xml_text = file.read()
        xml_text = xml_text.replace("${PINGBACK_URL}", "http://%s:5000" % host_ip)
        temp_location = os.path.join(winGetBootFloppyFolder(), "%s-temp" % name)
        os.mkdir(temp_location)
        file = open(os.path.join(temp_location, "bootstrap.ps1"), "w+")
        file.write(xml_text)
        return os.path.join(temp_location, "bootstrap.ps1")

    def winCreateFloppy(self, location, name, pingback_ip):
        with util.cleanup() as create_floppy_cleanup:
            floppy_image_name = os.path.join(location, name + 'floppy.img')
            remote_temp_location = os.path.join(location, name + '-temp')

            bootstrap_filename = self._prepareBootstrap(name, pingback_ip)
            create_floppy_cleanup.add(lambda: os.rmdir(os.path.dirname(bootstrap_filename)))
            create_floppy_cleanup.add(lambda: os.unlink(bootstrap_filename))
            self._shell.execute_process(['mkdir', remote_temp_location])
            create_floppy_cleanup.add(lambda: self._shell.execute_process(['rm', '-rf', remote_temp_location]))

            self._shell.put(winGetBootFloppyFileName('autounattend.xml'), remote_temp_location)
            self._shell.put(winGetBootFloppyFileName('bootstrap.cmd'), remote_temp_location)
            self._shell.put(bootstrap_filename, remote_temp_location)
            self._shell.execute_process(['dd', 'if=/dev/zero', 'of=%s' % floppy_image_name, 'count=1440', 'bs=1k'])
            self._mkfs(floppy_image_name)
            self._shell.execute_process(['mcopy', '-i', floppy_image_name, "%s/autounattend.xml" % remote_temp_location, '::/'])
            self._shell.execute_process(['mcopy', '-i', floppy_image_name, "%s/bootstrap.cmd" % remote_temp_location, '::/'])
            self._shell.execute_process(['mcopy', '-i', floppy_image_name, "%s/bootstrap.ps1" % remote_temp_location, '::/'])

            if self._group:
                self._shell.execute_process(['chgrp', self._group, floppy_image_name])

            if self._perms:
                self._shell.execute_process(['chmod', self._perms, floppy_image_name])

            return floppy_image_name

    def winDeleteFloppy(self, location, name):
        floppy_image_name = os.path.join(location, name + 'floppy.img')
        print("winDeleteFloppy:%s" % floppy_image_name)
        self._shell.execute_process(['rm', floppy_image_name])
