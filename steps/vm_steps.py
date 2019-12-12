import json


def libvirt_diskvisor(steps_state, *, location, shell, group=None, perms=None):
    from vm import libvirtdisk_backend
    shell_obj = steps_state.shells[shell]
    return libvirtdisk_backend.LibVirtDiskBackEnd(shell=shell_obj, location=location, group=group, perms=perms)


diskvisor_types = {
    "libvirt": libvirt_diskvisor
}


def step_diskvisor(step_data, steps_state):
    if not 'type' in step_data:
        raise Exception('Missing diskvisor type')

    diskvisor_type = step_data['type']

    if not diskvisor_type in diskvisor_types:
        raise Exception('Unknown diskvisor type:%s' % diskvisor_type)

    steps_state[step_data['name']] = diskvisor_types[diskvisor_type](steps_state, **step_data['parameters'])

