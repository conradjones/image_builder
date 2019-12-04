import libvirt
import lxml.etree
import lxml.html
import os
from util import util


class LibVirtVM:
    def __init__(self, dom):
        self._dom = dom

    def vmIsOff(self):
        state, reason = self._dom.state()
        return state == libvirt.VIR_DOMAIN_SHUTDOWN or state == libvirt.VIR_DOMAIN_SHUTOFF

    def vmIsOn(self):
        state, reason = self._dom.state()
        return state == libvirt.VIR_DOMAIN_RUNNING

    def vmPowerOff(self):
        print("vmPowerOff:%s" % self._dom.name())
        self._dom.destroy()
        util.wait_for(lambda: self.vmIsOff(), operation_name="destroy %s" % self._dom.name(), wait_name="shutdown state")

    def vmPowerOn(self):
        print("vmPowerOn:%s" % self._dom.name())
        if not self.vmIsOff():
            raise Exception("VM:%s is already started" % self._dom.name())
        self._dom.create()
        util.wait_for(lambda: self.vmIsOn(), operation_name="power on %s" % self._dom.name(), wait_name="powered on state")

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
        rel_path = "libvirt_templates/%s.xml" % vm_name
        file_path = os.path.join(script_dir, rel_path)
        file = open(file_path, "r")
        return file.read()

    def vmCreate(self, *, template_name, vm_location, vm_name, iso, iso_drivers, mac_address, id, disk_system,
                 floppy):
        print("vmCreate:%s" % vm_name)
        template = self.vmGetTemplate(template_name)
        template = template.replace('${DOMAIN_NAME}', vm_name)
        template = template.replace('${DOMAIN_UUID}', id)
        template = template.replace('${DISK_SYSTEM}', disk_system)
        template = template.replace('${DISK_ISO}', iso)
        template = template.replace('${DISK_DRIVERS}', iso_drivers)
        template = template.replace('${MAC_ADDRESS}', mac_address)
        template = template.replace('${DISK_FLOPPY}', floppy)
        self._conn.defineXML(template)
        return LibVirtVM(self.vmGet(vm_name, throw=True))


