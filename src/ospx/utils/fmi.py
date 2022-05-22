

def get_fmi_data_type(arg):
    """Returns the fmi data type of the passed in argument (best guess)
    """
    if isinstance(arg, int):
        return 'Integer'
    elif isinstance(arg, float):
        return 'Real'
    elif isinstance(arg, bool):
        return 'Bool'
    else:
        return 'String'
