from steps import step_utils


def step_create_vm(step_data, steps_state):
    step_utils.check_step_values(step_data, ['hypervisor', 'vm-name'])

    hypervisor = steps_state.get_hypervisor(step_data['hypervisor'])

    vm = hypervisor.vmGet(step_data['vm-name'], throw=True)
    vm.vmPowerOn()


def step_power_on_vm(step_data, steps_state):
    step_utils.check_step_values(step_data, ['hypervisor', 'vm-name'])

    hypervisor = steps_state.get_hypervisor(step_data['hypervisor'])

    vm = hypervisor.vmGet(step_data['vm-name'], throw=True)
    vm.vmPowerOn()


def step_power_off_vm(step_data, steps_state):
    step_utils.check_step_values(step_data, ['hypervisor', 'vm-name'])

    hypervisor = steps_state.get_hypervisor(step_data['hypervisor'])

    vm = hypervisor.vmGet(step_data['vm-name'], throw=True)
    vm.vmPowerOff()


def step_delete_vm(step_data, steps_state):
    step_utils.check_step_values(step_data, ['hypervisor', 'vm-name'])

    hypervisor = steps_state.get_hypervisor(step_data['hypervisor'])

    vm = hypervisor.vmGet(step_data['vm-name'], throw=True)
    vm.vmDelete()
