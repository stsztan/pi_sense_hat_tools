import configargparse


config_parameter_prefix = '--'
match = -1


def all_params_config(*args, **kwargs):
    p = configargparse.ArgParser()
    p.add(*args, **kwargs)
    arguments, unknown = p.parse_known_args()
    return arguments


def auto_param_config(*args, **kwargs):
    parsed_args = all_params_config(*args, **kwargs)
    params = [*filter(lambda a: a.startswith(config_parameter_prefix), args)]
    param = params[match].lstrip(config_parameter_prefix)
    return getattr(parsed_args, param)
