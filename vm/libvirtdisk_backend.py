import os
import fabric


class LibVirtDiskBackEnd:

    def __init__(self, conn_string):
        self._conn = fabric.Connection(conn_string)
        if self._conn is None:
            raise Exception('Failed to connect to :%s' % conn_string)

    def diskValidateFreeSpace(self, location, sizeGB):
        #Implement me
        return True

    def diskCreate(self, location, name, sizeGB):
        if not self.diskValidateFreeSpace(location, sizeGB):
            raise Exception('Not enough free space in:%s' % location)
        target_disk = os.path.join(location, name)
        self._conn.run('qemu-img create -f qcow2 %s.qcow2 %sG' % (target_disk, sizeGB), hide=False)
        self._conn.run('chgrp kvm %s.qcow2' % target_disk)
        self._conn.run('chmod g+w %s.qcow2' % target_disk)