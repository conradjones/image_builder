import json


def ssh_shell(*, address):
    from shell import ssh
    return ssh.SSH(conn_string=address)


shell_types = {
    "ssh": ssh_shell
}


def step_shell(step_data, steps_state):
    if not 'type' in step_data:
        raise Exception('Missing shell type')

    shell_type = step_data['type']

    if not shell_type in shell_types:
        raise Exception('Unknown shell type:%s' % shell_type)

    steps_state[step_data['name']] = shell_types[shell_type](**step_data['parameters'])




step_parser = {
    "shell": step_shell
}

with open("../scratch/configs/build-ci-template.json") as file:
    data = json.loads(file.read())


class step_state:
    def __init__(self):
        self.shells = {}


state = step_state()

for step in data['steps']:

    if not 'step' in step:
        raise Exception('Missing step type')

    step_type = step['step']
    if not step_type in step_parser:
        raise Exception('Unknown step type:%s' % step_type)

    if not step_parser[step_type](step, state):
        raise Exception('Failed to execute step:%s' % json.dumps(step))
