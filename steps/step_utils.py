def check_step_values(step_data, required_values):
    for required_value in required_values:
        if required_value not in step_data:
            raise Exception('Missing %s' % required_value)


def check_step_parameters(step_data, required_parameters):
    for required_parameter in required_parameters:
        if required_parameter not in step_data['parameters']:
            raise Exception('Missing parameter %s' % required_parameter)


def execute_map_step_type(types, step_data, steps_state):
    check_step_values(step_data, ['type'])

    step_type = step_data['type']

    if step_type not in types:
        raise Exception('Unknown %s type:%s' % (step_data['step'], step_type))

    if 'parameters' in step_data:
        return types[step_type](steps_state, step_data, **step_data['parameters'])
    else:
        return types[step_type](steps_state, step_data)
