import unittest
from unittest.mock import Mock
from unittest.mock import call
from vm import libvirtdisk_backend
from shell import local

# NOTE THESE TESTS ARE NOT FINISHED AND NOT PARTICULARLY USEFUL YET


class LibVirtDiskBackEnd(unittest.TestCase):
    def test_diskCreate(self):
        shell = Mock()

        disk = libvirtdisk_backend.LibVirtDiskBackEnd(shell=shell, location="/somewhere", group="kvm", perms="g+w")
        disk.diskCreate("new_disk", 30)

        shell.execute_process.assert_has_calls(
            [call(['qemu-img', 'create', '-f', 'qcow2', "/somewhere/new_disk.qcow2", '30G']),
             call(['chgrp', 'kvm', "/somewhere/new_disk.qcow2"]),
             call(['chmod', 'g+w', "/somewhere/new_disk.qcow2"])]
        )

    def test_diskDelete(self):
        shell = Mock()

        disk = libvirtdisk_backend.LibVirtDiskBackEnd(shell=shell, location="/somewhere", group="kvm", perms="g+w")
        disk.diskDelete("/somewhere/new_disk.qcow2")

        shell.execute_process.assert_has_calls(
            [call(['rm', "/somewhere/new_disk.qcow2"])])

if __name__ == '__main__':
    unittest.main()
