from util import util
import socket
import uuid
from pingback import pingback


def build_windows_base_image(vm_backend, disk_backend, windows_autoinst, winrs, disk_location, size_gb, iso, iso_drivers):
    with util.cleanup() as base_image_cleanup:
        vm_id = str(uuid.uuid1())
        vm_name = 'image_build-' + vm_id

        disk_backend.diskCreate(disk_location, vm_name, size_gb)
        base_image_cleanup.add(lambda: disk_backend.diskDelete(disk_location, vm_name))

        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)

        floppy = windows_autoinst.winCreateFloppy(disk_location, vm_name, host_ip)
        base_image_cleanup.add(lambda: windows_autoinst.winDeleteFloppy(disk_location, vm_name))

        mac_address = 'FA:FA:FA:FA:FA:FA'
        vm_backend.vmCreate('WindowsTemplate', vm_name, iso, iso_drivers, mac_address, vm_id, disk_location, vm_name,
                         floppy)

        base_image_cleanup.add(lambda: vm_backend.vmDelete(vm_name))

        vm_backend.vmPowerOn(vm_name)
        base_image_cleanup.add(lambda: vm_backend.vmPowerOff(vm_name))
        print('VM Started - waiting for ping back')

        pingback.start_server()
        base_image_cleanup.add(lambda: pingback.stop_server())

        if not util.wait_for(lambda: pingback.get_stored_ip(), time_out=600, operation_name="Waiting", wait_name="Pingback"):
            print('Failed to get ping back')
            return False

        ip = pingback.get_stored_ip()

        print("Got ping back from:%s" % ip)

        print('Waiting for winrs connection')
        winrs.set_host(ip)
        if not winrs.remoteWaitDeviceIsAwake():
            print('failed to wait for device')
            return False

        print('Installing Winstall')
        winrs.remoteInstallWinstall()

