from steps import step_utils


def libvirt_hypervisor(*, address):
    from vm import libvirt_backend
    return libvirt_backend.LibVirtBackEnd(conn_string=address)


hypervisor_types = {
    "libvirt": libvirt_hypervisor
}


def step_hypervisor(step_data, steps_state):
    step_utils.check_step_values(step_data, ['type'])

    steps_state[step_data['name']] = step_utils.execute_map_step_type(hypervisor_types, step_data, steps_state)
