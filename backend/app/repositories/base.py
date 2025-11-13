class BaseRepo:
    def __init__(self, db):
        self.db = db

    def filter_context(self, *keys, context: dict):
        if [k for k in keys if k not in context]:
            raise ValueError('Missing context keys!')
        return {k: context[k] for k in keys if k in context}    
    
    def obj_by_obj_id(self, model, obj_id):
        return model.query.get(obj_id)

    def obj_by_obj_name(self, model, obj_name, field):
        return model.query.filter(obj_name == field).first()