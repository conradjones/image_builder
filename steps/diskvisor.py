import json


def libvirt_hypervisor(*, address):
    from vm import libvirt_backend
    return libvirt_backend.LibVirtBackEnd(conn_string=address)


hypervisor_types = {
    "libvirt": libvirt_hypervisor
}


def step_hypervisor(step_data, steps_state):
    if not 'type' in step_data:
        raise Exception('Missing hypervisor type')

    hypervisor_type = step_data['type']

    if not hypervisor_type in hypervisor_types:
        raise Exception('Unknown hypervisor type:%s' % hypervisor_type)

    steps_state[step_data['name']] = hypervisor_types[hypervisor_type](**step_data['parameters'])

