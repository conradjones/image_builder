import json
from steps import shell_steps, vm_steps, hypervisor_steps, diskvisor_steps, floppyimage_steps, disk_steps

step_parser = {
    "shell": shell_steps.step_shell,
    "create_vm": vm_steps.step_create_vm,
    "delete_vm": vm_steps.step_delete_vm,
    "power_on_vm": vm_steps.step_power_on_vm,
    "power_off_vm": vm_steps.step_power_off_vm,
    "hypervisor": hypervisor_steps.step_hypervisor,
    "diskvisor": diskvisor_steps.step_diskvisor,
    "floppy_image": floppyimage_steps.step_floppyimage,
    "create_disk": disk_steps.step_create_disk,
}

with open("scratch/configs/build-ci-template-fusion.json") as file:
    data = json.loads(file.read())


class step_state:
    def __init__(self):
        self.shells = {}
        self.diskvisors = {}
        self.hypervisors = {}
        self.disks = {}
        self.floppy_images = {}

    def get_hypervisor(self, name):
        if name not in self.hypervisors:
            raise Exception('Hypervisor: %s does not exist' % name)
        return self.hypervisors[name]

    def get_diskvisor(self, name):
        if name not in self.diskvisors:
            raise Exception('Diskvisor: %s does not exist' % name)
        return self.diskvisors[name]

    def get_shell(self, name):
        if name not in self.shells:
            raise Exception('Shell: %s does not exist' % name)
        return self.shells[name]


state = step_state()

for step in data['steps']:

    if 'step' not in step:
        raise Exception('Missing step type')

    step_type = step['step']
    if step_type not in step_parser:
        raise Exception('Unknown step type:%s' % step_type)

    if not step_parser[step_type](step, state):
        raise Exception('Failed to execute step:%s' % json.dumps(step))
