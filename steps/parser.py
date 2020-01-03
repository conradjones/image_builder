import json
import re
from steps import shell_steps, vm_steps, hypervisor_steps, diskvisor_steps, floppyimage_steps, disk_steps, \
    pingback_steps

step_parser = {
    "shell": shell_steps.step_shell,
    "vm": vm_steps.step_vm,
    "hypervisor": hypervisor_steps.step_hypervisor,
    "diskvisor": diskvisor_steps.step_diskvisor,
    "floppy_image": floppyimage_steps.step_floppyimage,
    "create_disk": disk_steps.step_create_disk,
    "pingback": pingback_steps.step_pingback
}

with open("scratch/configs/build-ci-template-fusion.json") as file:
    data = json.loads(file.read())


class step_state:

    def _init_store(self, name):
        self.stores[name] = {}

    def __init__(self):
        self.stores = {}
        for name in ['shells', 'diskvisors', 'hypervisors', 'disks', 'floppy_images', 'vms', 'pingback']:
            self._init_store(name)

    def get_item(self, store, name):
        if store not in self.stores:
            raise Exception('Unknown store type:%s' % store)

        return self.stores[store][name]

    def set_item(self, store, name, item):
        if store not in self.stores:
            raise Exception('Unknown store type:%s' % store)

        self.stores[store][name] = item

    def parse_single_item(self, valid, source_string):
        find_components = re.compile('\\${([A-Za-z0-9_\-]+):([A-Za-z0-9_\-]+)}')
        variables = find_components.findall(source_string)
        if len(variables) > 0:
            store, name = variables[0]
            if store not in valid:
                raise Exception("%s not valid in %s" % (store, source_string))
            return self.get_item(store, name)

        return source_string

    def parse_string(self, source):

        find_variable = re.compile('(\\${([A-Za-z0-9_\\-]+):([A-Za-z0-9_\\-]+)})')
        variables = find_variable.findall(source)

        for full, store, name in variables:
            print(store)
            print(name)

            if store not in self.stores:
                raise Exception('Unknown store type:%s' % store)

            if store not in self.stores:
                raise Exception('Unknown store type:%s' % store)


state = step_state()

for step in data['steps']:

    if 'step' not in step:
        raise Exception('Missing step type')

    step_type = step['step']
    if step_type not in step_parser:
        raise Exception('Unknown step type:%s' % step_type)

    if not step_parser[step_type](step, state):
        raise Exception('Failed to execute step:%s' % json.dumps(step))
