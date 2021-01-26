import libvirt
import lxml.etree
import lxml.html
import os
import random
import uuid
from util import util
from jinja2 import Template
import time

class LibVirtVM:
    def __init__(self, dom, disk_system):
        self._dom = dom
        self._disk_system = disk_system

    def vmIsOff(self):
        state, reason = self._dom.state()
        return state == libvirt.VIR_DOMAIN_SHUTDOWN or state == libvirt.VIR_DOMAIN_SHUTOFF

    def vmIsOn(self):
        state, reason = self._dom.state()
        return state == libvirt.VIR_DOMAIN_RUNNING

    def vmPowerOff(self):
        print("vmPowerOff:%s" % self._dom.name())
        self._dom.destroy()
        util.wait_for(lambda: self.vmIsOff(), operation_name="destroy %s" % self._dom.name(),
                      wait_name="shutdown state")

    def vmPowerOn(self):
        print("vmPowerOn:%s" % self._dom.name())
        if not self.vmIsOff():
            raise Exception("VM:%s is already started" % self._dom.name())
        self._dom.create()
        util.wait_for(lambda: self.vmIsOn(), operation_name="power on %s" % self._dom.name(),
                      wait_name="powered on state")
    def vmShutDown(self, timeout=80):

        elapsed_seconds = 0



        while not self._dom.state()[0] == libvirt.VIR_DOMAIN_SHUTOFF:
            # issuing ACPI shutdown a few times can sometimes convince windows guests
            # to take the request seriously instead of displaying "really shutdown?"
            # on the virtual machines console.
            try:
                self._dom.shutdownFlags(
                    libvirt.VIR_DOMAIN_SHUTDOWN_GUEST_AGENT | libvirt.VIR_DOMAIN_SHUTDOWN_ACPI_POWER_BTN)
            except libvirt.libvirtError as err:
                # we have a race condition between checking for VIR_DOMAIN_SHUTOFF
                # and issuing the shutdown request.
                # unfortunately, "libvirtError" is all we get in that case.
                time.sleep(1)
                if self._dom.state()[0] == libvirt.VIR_DOMAIN_SHUTOFF:
                    # if the domain is in SHUTOFF now, we assume all went well
                    pass
                else:
                    # if not, re-raise
                    raise
            time.sleep(1)
            elapsed_seconds += 1
            if elapsed_seconds == timeout:
                # graceful as in "send sigterm to qemu-kvm", this is still akin to yanking the virtual power cord
                self._dom.destroyFlags(libvirt.VIR_DOMAIN_DESTROY_GRACEFUL)
                print(' had to yank the virtual powercord')
        print('shutdown took {} seconds'.format(elapsed_seconds))



    def vmGetDisk(self, dev):
        raw_xml = self._dom.XMLDesc(0)
        xml = lxml.html.fromstring(raw_xml)
        sources = xml.xpath(".//disk/target[@dev='%s']/../source" % dev)
        for source in sources:
            return source.attrib['file']

        raise Exception('%s has no disk device:%s' % (self._dom.name(), dev))

    def vmDelete(self):
        print("vmDelete:%s" % self._dom.name())
        self._dom.undefine()

    @property
    def system_disk(self):
        return self._disk_system


class LibVirtBackEnd:

    def __init__(self, conn_string):
        self._conn = libvirt.open(conn_string)
        if self._conn is None:
            raise Exception('Failed to connect to :%s' % conn_string)

    def vmGet(self, vm_name, throw=False):
        try:
            dom = self._conn.lookupByName(vm_name)
        except BaseException:
            dom = None
        if not dom and throw:
            raise Exception('%s not found' % vm_name)
        return dom

    def vmExists(self, vm_name):
        dom = self.vmGet(vm_name)
        return dom is not None

    def vmGetTemplate(self, vm_name):
        script_dir = os.path.dirname(__file__)
        rel_path = "libvirt_templates/%s.j2.xml" % vm_name
        file_path = os.path.join(script_dir, rel_path)
        with open(file_path, "r") as file:
            return Template(file.read())

    def vmCreate(self, *, template_name, vm_location, vm_name, iso, iso_drivers, mac_address=None, vm_id=None,
                 disk_system,
                 floppy):
        print("vmCreate:%s" % vm_name)
        template = self.vmGetTemplate(template_name)

        if mac_address is None:
            mac_address = "52:54:00:%02x:%02x:%02x" % (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
        if vm_id is None:
            vm_id = str(uuid.uuid1())

        template = template.render(vmName=vm_name, vmId=vm_id, diskSystem=disk_system, installerIso=iso,
                                   driversIso=iso_drivers, macAddress=mac_address, diskFloppy=floppy)

        self._conn.defineXML(template)
        return LibVirtVM(self.vmGet(vm_name, throw=True), disk_system)
