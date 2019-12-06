from unittest import mock
from unittest.mock import Mock
import unittest.mock
from unittest.mock import call
from vm import libvirt_backend
from shell import local

# NOTE THESE TESTS ARE NOT FINISHED AND NOT PARTICULARLY USEFUL YET

@mock.patch('libvirt.open')
def mock_open(name=None):
    return Mock()


class LibVirtBackEnd(unittest.TestCase):
    def test_diskCreate(self):
        shell = Mock()

        virt = libvirt_backend.LibVirtBackEnd(conn_string="ssh://not-really-here.com")
        virt.vmExists("Fred")

if __name__ == '__main__':
    unittest.main()
