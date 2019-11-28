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

    def __get_vm(self, name, throw=False):
        dom = self._conn.lookupByName(name)
        if not dom and throw:
            raise Exception('%s not found' % name)
        return dom

    def vmExists(self, name):
        dom = self.__get_vm(name)
        return dom is not None

    def vmIsOff(self, name):
        dom = self.__get_vm(name, throw=True)
        state, reason = dom.state()
        return state == libvirt.VIR_DOMAIN_SHUTDOWN or state == libvirt.VIR_DOMAIN_SHUTOFF

    def vmIsOn(self, name):
        dom = self.__get_vm(name, throw=True)
        state, reason = dom.state()
        return state == libvirt.VIR_DOMAIN_RUNNING

    def vmPowerOff(self, name):
        dom = self.__get_vm(name, throw=True)
        dom.destroy()
        util.wait_for(lambda: self.vmIsOff(name), "destroy %s" % name, "shutdown state")

    def vmPowerOn(self, name):
        if not self.vmIsOff(name):
            raise Exception("VM:%s is already started" % name)
        dom = self.__get_vm(name, throw=True)
        dom.create()
        util.wait_for(lambda: self.vmIsOn(name), "destroy %s" % name, "shutdown state")

    def vmGetDisk(self, name, dev):
        dom = self.__get_vm(name, throw=True)
        raw_xml = dom.XMLDesc(0)
        xml = lxml.html.fromstring(raw_xml)
        sources = xml.xpath(".//disk/target[@dev='%s']/../source" % dev)
        for source in sources:
            return source.attrib['file']

        raise Exception('%s has no disk device:%s' % (name, dev))

    def vmGetTemplate(self, name):
        script_dir = os.path.dirname(__file__)
        rel_path = "libvirt_templates/%s.xml" % name
        file_path = os.path.join(script_dir, rel_path)
        file = open(file_path, "r")
        return file.read()

    def vmCreate(self, template_name, name, iso, iso_drivers, mac_address, id, disk_location, disk_name, floppy):
        template = self.vmGetTemplate(template_name)
        template = template.replace('${DOMAIN_NAME}', name)
        template = template.replace('${DOMAIN_UUID}', id)
        template = template.replace('${DISK_SYSTEM}', os.path.join(disk_location, disk_name) + '.qcow2')
        template = template.replace('${DISK_ISO}', iso)
        template = template.replace('${DISK_DRIVERS}', iso_drivers)
        template = template.replace('${MAC_ADDRESS}', mac_address)
        template = template.replace('${DISK_FLOPPY}', floppy)
        print(template)
        self._conn.defineXML(template)