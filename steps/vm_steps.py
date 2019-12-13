from steps import step_utils


def create_vm(steps_state, step_data, *, template_name, vm_location, vm_name, iso, iso_drivers, mac_address=None,
              vm_id=None, disk_system, floppy=None):
    step_utils.check_step_values(step_data, ['hypervisor', 'name'])
    hypervisor = steps_state.get_item('hypervisors', step_data['hypervisor'])

    disk_system = steps_state.parse_single_item(['disks'], disk_system)

    if floppy is not None:
        floppy = steps_state.parse_single_item(['floppy_images'], floppy)

    vm = hypervisor.vmCreate(template_name=template_name, vm_location=vm_location, vm_name=vm_name, iso=iso,
                             iso_drivers=iso_drivers, mac_address=mac_address, vm_id=vm_id, disk_system=disk_system,
                             floppy=floppy)
    steps_state.set_item('vms', step_data['name'], vm)


def power_on_vm(steps_state, step_data):
    step_utils.check_step_values(step_data, ['name'])
    vm = steps_state.get_vm(step_data['name'])
    vm.vmPowerOn()


vm_types = {
    "create": create_vm,
    "power_on": power_on_vm
}


def step_vm(step_data, steps_state):
    step_utils.check_step_values(step_data, ['type'])

    step_utils.execute_map_step_type(vm_types, step_data, steps_state)

    return True
