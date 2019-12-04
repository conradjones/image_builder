import os


class LibVirtDiskBackEnd:

    def __init__(self, *, shell, location, group=None, perms=None):
        self._shell = shell
        self._perms = perms
        self._group = group
        self._location = location
        if self._shell is None:
            raise Exception('Require a shell')

    def diskValidateFreeSpace(self, location, sizeGB):
        # Implement me
        return True

    def diskCreate(self, disk_name, size_gb):
        if not self.diskValidateFreeSpace(self._location, size_gb):
            raise Exception('Not enough free space in:%s' % self._location)
        target_disk = os.path.join(self._location, "%s.qcow2" % disk_name)
        self._shell.execute_process(['qemu-img', 'create', '-f', 'qcow2', target_disk, '%sG' % size_gb])

        if self._group:
            self._shell.execute_process(['chgrp', self._group, target_disk])

        if self._perms:
            self._shell.execute_process(['chmod', self._perms, target_disk])

        return target_disk

    def diskDelete(self, location, disk_name):
        target_disk = os.path.join(location, disk_name)
        self._shell.execute_process(['rm', '%s.qcow2' % target_disk])

    @property
    def location(self):
        return self._location

    @property
    def perms(self):
        return self._perms

    @property
    def group(self):
        return self._group
