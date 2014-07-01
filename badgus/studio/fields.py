import ast
from django.db import models


try:
    import cPickle as pickle
except ImportError:
    import pickle


class PickledObject(str):
    """A subclass of string so it can be told whether a string is
       a pickled object or not (if the object is an instance of this class
       then it must [well, should] be a pickled one)."""
    pass


class PickledObjectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return 'TextField'

    def to_python(self, value):
        if isinstance(value, PickledObject):
            # If the value is a definite pickle; and an error is raised in de-pickling
            # it should be allowed to propogate.
            return pickle.loads(str(value))
        else:
            try:
                value = pickle.loads(str(value))
                if isinstance(value, basestring):
                    # Just to make sure we're not looking at a corrupted dict/list
                    try:
                        value = ast.literal_eval(value)
                    except SyntaxError:
                        if value == '':
                            pass
                return value
            except pickle.UnpicklingError as err:
                # If an error was raised, just return the plain value
                return value

    def get_prep_value(self, value):
        if isinstance(value, basestring):
            try:
                value = ast.literal_eval(value)
            except Exception:
                pass
        if value is not None and not isinstance(value, PickledObject):
            value = PickledObject(pickle.dumps(value))
        return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            value = self.get_prep_save(value)
            return super(PickledObjectField, self).get_prep_lookup(lookup_type, value)
        elif lookup_type == 'in':
            value = [self.get_prep_save(v) for v in value]
            return super(PickledObjectField, self).get_prep_lookup(lookup_type, value)
        else:
            raise TypeError('Lookup type %s is not supported.' % lookup_type)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^badgus\.studio\.fields\.PickledObjectField"])
except ImportError:
    pass
