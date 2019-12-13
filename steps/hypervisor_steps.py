from steps import step_utils


def libvirt_hypervisor(steps_state, step_data):
    from vm import libvirt_backend
    return libvirt_backend.LibVirtBackEnd(conn_string=address)


def fusion_hypervisor(steps_state, step_data):
    step_utils.check_step_values(step_data, ['shell'])
    from vm import vmware_run_backend
    shell = steps_state.get_item('shells', step_data['shell'])
    return vmware_run_backend.VMwareVMRunBackend(shell=shell)


hypervisor_types = {
    "libvirt": libvirt_hypervisor,
    "fusion": fusion_hypervisor
}


def step_hypervisor(step_data, steps_state):
    step_utils.check_step_values(step_data, ['type'])

    steps_state.set_item('hypervisors',
                         step_data['name'],
                         step_utils.execute_map_step_type(hypervisor_types, step_data, steps_state))

    return True
