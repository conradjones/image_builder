import libvirt
import lxml.etree
import lxml.html
import os
from util import util


class LibVirtBackEnd:

    def __init__(self, conn_string):
        self._conn = libvirt.open(conn_string)
        if self._conn is None:
            raise Exception('Failed to connect to :%s' % conn_string)

    def __get_vm(self, vm_name, throw=False):
        try:
            dom = self._conn.lookupByName(vm_name)
        except BaseException:
            dom = None
        if not dom and throw:
            raise Exception('%s not found' % vm_name)
        return dom

    def vmExists(self, vm_name):
        dom = self.__get_vm(vm_name)
        return dom is not None

    def vmIsOff(self, vm_name):
        dom = self.__get_vm(vm_name, throw=True)
        state, reason = dom.state()
        return state == libvirt.VIR_DOMAIN_SHUTDOWN or state == libvirt.VIR_DOMAIN_SHUTOFF

    def vmIsOn(self, vm_name):
        dom = self.__get_vm(vm_name, throw=True)
        state, reason = dom.state()
        return state == libvirt.VIR_DOMAIN_RUNNING

    def vmPowerOff(self, vm_name):
        print("vmPowerOff:%s" % vm_name)
        dom = self.__get_vm(vm_name, throw=True)
        dom.destroy()
        util.wait_for(lambda: self.vmIsOff(vm_name), operation_name="destroy %s" % vm_name, wait_name="shutdown state")

    def vmPowerOn(self, vm_name):
        print("vmPowerOn:%s" % vm_name)
        if not self.vmIsOff(vm_name):
            raise Exception("VM:%s is already started" % vm_name)
        dom = self.__get_vm(vm_name, throw=True)
        dom.create()
        util.wait_for(lambda: self.vmIsOn(vm_name), operation_name="destroy %s" % vm_name, wait_name="shutdown state")

    def vmGetDisk(self, vm_name, dev):
        dom = self.__get_vm(vm_name, throw=True)
        raw_xml = dom.XMLDesc(0)
        xml = lxml.html.fromstring(raw_xml)
        sources = xml.xpath(".//disk/target[@dev='%s']/../source" % dev)
        for source in sources:
            return source.attrib['file']

        raise Exception('%s has no disk device:%s' % (vm_name, dev))

    def vmGetTemplate(self, vm_name):
        script_dir = os.path.dirname(__file__)
        rel_path = "libvirt_templates/%s.xml" % vm_name
        file_path = os.path.join(script_dir, rel_path)
        file = open(file_path, "r")
        return file.read()

    def vmCreate(self, template_name, vm_name, iso, iso_drivers, mac_address, id, disk_location, disk_name, floppy):
        print("vmCreate:%s" % vm_name)
        template = self.vmGetTemplate(template_name)
        template = template.replace('${DOMAIN_NAME}', vm_name)
        template = template.replace('${DOMAIN_UUID}', id)
        template = template.replace('${DISK_SYSTEM}', os.path.join(disk_location, disk_name) + '.qcow2')
        template = template.replace('${DISK_ISO}', iso)
        template = template.replace('${DISK_DRIVERS}', iso_drivers)
        template = template.replace('${MAC_ADDRESS}', mac_address)
        template = template.replace('${DISK_FLOPPY}', floppy)
        self._conn.defineXML(template)

    def vmDelete(self, vm_name):
        print("vmDelete:%s" % vm_name)
        dom = self.__get_vm(vm_name, throw=True)
        dom.undefine()
