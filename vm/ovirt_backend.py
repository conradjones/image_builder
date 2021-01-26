import ovirtsdk4 as sdk
import ovirtsdk4.types

import lxml.etree
import lxml.html
import os
import random
import uuid
from util import util
from jinja2 import Template


class OVirtBackEnd:

    def __init__(self, conn_string):
        self._connection = sdk.Connection(
            url='https://ovirt-engine.localdomain/ovirt-engine/api',
            username='admin@ovirt-engine.localdomain',
            password='27081982Monkeys1_',
            ca_file='/Users/conrad/ovirt/pki-resource.cer',
        )

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


    def vmCreate(self, *, template_name, vm_location, vm_name, iso, iso_drivers, mac_address=None, vm_id=None, disk_system, floppy):
        vms_service = self._connection.system_service().vms_service()

        vms_service.add(
            ovirtsdk4.types.Vm( name='vm1', memory=512 * 1024 * 1024cluster = types.Cluster(
            name='Default',
        ),
                  template = types.Template(name='Blank',
                                            ),
                             os = types.OperatingSystem(boot=types.Boot(devices=[types.BootDevice.HD)]
        ), )

'''
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
'''