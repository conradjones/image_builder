import os

# todo add platform specific checks and look instead of presume location
_vdiskmanager = "/Applications/VMware Fusion.app/Contents/Library/vmware-vdiskmanager"


class VMwareVDiskManagerBackend:

    def __init__(self, shell):
        self._shell = shell

    def diskValidateFreeSpace(self, location, sizeGB):
        # Implement me
        return True

    def diskCreate(self, location, disk_name, sizeGB):
        if not self.diskValidateFreeSpace(location, sizeGB):
            raise Exception('Not enough free space in:%s' % location)
        target_disk = os.path.join(location, disk_name + ".vmdk")

        self._shell.execute_process(
            [_vdiskmanager, '-c', '-t', '0', '-s', '%sGB' % sizeGB, '-a', 'lsilogic', target_disk])

    def diskDelete(self, location, disk_name):
        target_disk = os.path.join(location, disk_name)
        self._shell.execute_process(['rm', '%s.vmdk' % target_disk])
