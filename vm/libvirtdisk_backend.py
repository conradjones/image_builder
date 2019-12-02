import os


class LibVirtDiskBackEnd:

    def __init__(self, *, shell, group=None, perms=None):
        self._shell = shell
        self._perms = perms
        self._group = group
        if self._shell is None:
            raise Exception('Require a shell')

    def diskValidateFreeSpace(self, location, sizeGB):
        #Implement me
        return True

    def diskCreate(self, location, disk_name, sizeGB):
        if not self.diskValidateFreeSpace(location, sizeGB):
            raise Exception('Not enough free space in:%s' % location)
        target_disk = os.path.join(location, "%s.qcow2" % disk_name)
        self._shell.execute_process(['qemu-img', 'create', '-f', 'qcow2', target_disk, '%sG' % sizeGB])

        if self._group:
            self._shell.execute_process(['chgrp', self._group, target_disk])

        if self._perms:
            self._shell.execute_process(['chmod', self._perms, target_disk])

    def diskDelete(self, location, disk_name):
        target_disk = os.path.join(location, disk_name)
        self._shell.execute_process(['rm',  '%s.qcow2' % target_disk])
