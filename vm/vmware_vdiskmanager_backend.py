import os

# todo add platform specific checks and look instead of presume location
_vdiskmanager = "/Applications/VMware Fusion.app/Contents/Library/vmware-vdiskmanager"


class VMwareVDiskManagerBackend:

    def __init__(self, *, shell, location):
        self._shell = shell
        self._perms = None
        self._group = None
        self._location = location

    def diskValidateFreeSpace(self, location, size_gb):
        # Implement me
        return True

    def diskCreate(self, *, disk_name, size_gb):
        if not self.diskValidateFreeSpace(self._location, size_gb):
            raise Exception('Not enough free space in:%s' % self._location)
        self._shell.mkdir(os.path.join(self._location, disk_name))
        target_disk = os.path.join(self._location, disk_name, disk_name + ".vmdk")

        self._shell.execute_process(
            [_vdiskmanager, '-c', '-t', '0', '-s', '%sGB' % size_gb, '-a', 'lsilogic', target_disk])

        return target_disk

    def diskDelete(self, disk_name):
        target_disk = os.path.join(self._location, disk_name)
        self._shell.execute_process(['rm', '%s' % target_disk])

    def diskCopy(self, source, dest):
        self._shell.execute_process(['cp', source, dest])
        
    @property
    def location(self):
        return self._location

    @property
    def location(self):
        return self._location

    @property
    def perms(self):
        return self._perms

    @property
    def group(self):
        return self._group
