import lxml.etree
import lxml.html
import uuid
from shell import local
import getpass
from windows import windows_autoinst
from workflows.windows import packages
from util import util
from pingback import pingback
import random


def get_diskvisor(diskvisor_type, *, shell):
    if diskvisor_type == "VDiskManager":
        from vm import vmware_vdiskmanager_backend
        return vmware_vdiskmanager_backend.VMwareVDiskManagerBackend(shell)


def parse_diskvisor_type(xml, *, shell):
    disk_s = xml.xpath(".//Disk")
    type_s = disk_s[0].xpath(".//Type")
    diskvisor_type = type_s[0].text

    location_s = disk_s[0].xpath(".//Location")
    location = location_s[0].text

    if diskvisor_type == "VDiskManager":
        from vm import vmware_vdiskmanager_backend
        return vmware_vdiskmanager_backend.VMwareVDiskManagerBackend(shell=shell, location=location)

    if diskvisor_type == "LibVirtDisk":
        from vm import libvirtdisk_backend

        groups_s = disk_s[0].xpath(".//Group")
        group = groups_s[0].text if len(groups_s) > 0 else None

        perm_s = disk_s[0].xpath(".//Perms")
        perm = perm_s[0].text if len(perm_s) > 0 else None

        return libvirtdisk_backend.LibVirtDiskBackEnd(shell=shell, location=location, group=group, perms=perm)

    raise Exception("Unknown diskvisor type:%s" % diskvisor_type)


def get_hypervisor(hypervisor_type, *, shell):
    if hypervisor_type == "Fusion":
        from vm import vmware_run_backend
        return vmware_run_backend.VMwareVMRunBackend(shell)

    raise Exception("Unknown hypervisor type:%s" % hypervisor_type)


def parse_hypervisor_type(xml, *, shell):
    hypervisor_s = xml.xpath(".//Hypervisor")
    if len(hypervisor_s) is 0:
        raise Exception("Requires Hypervisor node")

    type_s = hypervisor_s[0].xpath(".//Type")
    if len(hypervisor_s) is 0:
        raise Exception("Requires Hypervisor/Type node")

    if type_s[0].text == "Fusion":
        from vm import vmware_run_backend
        return vmware_run_backend.VMwareVMRunBackend(shell)

    if type_s[0].text == "LibVirt":
        uri_s = hypervisor_s[0].xpath(".//URI")
        if len(uri_s) is 0:
            raise Exception("LibVirt Requires Hypervisor/URI node")

        from vm import libvirt_backend
        return libvirt_backend.LibVirtBackEnd(uri_s[0].text)

    raise Exception("Unknown hypervisor type:%s" % type_s[0].text)


def get_shell(xml):
    shell_s = xml.xpath(".//Shell")
    if len(shell_s) == 0 or shell_s[0].text == 'Local':
        return local.LocalShell()

    if shell_s[0].text == 'SSH':
        shell_address_s = xml.xpath(".//ShellAddress")
        if len(shell_address_s) == 0:
            raise Exception("SSH shell requires ShellAddress")

        from shell import ssh

        return ssh.SSH(shell_address_s[0].text)

    raise Exception("Unknown shell type")


def parse_image_source(xml):
    image_source_s = xml.xpath(".//Image/Source")
    if len(image_source_s) is 0:
        raise Exception("No Image/Source")

    iso_drivers_s = xml.xpath(".//ISODrivers")
    if len(iso_drivers_s) > 0:
        iso_drivers = iso_drivers_s[0].text
    else:
        iso_drivers = None

    template_s = xml.xpath(".//Template")
    if len(template_s) > 0:
        template = template_s[0].text
    else:
        raise Exception("Requires Build/Image/Source/Template")

    iso_s = xml.xpath(".//ISO")
    if len(iso_s) > 0:
        return WindowsIsoSource(iso=iso_s[0].text, iso_drivers=iso_drivers, template=template)

    linked_clone_s = image_source_s[0].xpath(".//LinkedClone")
    if len(linked_clone_s) > 0:
        return DiskImageSource(parent_disk=linked_clone_s[0].text, template=template)

    raise Exception("Requires valid image source")


def parse_packages(xml):
    package_s = xml.xpath(".//Image/Packages/Package")
    packages = {}
    for package_node in package_s:
        packages[package_node.text] = package_node.attrib

    return packages


def parse_remote(xml, *, admin_user, admin_password):
    remote_s = xml.xpath(".//Image/Remote")
    if len(remote_s) > 0:
        remote = remote_s[0].text
    else:
        raise Exception("Requires Build/Image/Remote")

    if remote == 'WinRS':
        host = ""
        if 'Address' in remote_s[0].attrib:
            host = remote_s[0].attrib['Address']
        from remote import winrs
        return winrs.WinRsRemote(host=host, user=admin_user, auth=admin_password)

    raise Exception("Unknown remote type:%s" % remote)


def parse_dest(xml):
    dest_s = xml.xpath(".//Image/Dest")
    if len(dest_s) > 0:
        return dest_s[0].text
    else:
        return None


