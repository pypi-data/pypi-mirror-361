
def dict_update(old:dict, new:dict):
    if not old:
        return new
    return {**old, **new}