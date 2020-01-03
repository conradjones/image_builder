from steps import step_utils
from pingback import pingback
from util import util


def start_server(steps_state, step_data):
    pb = pingback.PingBack()
    pb.start_server()
    steps_state.set_item('pingback', step_data['name'], pb)
    return True


def wait_for(steps_state, step_data):
    pb = steps_state.get_item('pingback', step_data['name'])

    if not util.wait_for(lambda: pb.get_stored_ip(), time_out=600, operation_name="Waiting",
                         wait_name="Pingback"):
        print('buildImage:failed to get ping back')
        return False

    steps_state.set_item('ip', step_data['name'], pb.get_stored_ip())
    pb.stop_server()

    return True


pingback_types = {
    "start_server": start_server,
    "wait_for": wait_for
}


def step_pingback(step_data, steps_state):
    step_utils.check_step_values(step_data, ['type', 'name'])

    return step_utils.execute_map_step_type(pingback_types, step_data,
                                            steps_state)
