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

        disk_backend.diskCreate(vm_name, size_gb)
        base_image_cleanup.add(lambda: disk_backend.diskDelete(disk_location, vm_name))

        host_ip = _guess_local_ip()
        print("buildImage:local ip %s" % host_ip)

        floppy = windows_autoinst.winCreateFloppy(name=vm_name, pingback_ip=host_ip)
        base_image_cleanup.add(lambda: windows_autoinst.winDeleteFloppy(disk_location, vm_name))

        mac_address = 'FA:FA:FA:FA:FA:FA'
        '''template_name, vm_name, vm_location, iso, iso_drivers, mac_address, id, disk_location,
                 disk_name, floppy'''
        vm = vm_backend.vmCreate(template_name='WindowsTemplate', vm_location=disk_location, vm_name=vm_name, iso=iso, iso_drivers=iso_drivers,
                            mac_address=mac_address, vm_id=vm_id, disk_location=disk_location, disk_name=vm_name,
                         floppy=floppy)

        if not keep_vm:
            base_image_cleanup.add(lambda: vm.vmDelete())

        vm.vmPowerOn()
        if not keep_vm:
            base_image_cleanup.add(lambda: vm.vmPowerOff())
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

        print('buildImage:installing packages')
        for package in packages:
            result = winrs.remoteInstallPackage(package)
            if "Reboot" not in result:
                continue

            print('buildImage:reboot required, rebooting....')
            winrs.remoteReboot()

        input("buildImage:Press Enter to continue...")

        return True

