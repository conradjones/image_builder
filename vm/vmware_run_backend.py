import os
from util import util

# todo add platform specific checks and look instead of presume location

_vmrun = "/Applications/VMware Fusion.app/Contents/Library/vmrun"
_vmrun_type = "fusion"



def _vm_run_folder(vm_location, vm_name):
    return os.path.join(vm_location, vm_name)

def _vm_vmx_file(vm_location, vm_name):
    return os.path.join(vm_location, vm_name, '%s.vmx' % vm_name)

class VMwareVMRunVM:
    def __init__(self, shell, vm_location, vm_name):
        self._shell = shell
        self._vm_location = vm_location
        self._vm_name = vm_name

    def _vmx_file(self):
        return _vm_vmx_file(self._vm_location, self._vm_name)

    def vmIsOff(self):
        return not self.vmIsOn()

    def vmIsOn(self):
        result, stdout, stderr = self._shell.execute_process(
            [_vmrun, '-T', _vmrun_type, 'list'])

        return self._vmx_file() in stdout

    def vmPowerOff(self):
        print("vmPowerOff:%s", self._vm_name)

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


def vmGetTemplate(vm_name):
    script_dir = os.path.dirname(__file__)
    rel_path = "vmx_templates/%s.vmx" % vm_name
    file_path = os.path.join(script_dir, rel_path)
    file = open(file_path, "r")
    return file.read()



class VMwareVMRunBackend:

    def __init__(self, shell):
        self._shell = shell

    def vmGet(self, vm_location, vm_name):
        if not self.vmExists(vm_location, vm_name):
            return None
        return VMwareVMRunVM(self._shell, vm_location, vm_name)

    def vmExists(self, vm_location, vm_name):
        vmx_file_path = os.path.join(vm_location, vm_name, '%s.vmx' % vm_name)
        return os.path.isfile(vmx_file_path)

    def vmCreate(self, *, template_name, vm_location, vm_name, iso, iso_drivers, mac_address, id, disk_location,
                 disk_name, floppy):

        vm_run_folder = _vm_run_folder(vm_location, vm_name)
        self._shell.mkdir(vm_run_folder)

        print("vmCreate:%s" % vm_name)
        template = vmGetTemplate(template_name)
        template = template.replace('${VM_NAME}', vm_name)
        template = template.replace('${DOMAIN_UUID}', id)
        template = template.replace('${DISK_SYSTEM}', os.path.join(disk_location, disk_name) + '.vmdk')
        template = template.replace('${DISK_ISO}', iso)
        template = template.replace('${DISK_DRIVERS}', iso_drivers)
        template = template.replace('${MAC_ADDRESS}', mac_address)
        template = template.replace('${DISK_FLOPPY}', floppy)
        vmx_file_path = os.path.join(vm_run_folder, '%s.vmx' % vm_name)
        with open(vmx_file_path, "w+") as file:
            file.write(template)

        return VMwareVMRunVM(self._shell, vm_location, vm_name)


