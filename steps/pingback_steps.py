from steps import step_utils


def start_server(steps_state, step_data):

    i = 0


def wait_for(steps_state, step_data):

     i = 0


pingback_types = {
    "start_server": start_server,
    "wait_for": wait_for
}


def step_pingback(step_data, steps_state):
    step_utils.check_step_values(step_data, ['type'])

    steps_state.hypervisors[step_data['name']] = step_utils.execute_map_step_type(pingback_types, step_data,
                                                                                  steps_state)

    return True
