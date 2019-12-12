from steps import step_utils


def ssh_shell(steps_state, *, address):
    from shell import ssh
    return ssh.SSH(conn_string=address)


def local_shell(steps_state):
    from shell import local
    return local.LocalShell()


shell_types = {
    "ssh": ssh_shell,
    "local": local_shell
}


def step_shell(step_data, steps_state):
    step_utils.check_step_values(step_data, ['type'])

    steps_state.shells[step_data['name']] = step_utils.execute_map_step_type(shell_types, step_data, steps_state)
    return True
