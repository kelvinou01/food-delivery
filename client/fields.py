from rest_framework import fields


class ModelField(fields.Field):
    def __init__(self, model, **kwargs):
        self.model = model
        return super().__init__(**kwargs)
    
    def to_representation(self, value):
        return value.id
    
    def to_internal_value(self, data):
        return self.model._default_manager.get(id=data)
