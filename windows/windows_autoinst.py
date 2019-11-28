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

    def __init__(self, conn_string):
        self._conn = fabric.Connection(conn_string)
        if self._conn is None:
            raise Exception('Failed to connect to :%s' % conn_string)

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
            self._conn.run('mkdir %s' % remote_temp_location)
            create_floppy_cleanup.add(lambda: self._conn.run('rm -rf %s' % remote_temp_location))

            self._conn.put(winGetBootFloppyFileName('autounattend.xml'), remote_temp_location)
            self._conn.put(winGetBootFloppyFileName('bootstrap.cmd'), remote_temp_location)
            self._conn.put(bootstrap_filename, remote_temp_location)
            self._conn.run('dd if=/dev/zero of=%s count=1440 bs=1k' % floppy_image_name, hide='both')
            self._conn.run('mkfs.msdos %s' % floppy_image_name, hide='out')
            self._conn.run('mcopy -i %s %s/* ::/' % (floppy_image_name, remote_temp_location))
            self._conn.run('chgrp kvm %s' % floppy_image_name)
            self._conn.run('chmod g+w %s' % floppy_image_name)

            return floppy_image_name

    def winDeleteFloppy(self, location, name):
        floppy_image_name = os.path.join(location, name + 'floppy.img')
        print("winDeleteFloppy:%s" % floppy_image_name)
        self._conn.run('rm %s' % floppy_image_name)
