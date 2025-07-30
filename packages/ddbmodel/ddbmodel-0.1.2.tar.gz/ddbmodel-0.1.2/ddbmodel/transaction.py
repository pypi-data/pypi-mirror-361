from logging import debug

from ddbmodel.base import FieldBase
from ddbmodel.record import RecordBase, Record, dbclient

class View:
    def __init__(self, pk, sk):
        self.pk = pk
        self.sk = sk

class TransactionRecord(RecordBase):
    def __init_subclass__(cls, **kwargs):
        debug(f"TransactionRecord.__init_subclass__({cls})")

        super().__init_subclass__(**kwargs)

        cls._views = {}

        try:
            meta_class = getattr(cls, 'Meta')
            getattr(meta_class, 'table_name')

            views = {
                name: view
                for name, view in meta_class.__dict__.items()
                if isinstance(view, View)
            }

            for name, view in views.items():
                new_record_class = cls._view_record(
                    name,
                    view.pk.deep_copy(cls),
                    view.sk.deep_copy(cls)
                )
                cls._views[name] = new_record_class

        except AttributeError:
            raise ValueError(f"{cls.__name__} must have a Meta class")

    def __repr__(self):
        fields = ",".join([
            f"{field_name}={field.value(self)}"
            for field_name, field in self.record_fields().items()
        ])
        return f"{self.__class__.__name__}({fields})"


    @classmethod
    def record_fields(cls):
        return {
            field_name: field
            for field_name, field in cls.__dict__.items()
            if isinstance(field, FieldBase)
        }

    @classmethod
    def _view_record(cls, name, pk, sk):
        new_record_class = type(
            name,
            (Record,),
            {
                'Meta': type('Meta', (), {
                    'pk': pk,
                    'sk': sk,
                    'table_name':cls.table_name()
                }),
                **cls.record_fields()
            }
        )

        meta_class = getattr(new_record_class, 'Meta')
        meta_class.pk = pk.deep_copy(new_record_class)
        meta_class.sk = sk.deep_copy(new_record_class)

        return new_record_class

    def __set_name__(self, owner, name):
        debug(f"Field.__setname__({name},{owner})")
        self.name = name
        self.private_name = f"_{name}"
        self.owner = owner

    def view(self, view_name):
        return self._views[view_name](**self.fields())

    @classmethod
    def views(cls):
        return cls._views

    def ddb_get_item_command(self, view=None, table_override=None):
        if view is None:
            view = self.Meta.default_view

        if view not in self._views:
            raise ValueError(f"{self.__class__.__name__} does not have a view named {view}")

        view_class = self._views[view]
        return view_class(**self.fields()).ddb_get_item_command(table_override=table_override)

    def ddb_put_item_command(self, overwrite=False, table_override=None):
        debug(f"TransactionRecord.ddb_put_item_command({overwrite}, {table_override})")
        put_commands = [
            {
                'Put': view_class(**self.fields()).ddb_put_item_command(
                    overwrite=overwrite,
                    table_override=table_override
                )
            }
            for view_name, view_class in self.views().items()
        ]

        return {
            'TransactItems': put_commands
        }

    def put_item(self, overwrite=False, table_override=None):
        debug(f"TransactionRecord.put_item({overwrite}, {table_override})")
        ddb_put = self.ddb_put_item_command(overwrite=overwrite, table_override=table_override)
        return dbclient.transact_write_items(**ddb_put) # todo: jjb decide on return and add error handling

    def ddb_update_item_command(self, table_override=None):
        update_commands = [
            {
                'Update': view_class(**self.fields()).ddb_update_item_command(
                    table_override=table_override,
                    transaction=True
                )
            }
            for view_name, view_class in self.views().items()
        ]

        return {
            'TransactItems': update_commands
        }

    def update_item(self, table_override=None):
        debug(f"TransactionRecord.update_item({table_override})")
        ddb_update = self.ddb_update_item_command(table_override=table_override)
        return dbclient.transact_write_items(**ddb_update) # todo: jjb decide on return and add error handling

    def ddb_delete_item_command(self, table_override=None):
        delete_commands = [
            {
                'Delete': view_class(**self.fields()).ddb_delete_item_command(
                    table_override=table_override,
                    transaction=True
                )
            }
            for view_name, view_class in self.views().items()
        ]

        return {
            'TransactItems': delete_commands
        }

    def delete_item(self, table_override=None):
        debug(f"Record.delete({table_override})")
        ddb_delete = self.ddb_delete_item_command(table_override=table_override)
        return dbclient.transact_write_items(**ddb_delete)  # todo: jjb decide on return and add error handling

    @classmethod
    def ddb_get_item_all_command(cls, view_name=None, table_override=None):
        if view_name is None:
            view_name = cls.Meta.default_view

        view = cls.views()[view_name](
            **cls.record_fields()
        )

        return view.ddb_get_item_all_command(table_override=table_override)

    @classmethod
    def ddb_get_item_all(cls, view_name=None, table_override=None):
        debug(f"TransactionRecord.ddb_get_all({view_name}, {table_override})")

        if view_name is None:
            view_name = cls.Meta.default_view

        view = cls.views()[view_name]()

        items = view.ddb_get_item_all(table_override=table_override)

        debug(f"TransactionRecord.ddb_get_all(): {items}")

        return [
            cls(**{
                field_name: field.value(item)
                for field_name, field in cls.record_fields().items()
            })
            for item in items
        ]

    def ddb_get_item_all_sk_command(self, view_name=None, table_override=None):
        if view_name is None:
            view_name = self.__class__.Meta.default_view

        view = self.views()[view_name](
            **self.__class__.record_fields()
        )

        return view.ddb_get_item_all_command(table_override=table_override)

    def ddb_get_item_all_sk(self, view_name=None, table_override=None):
        debug(f"TransactionRecord.ddb_get_all_sk({view_name}, {table_override})")
        if view_name is None:
            view_name = self.__class__.Meta.default_view

        view = self.views()[view_name](
            **self.fields()
        )

        items = view.ddb_get_item_all_sk(table_override=table_override)

        debug(f"TransactionRecord.ddb_get_all_sk(): {items}")

        return [
            self.__class__(**{
                field_name: field.value(item)
                for field_name, field in self.__class__.record_fields().items()
            })
            for item in items
        ]
