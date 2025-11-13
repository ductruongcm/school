def get_updated_fields(new_data: dict, current_data: dict):
    return {
        key: value
        for key, value in new_data.items()
            if key in current_data and value != current_data[key]
    }

def remove_none_fields(data: dict):
    return {k: v for k, v in data.items() if v is not None}

def filter_fields(*args, context: dict):
    return {k: context[k] for k in args if k in context}

def filter_list(context: list):
    return [i for i in context if i is not None]
      
    
