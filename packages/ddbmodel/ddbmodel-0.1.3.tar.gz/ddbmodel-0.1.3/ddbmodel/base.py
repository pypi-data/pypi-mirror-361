from logging import info, debug

from botocore.errorfactory import ClientError
from .config.ddbconfig import dbclient

class FieldBase:
    def __init__(self, should_update: bool, default_value):
        self.should_update = should_update
        self.default_value = default_value
        self.private_name = None

    def __set_name__(self, owner, name):
        raise NotImplementedError

    def deep_copy(self, owner):
        raise NotImplementedError

    def validate(self, value):
        raise NotImplementedError

    @classmethod
    def ddb_type(cls):
        raise NotImplementedError

    @classmethod
    def python_type(cls):
        raise NotImplementedError

    def value(self, record):
        raise NotImplementedError

    def dynamically_generated(self):
        raise NotImplementedError

    def generate(self):
        raise NotImplementedError


class KeyBase:
    def field_name(self):
        return NotImplementedError

    def ddb_constant_value(self):
        raise AttributeError(f"{self.field_name()} must be a constant key not {self.__class__.__name__}.")

    def ddb_value(self, parent):
        raise NotImplementedError


class RecordBase:
    class InvalidRecordClass(Exception):
        pass

    def __init__(self, **kwargs):
        debug(f"RecordBase.__init__({kwargs})")

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __setattr__(self, variable, value):
        if variable.startswith("_"):
            super().__setattr__(variable, value)
            return

        field = self.__class__.__dict__.get(variable)

        if field is not None and isinstance(field, FieldBase):
            debug(f'Record.__setattr__({variable}, {value}): field={field}')

            if value is None:
                if field.default_value is None:
                    if field.dynamically_generated():
                        new_value = field.generate()
                        setattr(self, field.private_name, new_value)
                        return

                    raise ValueError(f"{variable} not in ddb and now default or generator")

                setattr(self, field.private_name, field.default_value)
                return

            setattr(self, field.private_name, field.validate(field.python_type()(value)))
            return

        super().__setattr__(variable, value)

    def __getattribute__(self, item):
        if item.startswith("_"):
            return super().__getattribute__(item)

        value = self.__dict__.get(item)  # values are in the class instance
        field = self.__class__.__dict__.get(item)  # field descriptions are in the class

        if field is not None and isinstance(field, FieldBase):
            debug(f'Record.__getattribute__({item}): value={value}, field={field}')
            return field.value(self)

        return super().__getattribute__(item)

    def __set_name__(self, owner, name):
        debug(f"Field.__setname__({name},{owner})")
        self.name = name
        self.private_name = f"_{name}"
        self.owner = owner

    def __repr__(self):
        fields = ",".join([
            f"{field_name}={field.value(self)}"
            for field_name, field in self.record_fields().items()
        ])
        return f"{self.__class__.__name__}({fields})"


    def fields(self):
        #
        # This function returns the fields with a field definition _and_ were
        # loaded by a constructor, manually assigned into the class, or loaded
        # when fetching from ddb.
        #
        # The design decision for this function is to accept additional fields
        # into the class, but only presents those fields that can be validated
        # by a definition. This allows for additional fields to be added to
        # the class without breaking the class definition possibly making it
        # easier to support migrations. This may not work out and better
        # (or only) served by definitions with non-required/optional/default
        # values.
        #
        # The sloppiness enables constructors with just key values
        # used to get data like:
        #
        # ContactRecord(login='testlogin').fetch_item()
        #

        return {
            field_name[1:]: value  # remove the _
            for field_name, value in self.__dict__.items()
            if field_name.startswith("_") and field_name[1:] in self.record_fields()
        }


    def record_fields(self):
        return self.__class__._record_definitions_cache  # cached when subclass is created


    @classmethod
    def table_name(cls, table_override=None):
        if table_override is not None:
            return table_override

        return cls.Meta.table_name


    @classmethod
    def primary_key(cls):
        return cls.Meta.pk


    def sort_key(self):
        return self.__class__.Meta.sk


    def ddb_fields(self, update_only=False):
        debug(f"Record.ddb_fields()")

        return {
            field_name: {
                field.ddb_type(): str(field.value(self))
            }
            for field_name, field in self.record_fields().items()
            if field.should_update or not update_only
        }

    def ddb_get_item_command(self, view=None, table_override=None):
        raise NotImplementedError

    def get_item(self, view=None, table_override=None):
        debug(f"{self.__class__.__name__}.get({table_override})")
        ddb_get = self.ddb_get_item_command(view=view, table_override=table_override)

        try:
            response = dbclient.get_item(**ddb_get)

            if 'Item' not in response:
                return None

            for field_name, field in self.record_fields().items():
                field_value = response['Item'].get(field_name)
                if field_value is not None:
                    setattr(self, field_name, field_value.get(field.ddb_type()))
                else:
                    info(f"Record.get_item(): missing in response {field_name} is None")
                    setattr(self, field_name, None)

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                info(f"Record.get_item(): {self.table_name(table_override=table_override)} not found")
                return None
            else:
                raise

        return self

    def ddb_put_item_command(self, overwrite=False, table_override=None):
        raise NotImplementedError

    def put_item(self, overwrite=False, table_override=None):
        raise NotImplementedError

    def ddb_update_item_command(self, table_override=None):
        raise NotImplementedError

    def ddb_delete_item_command(self, table_override=None):
        raise NotImplementedError

    def delete_item(self, table_override=None):
        raise NotImplementedError
