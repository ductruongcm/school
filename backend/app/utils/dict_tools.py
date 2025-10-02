
def get_updated_fields(new_data: dict, current_data: dict):
    return {
        key: value
        for key, value in new_data.items()
            if key in current_data and value != current_data[key]
    }