from steps import step_utils
import os
from util import util


def windows_auto_install_floppyimage(steps_state, *, ping_back=True, administrator_password, shell, file, group=None,
                                     perms=None):
    from windows import windows_autoinst
    shell_obj = steps_state.get_shell(shell)

    unattend = windows_autoinst.WindowsAutoInst(shell=shell_obj, location=os.path.dirname(file),
                                                admin_password=administrator_password, group=group,
                                                perms=perms)

    return unattend.winCreateFloppy(name=os.path.basename(file), pingback_ip=util.guess_local_ip())


floppyimage_types = {
    "windows_auto_install": windows_auto_install_floppyimage
}


def step_floppyimage(step_data, steps_state):
    step_utils.check_step_values(step_data, ['type', 'name'])

    steps_state.disks[step_data['name']] = step_utils.execute_map_step_type(floppyimage_types, step_data,
                                                                                     steps_state)
    return True