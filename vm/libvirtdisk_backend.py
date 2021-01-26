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

    def diskCreate(self, disk_name, size_gb, *, parent_disk=None):
        if not self.diskValidateFreeSpace(self._location, size_gb):
            raise Exception('Not enough free space in:%s' % self._location)
        target_disk = os.path.join(self._location, "%s.qcow2" % disk_name)

        args = ['qemu-img', 'create']

        if parent_disk is not None:
            args += ["-b", parent_disk, "-F", "qcow2"]

        args += ['-f', 'qcow2', target_disk]
        if parent_disk is None:
            args += ['%sG' % size_gb]

        self._shell.execute_process(args)

        if self._group:
            self._shell.execute_process(['chgrp', self._group, target_disk])

        if self._perms:
            self._shell.execute_process(['chmod', self._perms, target_disk])

        return target_disk

    def diskDelete(self, disk_name):
        self._shell.execute_process(['rm', disk_name])

    def diskCopy(self, source, dest):
        self._shell.execute_process(['cp', source, dest])

        if self._group:
            self._shell.execute_process(['chgrp', self._group, dest])

        if self._perms:
            self._shell.execute_process(['chmod', self._perms, dest])

    @property
    def location(self):
        return self._location

    @property
    def perms(self):
        return self._perms

    @property
    def group(self):
        return self._group
