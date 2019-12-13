from steps import step_utils


def libvirt_diskvisor(steps_state, step_data, *, location, shell, group=None, perms=None):
    from vm import libvirtdisk_backend
    shell = steps_state.get_item('shells', shell)
    return libvirtdisk_backend.LibVirtDiskBackEnd(shell=shell, location=location, group=group, perms=perms)


def vdiskmanager_diskvisor(steps_state, step_data, *, location):
    step_utils.check_step_values(step_data, ['shell'])
    from vm import vmware_vdiskmanager_backend
    shell = steps_state.get_item('shells', step_data['shell'])
    return vmware_vdiskmanager_backend.VMwareVDiskManagerBackend(shell=shell, location=location)


diskvisor_types = {
    "libvirt": libvirt_diskvisor,
    "vdiskmanager": vdiskmanager_diskvisor
}


def step_diskvisor(step_data, steps_state):
    step_utils.check_step_values(step_data, ['type'])

    steps_state.set_item('diskvisors',
                         step_data['name'],
                         step_utils.execute_map_step_type(diskvisor_types, step_data, steps_state))

    return True
