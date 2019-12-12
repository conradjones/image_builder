from steps import step_utils


def step_create_disk(step_data, steps_state):
    step_utils.check_step_values(step_data, ['diskvisor', 'name'])
    step_utils.check_step_parameters(step_data, ['disk-name', 'size-gb'])

    diskvisor = steps_state.get_diskvisor(step_data['diskvisor'])

    disk_system = diskvisor.diskCreate(disk_name=step_data['parameters']['disk-name'],
                                       size_gb=step_data['parameters']['size-gb'])

    steps_state.disks[step_data['name']] = disk_system
    return True


def step_delete_disk(step_data, steps_state):
    step_utils.check_step_values(step_data, ['diskvisor', 'name'])

    diskvisor = steps_state.get_diskvisor(step_data['diskvisor'])

    vm = diskvisor.vmGet(step_data['vm-name'], throw=True)
    vm.vmPowerOn()
