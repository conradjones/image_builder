
def step_poweron_vm(step_data, steps_state):
    if not 'hypervisor' in step_data:
        raise Exception('Missing hypervisor type')

    diskvisor_type = step_data['type']

    if not diskvisor_type in diskvisor_types:
        raise Exception('Unknown diskvisor type:%s' % diskvisor_type)

    steps_state[step_data['name']] = diskvisor_types[diskvisor_type](steps_state, **step_data['parameters'])

