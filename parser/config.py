import lxml.etree
import lxml.html
from shell import local
import getpass
from workflows.windows import baseimage

def get_hypervisor(hypervisor_type, *, shell):
    if hypervisor_type == "Fusion":
        from vm import vmware_run_backend
        return vmware_run_backend.VMwareVMRunBackend(shell)

    raise Exception("Unknown hypervisor type:%s" % hypervisor_type)


def get_diskvisor(diskvisor_type, *, shell):
    if diskvisor_type == "VDiskManager":
        from vm import vmware_vdiskmanager_backend
        return vmware_vdiskmanager_backend.VMwareVDiskManagerBackend(shell)

    raise Exception("Unknown diskvisor type:%s" % diskvisor_type)


def parse_diskvisor_type(xml):
    disk_s = xml.xpath(".//Disk")
    type_s = disk_s[0].xpath(".//Type")
    return type_s[0].text


def parse_hypervisor_type(xml):
    hypervisor_s = xml.xpath(".//Hypervisor")
    if len(hypervisor_s) is 0:
        raise Exception("Requires Hypervisor node")

    type_s = hypervisor_s[0].xpath(".//Type")
    if len(hypervisor_s) is 0:
        raise Exception("Requires Hypervisor/Type node")

    return type_s[0].text


def get_shell(xml):
    shell_s = xml.xpath(".//Shell")
    if len(shell_s) == 0 or shell_s[0].text == 'Local':
        return local.LocalShell()

    raise Exception("Unknown shell type")


def parse_image_source(xml):
    image_source_s = xml.xpath(".//Image/Source")
    if len(image_source_s) is 0:
        raise Exception("No Image/Source")

    iso_s = xml.xpath(".//ISO")
    if len(iso_s) > 0:
        return IsoSource(iso_s[0].text)

    raise Exception("Requires valid image source")


def parse_packages(xml):
    package_s = xml.xpath(".//Image/Packages/Package")
    packages = []
    for package_node in package_s:
        packages += package_node.text

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

class IsoSource:

    def __init__(self, iso):
        self._iso = iso


def parse_config(file_name):
    # print(raw_xml)
    xml = lxml.etree.parse(file_name)
    shell = get_shell(xml)

    hypervisor_type = parse_hypervisor_type(xml)
    hypervisor = get_hypervisor(hypervisor_type, shell=shell)

    diskvisor_type = parse_diskvisor_type(xml)
    diskvisor = get_diskvisor(diskvisor_type, shell=shell)

    image_source = parse_image_source(xml)
    package_list = parse_packages(xml)

    admin_password = parse_admin_user(xml)

    baseimage.build_windows_base_image(hypervisor, diskvisor_type, windows_autoinst, winrs_remote, disk_location,
                                              40, iso, iso_drivers, packages, keep_vm=False)