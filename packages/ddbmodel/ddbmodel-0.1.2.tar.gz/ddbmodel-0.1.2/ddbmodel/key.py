from ddbmodel.base import KeyBase
from ddbmodel.record import RecordBase


class FieldKey(KeyBase):
    def __init__(self, field_name):
        self._field_name = field_name

    def deep_copy(self, owner):
        field_key = FieldKey(self._field_name)
        field_key._owner = owner
        return field_key

    def __repr__(self):
        return f"FieldKey({self._field_name})"

    def field_name(self):
        return self._field_name

    def ddb_value(self, parent):
        if not isinstance(parent, RecordBase):
            raise ValueError(f'"{parent}" is not a Record')

        return str(getattr(parent, self.field_name()))

class ConstantKey(KeyBase):
    def __init__(self, value):
        self.value = value

    def deep_copy(self, owner):
        const_key = ConstantKey(self.value)
        const_key._owner = owner
        return const_key

    def __repr__(self):
        return f"ConstantKey({self.value})"

    def ddb_constant_value(self):
        return self.value

    def ddb_value(self, _):
        return str(self.value)


class Key(KeyBase):
    def __init__(self):
        self.keys = []

    def __repr__(self):
        keys = ",".join([str(key) for key in self.keys])
        return f"Key({keys})"

    def deep_copy(self, owner):
        new_key = Key()
        new_key.keys = [key.deep_copy(owner) for key in self.keys]
        new_key._owner = owner
        return new_key

    def constant(self, value):
        self.keys.append(ConstantKey(value))
        return self

    def field(self, field_name):
        self.keys.append(FieldKey(field_name))
        return self

    def ddb_const_value(self):
        return "#".join([
            key.ddb_constant_value()
            for key in self.keys
            if isinstance(key, ConstantKey) # jjb todo: consider better error handling when not constant
        ])

    def ddb_value(self, parent):
        if not isinstance(parent, RecordBase):
            raise ValueError(f'"{parent}" is "{type(parent)}" not a Record')

        return "#".join([key.ddb_value(parent) for key in self.keys])