keys = {}

def create_key(key_name, key_value):
    keys[key_name] = key_value
    return f"Key '{key_name}' created with value '{key_value}'"

def get_key(key_name):
    if key_name in keys:
        return keys[key_name]
    else:
        return f"Key '{key_name}' not found"

def update_key(key_name, new_key_value):
    if key_name in keys:
        keys[key_name] = new_key_value
        return f"Key '{key_name}' updated with new value '{new_key_value}'"
    else:
        return f"Key '{key_name}' not found"

def delete_key(key_name):
    if key_name in keys:
        del keys[key_name]
        return f"Key '{key_name}' deleted"
    else:
        return f"Key '{key_name}' not found"