def parse_macaddress(xml):
    mac_address = xml.xpath(".//MacAddress")
    if len(mac_address) > 0:
        return mac_address[0].text
    else:
        return None


def parse_admin_user(xml):
    password_s = xml.xpath(".//Image/Administrator/Password")
    if len(password_s) is 0:
        raise Exception("Requires Image/Administrator/Password node")

    if password_s[0].text == '*':
        password = None
        while password is None:
            print("Enter password:")
            pass1 = getpass.getpass()

            print("Confirm password:")
            pass2 = getpass.getpass()

            if pass1 == pass2:
                password = pass1
            else:
                print("Passwords did not match")

        return password

    return password_s[0].text


class WindowsIsoSource:

    def __init__(self, *, iso, template, iso_drivers=None):
        self._iso = iso
        self._iso_drivers = iso_drivers
        self._template = template

    def create(self, *, shell, cleanup, hypervisor, diskvisor, admin_password, vm_name, mac_address, vm_id, size_gb,
               keep_vm):
        unattend = windows_autoinst.WindowsAutoInst(shell=shell, location=diskvisor.location,
                                                    admin_password=admin_password, group=diskvisor.group,
                                                    perms=diskvisor.perms)

        floppy = unattend.winCreateFloppy(name=vm_name, pingback_ip=util.guess_local_ip())
        if not keep_vm:
            cleanup.add(lambda: unattend.winDeleteFloppy(name=vm_name))

        disk_system = diskvisor.diskCreate(disk_name=vm_name, size_gb=40)
        if not keep_vm:
            cleanup.add(lambda: diskvisor.diskDelete(disk_name=disk_system))

        vm = hypervisor.vmCreate(template_name=self._template, vm_name=vm_name, iso=self._iso,
                                 vm_location=diskvisor.location, iso_drivers=self._iso_drivers, mac_address=mac_address,
                                 id=vm_id, disk_system=disk_system, floppy=floppy)

        return vm


class DiskImageSource:

    def __init__(self, *, template, parent_disk):
        self._template = template
        self._parent_disk = parent_disk

    def create(self, *, shell, cleanup, hypervisor, diskvisor, admin_password, vm_name, mac_address, vm_id, size_gb,
               keep_vm):
        disk_system = diskvisor.diskCreate(disk_name=vm_name, size_gb=40, parent_disk=self._parent_disk)
        if not keep_vm:
            cleanup.add(lambda: diskvisor.diskDelete(disk_name=disk_system))

        vm = hypervisor.vmCreate(template_name=self._template, vm_name=vm_name, iso=None,
                                 vm_location=diskvisor.location, iso_drivers=None, mac_address=mac_address,
                                 id=vm_id, disk_system=disk_system, floppy=None)

        return vm


def parse_config(file_name, *, keep_vm=True):
    # print(raw_xml)
    with util.cleanup() as image_cleanup:
        xml = lxml.etree.parse(file_name)
        shell = get_shell(xml)

        hypervisor = parse_hypervisor_type(xml, shell=shell)

        diskvisor = parse_diskvisor_type(xml, shell=shell)

        image_source = parse_image_source(xml)
        package_list = parse_packages(xml)

        dest = parse_dest(xml)

        admin_password = parse_admin_user(xml)

        remote = parse_remote(xml, admin_user="Administrator", admin_password=admin_password)

        vm_id = str(uuid.uuid1())
        vm_name = 'image_build-' + vm_id

        mac_address = parse_macaddress(xml)
        if mac_address is None:
            mac_address = "52:54:00:%02x:%02x:%02x" % (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )

        vm = image_source.create(shell=shell, cleanup=image_cleanup, hypervisor=hypervisor, diskvisor=diskvisor,
                                 admin_password=admin_password, vm_name=vm_name, mac_address=mac_address, vm_id=vm_id,
                                 size_gb=40, keep_vm=keep_vm)

        if not keep_vm:
            image_cleanup.add(lambda: vm.vmDelete())

        vm.vmPowerOn()
        if not keep_vm:
            _power_off = image_cleanup.add(lambda: vm.vmPowerOff())

        if remote.host == "":
            print('buildImage:waiting for ping back')
            pingback.start_server()
            image_cleanup.add(lambda: pingback.stop_server())

            if not util.wait_for(lambda: pingback.get_stored_ip(), time_out=600, operation_name="Waiting",
                                 wait_name="Pingback"):
                print('buildImage:failed to get ping back')
                return False

            ip = pingback.get_stored_ip()

            print("buildImage:ping back from %s" % ip)

            remote.set_host(host=ip)

        packages.install_packages(remote=remote, packages=package_list)

        if dest is not None:
            vm.vmPowerOff()
            image_cleanup.remove(_power_off)
            diskvisor.diskCopy(vm.system_disk, dest)

        if not keep_vm:
            vm.vmPowerOff()
            image_cleanup.remove(_power_off)
