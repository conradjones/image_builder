from util import util
import socket
import uuid
from pingback import pingback


def _guess_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def build_windows_base_image(vm_backend, disk_backend, windows_autoinst, winrs, disk_location, size_gb, iso, iso_drivers, packages, *, keep_vm=False):
    with util.cleanup() as base_image_cleanup:
        vm_id = str(uuid.uuid1())
        vm_name = 'image_build-' + vm_id

        disk_backend.diskCreate(disk_location, vm_name, size_gb)
        base_image_cleanup.add(lambda: disk_backend.diskDelete(disk_location, vm_name))

        host_ip = _guess_local_ip()
        print("buildImage:local ip %s" % host_ip)

        floppy = windows_autoinst.winCreateFloppy(disk_location, vm_name, host_ip)
        base_image_cleanup.add(lambda: windows_autoinst.winDeleteFloppy(disk_location, vm_name))

        mac_address = 'FA:FA:FA:FA:FA:FA'
        vm_backend.vmCreate('WindowsTemplate', vm_name, iso, iso_drivers, mac_address, vm_id, disk_location, vm_name,
                         floppy)

        if not keep_vm:
            base_image_cleanup.add(lambda: vm_backend.vmDelete(vm_name))

        vm_backend.vmPowerOn(vm_name)
        if not keep_vm:
            base_image_cleanup.add(lambda: vm_backend.vmPowerOff(vm_name))
        print('buildImage:waiting for ping back')

        pingback.start_server()
        base_image_cleanup.add(lambda: pingback.stop_server())

        if not util.wait_for(lambda: pingback.get_stored_ip(), time_out=600, operation_name="Waiting", wait_name="Pingback"):
            print('buildImage:failed to get ping back')
            return False

        ip = pingback.get_stored_ip()

        print("buildImage:ping back from %s" % ip)

        print('buildImage:waiting for winrs connection')
        winrs.set_host(ip)
        if not winrs.remoteWaitDeviceIsAwake():
            print('buildImage:failed to wait for device')
            return False

        print('buildImage:installing Winstall')
        winrs.remoteInstallWinstall()

        winrs.remoteInstallPackage('windows_defender_disable')

        print('buildImage:rebooting device')
        winrs.remoteReboot()

        print('buildImage:installing packages')
        for package in packages:
            result = winrs.remoteInstallPackage(package)
            if "Reboot" not in result:
                continue

            print('buildImage:reboot required, rebooting....')
            winrs.remoteReboot()

        input("buildImage:Press Enter to continue...")

        return True

