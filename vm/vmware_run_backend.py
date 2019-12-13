import os
import uuid
import random
from util import util
from jinja2 import Template

# todo add platform specific checks and look instead of presume location

_vmrun = "/Applications/VMware Fusion.app/Contents/Library/vmrun"
_vmrun_type = "fusion"


def _vm_run_folder(vm_location, vm_name):
    return os.path.join(vm_location, vm_name)


def _vm_vmx_file(vm_location, vm_name):
    return os.path.join(vm_location, vm_name, '%s.vmx' % vm_name)


class VMwareVMRunVM:
    def __init__(self, shell, vm_location, vm_name, disk_system):
        self._shell = shell
        self._vm_location = vm_location
        self._vm_name = vm_name
        self._disk_system = disk_system

    def _vmx_file(self):
        return _vm_vmx_file(self._vm_location, self._vm_name)

    def vmIsOff(self):
        return not self.vmIsOn()

    def vmIsOn(self):
        result, stdout, stderr = self._shell.execute_process(
            [_vmrun, '-T', _vmrun_type, 'list'])

        return self._vmx_file() in stdout

    def vmPowerOff(self):
        print("vmPowerOff:%s" % self._vm_name)

        self._shell.execute_process(
            [_vmrun, '-T', _vmrun_type, 'stop', self._vmx_file()])

        util.wait_for(lambda: self.vmIsOff(), operation_name="power off %s" % self._vm_name, wait_name="shutdown state")

    def vmPowerOn(self):
        print("vmPowerOn:%s" % self._vm_name)
        if not self.vmIsOff():
            raise Exception("VM:%s is already started" % self._vm_name)

        self._shell.execute_process(
            [_vmrun, '-T', _vmrun_type, 'start', self._vmx_file()])

        util.wait_for(lambda: self.vmIsOn(), operation_name="power on %s" % self._vm_name,
                      wait_name="powered on state")

    def vmDelete(self):
        print("vmDelete:%s" % self._vm_name)
        if not util.wait_for(lambda: not self.isLocked(), time_out=120, operation_name="VM Locked", wait_name="unlock"):
            raise Exception("Timed out waiting for vmware to release lock file")

        self._shell.rmdir(os.path.join(self._vm_location, self._vm_name), recurse=True)

        # print(self._vmx_file())
        # self._shell.execute_process(
        #    [_vmrun, '-T', _vmrun_type, 'deleteVM', self._vmx_file()])

    def isLocked(self):
        lck_file = os.path.join(self._vm_location, self._vm_name + '.vmx.lck')
        return os.path.isfile(lck_file)

    @property
    def system_disk(self):
        return self._disk_system


def vmGetTemplate(vm_name):
    script_dir = os.path.dirname(__file__)
    rel_path = "vmx_templates/%s.vmx" % vm_name
    file_path = os.path.join(script_dir, rel_path)
    file = open(file_path, "r")
    return file.read()


class VMwareVMRunBackend:

    def __init__(self, shell):
        self._shell = shell

    def vmGetTemplate(self, vm_name):
        script_dir = os.path.dirname(__file__)
        rel_path = "vmx_templates/%s.j2.vmx" % vm_name
        file_path = os.path.join(script_dir, rel_path)
        with open(file_path, "r") as file:
            return Template(file.read())

    def vmGet(self, vm_location, vm_name):
        if not self.vmExists(vm_location, vm_name):
            return None
        return VMwareVMRunVM(self._shell, vm_location, vm_name)

    def vmExists(self, vm_location, vm_name):
        vmx_file_path = os.path.join(vm_location, vm_name, '%s.vmx' % vm_name)
        return os.path.isfile(vmx_file_path)

    def vmCreate(self, *, template_name, vm_location, vm_name, iso, iso_drivers, mac_address, vm_id, disk_system,
                 floppy):

        vm_run_folder = _vm_run_folder(vm_location, vm_name)
        self._shell.mkdir(vm_run_folder)

        if vm_id is None:
            vm_id = str(uuid.uuid1())

        if mac_address is None:
            mac_address = "00:50:56:%02x:%02x:%02x" % (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )

        ### TODO jinja template this.
        template = self.vmGetTemplate(template_name)

        template = template.render(vmName=vm_name, vmId=vm_id, diskSystem=disk_system, installerIso=iso,
                                   driversIso=iso_drivers, macAddress=mac_address, diskFloppy=floppy)


        print("vmCreate:%s" % vm_name)

        vmx_file_path = os.path.join(vm_run_folder, '%s.vmx' % vm_name)
        with open(vmx_file_path, "w+") as file:
            file.write(template)

        return VMwareVMRunVM(self._shell, vm_location, vm_name, disk_system)
