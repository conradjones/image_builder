from steps import step_utils
import os
from util import util


def windows_auto_install_floppyimage(steps_state, step_data, *, ping_back=True, administrator_password, file,
                                     group=None,
                                     perms=None):
    step_utils.check_step_values(step_data, ['shell'])

    from windows import windows_autoinst
    shell = steps_state.get_item('shells', step_data['shell'])

    unattend = windows_autoinst.WindowsAutoInst(shell=shell, location=os.path.dirname(file),
                                                admin_password=administrator_password, group=group,
                                                perms=perms)

    return unattend.winCreateFloppy(name=os.path.basename(file), pingback_ip=util.guess_local_ip())


floppyimage_types = {
    "windows_auto_install": windows_auto_install_floppyimage
}


def step_floppyimage(step_data, steps_state):
    step_utils.check_step_values(step_data, ['type', 'name'])

    steps_state.set_item('floppy_images',
                         step_data['name'],
                         step_utils.execute_map_step_type(floppyimage_types, step_data, steps_state))

    return True
